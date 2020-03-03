#!/usr/bin/env ipython

import numpy as np
from ELD_Cell import ELD_Cell
from arrayFracture import arrayFracture

class ELD_Canvas(object):
    '''
    ELD Canvas class
    
    ELD_Canvas is part of the ELD datastructure.  This class is designed to 
    contain all layout information to facilitate processing such as
    fracturing, field fracturing, array fracturing, coordinate transforms,
    scaling, displacements, etc.
       
    The functions of this class are:
        addField                =   Adds a field
        addCell                 =   Adds a cell to a field
        addPattern              =   Adds a pattern to a cell
        setCellArray            =   Sets the cell array parameters
        setCellDisplacement     =   Sets cell displacement
        offsetCellDisplacement  =   Offsets the cell displacement
        displacePattern         =   Displace all patterns
        scalePattern            =   Scale all patterns
        cart2img                =   Convert cartesian to image coordinates
        fracture                =   Fracture all patterns into primitives
        fieldFracture           =   Fracture all patterns into fields
        arrayFracture           =   Fracture arrays into fields
       
    Long Chang, UH, August 2013
    
    Shell.gds
    '''

    def __init__(self):
        self._cellID = []
        self._cell = []
        self._boundary = np.array([2**31-1, 2**31-1, 0, 0],dtype=np.int32)
        #self._fieldSize = None
        self._area= np.zeros((256,),dtype=np.uint32)

    def __repr__(self):
        print 'ELD_Canvas object'
        print 'cell :             ' , len(self.cell)
        print 'boundary :         ' , self.boundary
        return ''
        
    @property
    def boundary(self):
        '''
        boundary : 4x1 numpy.ndarray of type numpy.int32
            The smallest box that contains all patterns
            [x_min, y_min, x_max, y_max]
        '''
        return self._boundary
    
    @boundary.setter
    def boundary(self, val):
        self._boundary = val
        
    @property
    def cell(self):
        '''
        cell : a list of ELD_Cell instances
            A list of cells
        '''
        return self._cell
        
    @cell.setter
    def cell(self, val):
        self._cell = val
        
    @property
    def cellID(self):
        '''
        cellID : list of unique integers
            List of cell identification numbers
        '''
        return self._cellID
        
    @cellID.setter
    def cellID(self, val):
        self._cellID.append(val)

    def addCell(self, cellID):
        '''
        addCell(cellID = None)
        
        Adds a cell to the canvas and returns the cellID
        
        Parameters
        ----------
        cellID : integer
            Adds a cell with the specified identification number to the canvas
            
        Returns
        -------
        cellID : integer
            The identification number of the new cell
        '''
        if cellID in self.cellID:
            raise ValueError('ELD_Canvas.addCell() : The specified cellID is already defined.')
        else:
            tmp = ELD_Cell(cellID)
            self.cell.append(tmp)
            self.cellID = cellID
    
    def addPattern(self, cellID, vertices, shotRank = 0):
        '''
        addPattern(vertices, shotRank = 0)
        
        Adds a pattern to the specified cell
        
        Parameters
        ----------
        cellID : integer
            Cell identification number
        vertices : list of integers or numpy.ndarray of type numpy.int32
            The vertices of a polygon in he form
            [x0 y0 x1 y1 ... xn yn x0 y0]
        shotRank : integer from 0 to 255
            Shot rank value

        '''
        if isinstance(vertices,list):
            vertices = np.array(vertices,np.int32)
        elif not isinstance(vertices,np.ndarray):
            raise TypeError('ELD_Field.addPattern() : This parameter must be of type numpy.ndarray')
        try:
            self.cell[self.cellID.index(cellID)].addPattern(vertices, shotRank)
        except:
            raise ValueError('ELD_Field.addPattern() : The specified cell does not exist')
            
    def setCellArray(self, cellID, pitchX = 0, pitchY = 0, nX = 1, nY = 1):
        '''
        setCellArray(cellID, pitchX = 0, pitchY = 0, nX = 1, nY = 1)
        
        Set the array parameters for the specified cell
        
        Parameters
        ----------
        CellID : integer
            Cell identification number
        pitchX : integer
            Array pitch or step along X
        pitchY : integer
            Array pitch or step along Y
        nX : integer
            Array repeats along X
        nY : integer
            Array repeats along Y
        '''
        try:
            self.cell[self.cellID.index(cellID)].setCellArray(pitchX,pitchY,nX,nY)
        except:
            raise ValueError('ELD_Cell.setCellArray() : The specified cell ID has not been defined')
    
    def setCellDisplacement(self, cellID, displacement):
        '''
        setCellDisplacement(cellID, displacement)
        
        Set the displacement parameter for the specified cell
        
        Parameters
        ----------
        cellID : integer
            Cell identification number
        displacement : 2x1 numpy.ndarry of type numpy.int32
            Displacement from the origin
        '''
        try:
            self.cell[self.cellID.index(cellID)].displacement = displacement
        except:
            raise ValueError('ELD_Field.setCellDisplacement() : The specified cellID does not exist')
            
    def offsetCellDisplacement(self, cellID, displacement):
        '''
        offsetCellDisplacement(cellID, displacement)
        
        Offsets the displacement parameter for the specified cell
        
        Parameters
        ----------
        cellID : integer
            Cell identification number
        displacement : 2x1 numpy.ndarry of type numpy.int32
            Offset from the displacement value
        '''
        try:
            self.cell[self.cellID.index(cellID)].displacement += displacement
        except:
            raise ValueError('ELD_Field.offsetCellDisplacement() : The specified cellID does not exist')
            
    def displacePattern(self):
        '''
        displacePattern()
        
        Displace all patterns and zero the displacement parameter
        '''
        try:
            for i in self.cell:
                i.displacePattern()
        except:
            raise ValueError('ELD_Field.displacePattern() : The specified field does not exist')
    
    def scalePattern(self, scale):
        '''
        scalePattern(scale)
        
        Scales all the patterns
        
        Parameters
        ----------
        scale : float
            Scale factor
            
        Note
        ----
        This function DOES NOT scale patterns or parameters added later
        '''
        for i in range(len(self.cell)):
            self.cell[i].scalePattern(scale)
        self.updateBoundary()
        
    def cart2img(self):
        '''
        cart2img()
        
        Transform from cartesian coordinates to image coordinates
        '''
        self.updateBoundary()
        if self.boundary[0] != 0 or self.boundary[1] != 0:
            dxy = self.boundary[:2]
            for i in self.cell:
                i.displacement -= dxy
        
        self.updateBoundary()
        dy = self.boundary[3]
        for i in self.cell:
            i.cart2img()
            i.displacement[1] = dy - i.displacement[1] - i.boundary[5]
        self.displacePattern()
        self.updateBoundary()
    
    def updateBoundary(self):
        '''
        updateBoundary()
        
        Updates the boundary parameter
        '''
        self.boundary = np.array([2**31-1, 2**31-1, 0, 0],dtype=np.int32)
        for i in self.cell:
            #Update boundary
            i.updateBoundary()
            tmp = i.boundary[0] + i.displacement[0]
            if tmp < self.boundary[0]:
                self.boundary[0] = tmp
            tmp = i.boundary[4] + i.displacement[0]
            if  tmp > self.boundary[2]:
                self.boundary[2] = tmp
                
            tmp = i.boundary[1] + i.displacement[1]
            if tmp < self.boundary[1]:
                self.boundary[1] = tmp
            tmp = i.boundary[5] + i.displacement[1]
            if  tmp > self.boundary[3]:
                self.boundary[3] = tmp
    
    def fracture(self):
        '''
        fracture()
        
        Fractures all polygons into primitives
        '''
        for i in self.cell:
            i.fracture()
            
    def fieldFracture(self, fieldSize = [200000, 200000]):
        '''
        fieldFracture(fieldSize = [200000, 200000])
        
        Fractures the patterns along field boundaries
        
        Parameters
        ----------
        fieldSize : list of 2 integers
            Specify the width and height of each field
        '''
        for i in self.cell:
            if np.sum(i.displacement > 0) >= 1:
                i.displacePattern()
            i.fieldFracture(fieldSize)
