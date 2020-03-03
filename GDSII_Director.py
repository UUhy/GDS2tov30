#!/usr/bin/env ipython

from GDSII_Library import GDSII_Library
import numpy as np

class GDSII_Director(object):
    '''
    GDSII_Director class : subclass of object
    
    GDSII Stream file format release 6.0
    Director
    
    The director is a class designed to quickly generate a layout using the
    GDSII_Library class.  Consequently, this class does not support the entire
    capabilities of the GDSII stream format.
    
    The GDSII_Director class supports the following functions:
       addCell              =   Set the library name and units
       addArray             =   Adds a structure to the library
       addCellRef           =   Adds a boundary to a structure
       drawCross            =   Returns the vertices of a cross
       drawSquare           =   Returns the vertices of a square
       drawSquareInverse    =   Returns the vertices of an inverse square
       drawCircle           =   Returns the vertices of a circle
       drawCircleInverse    =   Returns the vertices of an inverse circle
       writeFile            =   Write to a file
           
    Long Chang, UH, September 2013
    '''
    
    def __init__(self):
        self.g = GDSII_Library()

    def addCell(self, cellName, polygon, datatype = 0, suffix = '_d', layer = 0):
        '''
        addCell(cellName, polygon, datatype = 0, suffix = '_d', layer = 0)
        
        Adds a cell with a boundary
        
        Parameters
        ----------
        cellName : string
            Name of cell
        polygon : numpy.ndarray or list of numpy.ndarray
            The vertices of a polygon or set of polygons
            The vertices must have the form:
                np.array([x0, y0, x1, y1, ... xn, yn, x0, y0])              
        datatype : integer or list of integer
            The shot rank value for the cell
            A list of N datatype value will generate N cells with similar names       
        suffix : string
            A suffix that is appended to the cell name
            The shot rank value is appended to the cell name + suffix
            This is done only if datatype is a list
        layer : integer
            Specify the layer
            
        Returns
        -------
        sList : list of strings
            A list of cells names created by this function
        '''
        if type(datatype) is int:
            self.g.addStructure(cellName)
            self.g.addBoundary(cellName, polygon, layer, datatype)
            sList = cellName
        else:
            if not type(datatype) is list:
                raise ValueError('GDSII_Director.addCell : The datatype parameter must be an integer or a list of integer')
            sList = []
            for i in datatype:
                tmp = cellName + suffix + str(i)
                self.g.addStructure(tmp)
                if type(polygon) is list:
                    for j in polygon:
                        self.g.addBoundary(tmp, j, layer, i)
                else:
                    if type(polygon) is np.ndarray:
                        self.g.addBoundary(tmp, polygon, layer, i)
                    else:
                        raise ValueError('GDSII_Director.addCell : The polygon parameter must be a numpy.ndarray or a list of numpy.ndarray')
                sList.append(tmp)
        return sList
    
    def addArray(self, cellName, pitchX, pitchY, nX, nY):
        '''
        addArray(cellName, pitchX, pitchY, nX, nY)
        
        Creates a cell array from a cell
        
        Parameters
        ----------
        cellName : string or list of strings
            Name of cell or cells
        pitchX : integer
            Array spacing along X        
        pitchY : integer
            Array spacing along Y
        nX : integer
            Number of repeats along X        
        nY : integer
            Number of repeats along Y
            
        Returns
        -------
        sList : list of strings
            A list of cells names created by this function
        '''
        if type(cellName) is str:
            tmp = 'A_' + cellName[0]
            self.g.addStructure(tmp)
            self.g.addARef(tmp, cellName[0], [0,0], pitchX, pitchY, nX, nY)
            sList = [tmp]
        else:
            if type(cellName) is list:
                sList = []
                for i in cellName:
                    tmp = 'A_' + i
                    self.g.addStructure(tmp)
                    self.g.addARef(tmp, i, [0,0], pitchX, pitchY, nX, nY, xRot = 0.0, yRot = 180.0)
                    sList.append(tmp)
            else:
                raise ValueError('GDSII_Director.addArray : The cellName parameter must be a string or a list of strings')
        return sList
    
    def addCellRef(self, cellName, cellRef, xy = [[0,0],[0,10000],[10000,0],[10000,10000]]):
        '''
        addCellRef(cellName, cellRef, xy)
        
        Creates a cell and references other cells
        
        Parameters
        ----------
        cellName : string
            Name of cell
        cellRef : string or list of strings
            Name of cells to reference
        xy : list of integer pairs
            Each integer pair specifies the position of the referenced cell
        '''
        if type(cellRef) is str:
            cellRef = [cellRef]
        if type(xy[0]) is int:
            xy = [xy]
            
        if len(cellRef) != len(xy):
            raise ValueError('GDSII_Director.addDS : The length of cellRef and xy should be equal')

        try:
            self.g.addStructure(cellName)
        except:
            pass
        
        for i in range(len(xy)):
            self.g.addSRef(cellName, cellRef[i], xy[i])
    
    def addARef(self, cellName, cellRef, pitchX, pitchY, nX, nY, xy = [[0,0],[0,10000],[10000,0],[10000,10000]]):
        '''
        addARef(cellName, cellRef, pitchX, pitchY, nX, nY, xy)
        
        Creates a cell and array references other cells
        
        Parameters
        ----------
        cellName : string
            Name of cell
        cellRef : string or list of strings
            Name of cells to reference   
        pitchX : integer
            Array spacing along X           
        pitchY : integer
            Array spacing along Y     
        nX : integer
            Number of repeats along X        
        nY : integer
            Number of repeats along Y
        xy : list of integer pairs
            Each integer pair specifies the position of the referenced cell
        '''
        if type(cellRef) is str:
            cellRef = [cellRef]
        if type(xy[0]) is int:
            xy = [xy]
            
        if len(cellRef) != len(xy):
            raise ValueError('GDSII_Director.addARef : The length of cellRef and xy should be equal')
        try:
            self.g.addStructure(cellName)
        except:
            pass
        
        for i in range(len(xy)):
            self.g.addARef(cellName, cellRef[i], xy[i], pitchX, pitchY, nX, nY, xRot = 0.0, yRot = 180.0)    
    
    def drawCross(self, width = 10, length = 100):
        '''
        drawCross(width, length)
        
        Returns the vertices of a cross
        
        Parameters
        ----------
        width : integer
            Width of the cross
        length : integer
            Length of the cross
            
        Results
        -------
        xy : Nx1 numpy.ndarray of type numpy.int32
            The vertices of the cross
        '''
        if width >= length:
            raise ValueError('GDSII_Director.drawCross : The width cannot be greater than or equal to the length')
        a = length/2-width/2
        b = length/2+width/2
        xy = np.array([0,a,0,b,a,b,a,length,b,length,b,b,length,b,length,a,b,a,b,0,a,0,a,a,0,a],dtype=np.int32)
        return xy
        
    def drawCircle(self, radius, nSegment, startAngle = None, clockwise = True):
        '''
        drawCircle(radius, nSegment, startAngle = None, clockwise = True)
        
        Returns the vertices of a circle at the specified vertices
        
        Parameters
        ----------
        radius : unsigned float or integer
            The radius of the circle
        nSegment : unsigned integer
            Specify the number of segments used to represent the circle
        startAngle : float or integer
            The angle of the first vertex in [degrees]
            None : Default start angle is 360/nSegment
        clockwise : boolean
            The direction of rotation for generating each vertex
        
        Returns
        -------
        xy : Nx1 numpy.ndarray of type numpy.int32
            The vertices of the circle
        '''
        if startAngle is None:
            startAngle = 360/float(nSegment*2)
            
        startAngle *= np.pi/180
        
        dTheta = np.zeros(nSegment, dtype=np.float)
        if clockwise:
            for i in range(nSegment):
                dTheta[i] = -i*2*np.pi/nSegment + startAngle
        else:
            for i in range(nSegment):
                dTheta[i] = i*2*np.pi/nSegment + startAngle
        x = radius*np.cos(dTheta)
        y = radius*np.sin(dTheta)

        xy = np.zeros(nSegment*2+2, dtype=np.int32)
        x -= np.min(x)
        y -= np.min(y)
        xy[:-2:2] = np.round(x)
        xy[1:-2:2] = np.round(y)
        xy[-2] = xy[0]
        xy[-1] = xy[1]
        
        return xy
    
    def drawCircleInverse(self, pitch, radius, nSegment, startAngle = 0, clockwise = True):
        '''
        drawCircle(pitch, radius, nSegment, startAngle = 0, clockwise = True)
        
        Return the x, y coordinates of a circle at the specified vertices
        
        Parameters
        ----------
        pitch : integer
            The size of a box that surrounds the circle
        radius : unsigned float or integer
            The radius of the circle
        nSegment : unsigned integer
            Specify the number of segments used to represent the circle
        startAngle : float or integer
            The angle of the first vertex in [degrees]
        clockwise : boolean
            The direction of rotation for generating each vertex
        
        Returns
        -------
        x : numpy.ndarray of type numpy.float
            The x posistion of each vertices
        y : numpy.ndarray of type numpy.float
            The y position of each vertices
        '''
        if startAngle > 90 or startAngle < -90:
            raise ValueError('GDSII_Director.drawCircleInverse : startAngle must be in quadrant 1 or 4')
        tmp = self.drawCircle(radius, nSegment, startAngle, clockwise)
        tmp[::2] -= np.min(tmp[::2])
        tmp[1::2] -= np.min(tmp[1::2])
        tmp += (pitch-radius*2)/2
        xy = np.zeros(tmp.size+14,dtype=np.int32)
        xy[0:6] = np.array([0, 0, pitch, 0, pitch, tmp[1]])
        xy[6:-8] = tmp
        xy[-8:] = np.array([pitch,tmp[1],pitch, pitch, 0, pitch, 0, 0])
        return xy

    def drawSquare(self, width):
        '''
        drawSquareInverse(width)
        
        Returns a polygon of an square
        
        Parameters
        ----------
        width : integer
            width of the square

        Returns
        -------
        xy : numpy.ndarray of type numpy.int32
            The vertices of the square
        '''
        xy = np.array([0,0,width,0,width,width,0,width,0,0],dtype=np.int32) 
        return xy
 
    def drawSquareInverse(self, pitch, width):
        '''
        drawSquareInverse(pitch, width)
        
        Returns a polygon of an inverse square
        
        Parameters
        ----------
        pitch : integer
            The size of a box that surrounds the square
        width : integer
            Width of the square
            
        Returns
        -------
        xy : numpy.ndarray of type numpy.int32
            The vertices of the inverse square
        '''
        tmp = self.drawSquare(width)
        tmp += (pitch-width)/2
        xy = np.zeros(tmp.size+12,dtype=np.int32)
        xy[0:10] = np.array([0, 0, 0, pitch, pitch, pitch, pitch, 0, tmp[0], 0])
        xy[10:-4] = tmp[:-2]
        xy[-4:] = np.array([tmp[-2],0, 0, 0])
        return xy

    def drawRectangle(self, width, height):
        '''
        drawRectangle(width, height)
        
        Returns a polygon of a rectangle
        
        Parameters
        ----------
        width : integer
            width of the rectangle along x
        height : integer
            height of the rectangle along y

        Returns
        -------
        xy : numpy.ndarray of type numpy.int32
            The vertices of the square
        '''
        xy = np.array([0,0,width,0,width,height,0,height,0,0],dtype=np.int32) 
        return xy

    def genPos(self, x, y):
        '''
        genPos(x, y)
        
        Generates a list of positions
        
        Parameters
        ----------
        x : integer or list of integer
            The x positions
        y : integer or list of integer
            The y positions
            
        Returns
        -------            
        xy : list of integer pairs
            A list of xy positions
            
        Description
        -----------
        x = 0, y = [0, 1, 2, 4]
            xy = [[0,0],[0,1],[0,2],[0,4]]
        x = [0, 1, 2, 5], y = 0
            xy = [[0,0],[1,0],[2,0],[5,0]]
        x = [0, 1], y = [2, 3]
            xy = [[0,2],[0,3],[1,2],[1,3]]
        '''
        if type(x) is int:
            x = [x]
        if type(y) is int:
            y = [y]
            
        xy = []
        for i in x:
            for j in y:
                xy.append([i,j])
                
        return xy
    
    def writeFile(self, filename):
        '''
        writeFile(filename)
        
        Writes the gds file
        
        Parameters
        ----------
        filename : string
            Nameof the file
        '''
        self.g.writeFile(filename)