#            tmp = [i.boundary[0]/fieldSize[0], i.boundary[1]/fieldSize[1], i.boundary[4]/fieldSize[0], i.boundary[5]/fieldSize[1]]
#            if tmp[0] == tmp[2] or tmp[1] == tmp[3]:
#                displacement = np.array([tmp[0]*fieldSize[0]+i.displacement[0], tmp[1]*fieldSize[1]+i.displacement[1]],dtype=np.int32)
#                i.displacement = -displacement
#                i.displacePattern()
#                i.displacement = displacement
#            
#            print 'hello'
            
    def arrayFracture(self, fieldSize = [200000, 200000], maxArrayLength = 2000):
        '''
        arrayFracture(fieldSize = [200000, 200000], maxArrayLength = 2000)
        
        Fractures arrays
        
        Parameters
        ----------
        fieldSize : list of 2 integers
            Specify the width and height of each field
        maxArrayLength : integer
            Specify the maximum array repeat value
            
        Description
        -----------
        1)  Fracture arrays such that nX and nY <= maxArrayLength
        2)  Fracture arrays along field lines on the x axis
        3)  Fracture arrays along field lines on the y axis
        '''
        
        #Fracture array such that nX and nY <= maxArrayLength
        for i in range(len(self.cell)-1,-1,-1):
            tmp = arrayFracture().resize(self.cell[i],maxArrayLength)
            if len(tmp) > 1:
                self.cell.pop(i)
                [i.displacePattern() for i in tmp]
                self.cell.extend(tmp)
        
        #Fracture arrays along field lines
        for i in range(len(self.cell)-1,-1,-1):
            tmp = arrayFracture().fieldFracture(self.cell[i],fieldSize)
            if len(tmp) > 1:
                self.cell.pop(i)
                [i.displacePattern() for i in tmp]
                self.cell.extend(tmp)

    @property
    def area(self):
        return self._area
    
    @area.setter
    def area(self, val):
        self._area = val
    
    def getArea(self):
        '''
        getArea()
        
        Calculates the area of all patterns in canvas
        '''
        for i in self.cell:
            for j in i.pattern:
                tmp = 0
                for k in j.xy:
                    tmp += np.sum((k[:-2:2]+k[2::2])*(k[3::2]-k[1:-2:2]))/2
                if j.nX > 1 or j.nY > 1:
                    tmp *= j.nX*j.nY
                if i.nX > 1 or i.nY > 1:
                    tmp *= i.nX*i.nY
                self.area[j.shotRank] += tmp
                    

def test():
    import matplotlib.pyplot as plot
    a = ELD_Canvas()
    a.addCell(0)
#    a.addPattern(0,[200,0,220,40,230,10,200,0],5)
#    a.addPattern(0,[240,40,250,50,250,40,240,40],3)
    a.addPattern(0,[200,0,200,100,300,100,300,0,200,0],3)
    a.addCell(1)
    a.addPattern(1,[100,100, 200, 200, 300, 100, 100, 100],1)
    a.setCellArray(0,100,100,100,100)
    a.arrayFracture([5025,5025],2000)
    a.displacePattern()
    a.updateBoundary()
    for i in a.cell:
        for j in i.pattern:
            for k in j.xy:
                plot.plot(k[::2],k[1::2])
    plot.show()

    a.cart2img()
    a.updateBoundary()
    for i in a.cell:
        for j in i.pattern:
            for k in j.xy:
                plot.plot(k[::2],k[1::2])
    plot.gca().invert_yaxis()
    plot.show()
    print a.boundary

if __name__ == '__main__':
    test()