def main():
    datatype = [0, 1, 2, 3, 4, 5, 6, 7, 8]    
    
    G = GDSII_Director()
    
    lxy = G.genPos(range(0,160001,20000),0)
    xy = G.drawSquareInverse(200,40)
    tmp = G.addCell('w40_p200',xy,datatype)
    tmp = G.addArray(tmp,200,200,50,50)
    G.addCellRef('A_w40_p200_DS',tmp,lxy)
    
    xy = G.drawSquareInverse(200,60)
    tmp = G.addCell('w60_p200',xy,datatype)
    tmp = G.addArray(tmp,200,200,50,50)
    G.addCellRef('A_w60_p200_DS',tmp,lxy)
    
    xy = G.drawSquareInverse(200,80)
    tmp = G.addCell('w80_p200',xy,datatype)
    tmp = G.addArray(tmp,200,200,50,50)
    G.addCellRef('A_w80_p200_DS',tmp,lxy)
    
    xy = G.drawSquareInverse(200,100)
    tmp = G.addCell('w100_p200',xy,datatype)
    tmp = G.addArray(tmp,200,200,50,50)
    G.addCellRef('A_w100_p200_DS',tmp,lxy)
    
    tmp = ['A_w40_p200_DS','A_w60_p200_DS','A_w80_p200_DS','A_w100_p200_DS']
    xy = [[0,0],[0,20000],[0,40000],[0,60000]]
    G.addCellRef('main',tmp,xy)
    
    xy = G.drawCircleInverse(200,50,8)
    tmp = G.addCell('c100_s8_p200',xy,datatype)
    tmp = G.addArray(tmp,200,200,50,50)
    G.addCellRef('A_c100_s8_p200_DS',tmp,lxy)
    
    xy = G.drawCircleInverse(200,50,10)
    tmp = G.addCell('c100_s10_p200',xy,datatype)
    tmp = G.addArray(tmp,200,200,50,50)
    G.addCellRef('A_c100_s10_p200_DS',tmp,lxy)
    
    xy = G.drawCircleInverse(200,50,12)
    tmp = G.addCell('c100_s12_p200',xy,datatype)
    tmp = G.addArray(tmp,200,200,50,50)
    G.addCellRef('A_c100_s12_p200_DS',tmp,lxy)
    
    xy = G.drawCircleInverse(200,50,14)
    tmp = G.addCell('c100_s14_p200',xy,datatype)
    tmp = G.addArray(tmp,200,200,50,50)
    G.addCellRef('A_c100_s14_p200_DS',tmp,lxy)
    
    tmp = ['A_c100_s8_p200_DS','A_c100_s10_p200_DS','A_c100_s12_p200_DS','A_c100_s14_p200_DS']
    xy = [[0,80000],[0,100000],[0,120000],[0,140000]]
    G.addCellRef('main',tmp,xy)    
    
    G.writeFile('Test.gds')
   
if __name__ == '__main__':
    main()