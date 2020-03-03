#!/usr/bin/env ipython

import numpy as np
from ELD_Field import ELD_Field
from ELD_Canvas import ELD_Canvas

class ELD_Chip(object):
    '''
    ELD Chip class

    ELD_Chip is the top class in the ELD datastructure.  This class serves as
    the interface to store information in the ELD datastructure.    
    
    Electron-beam Lithography Datastructure (ELD)
    
    The ELD class is designed to support electron beam writing specifications
    such as fields, cells, arrays, and patterns.  This class should facilitate
    conversion from a powerful CAD layout format such as GDSII to a much more
    restrictive electron beam writing format such as Jeol v3.0.
       
    The functions of this class are:
        addField                =   Adds a field
        addCell                 =   Adds a cell to a field
        addPattern              =   Adds a pattern to a cell
        setCellArray            =   Sets the cell array parameters
        setCellDisplacement     =   Sets cell displacement
        offsetCellDisplacement  =   Offsets the cell displacement
        setScale                =   Sets the scale
        setFieldSize            =   Sets the field size
        fracture                =   Fracture all patterns
       
    Long Chang, UH, August 2013
    '''

    def __init__(self):
        self._fieldID = []
        self._field = []
        self._canvas = ELD_Canvas()
        self._chipSize = np.zeros(2,dtype=np.int32)
        self._fieldSize = [2000000, 2000000]
        self._scale = 0

    def __repr__(self):
        print 'ELD_Chip object'
        print 'canvas :           ' , self.canvas
        print 'fieldID  :         ' , self.fieldID
        print 'field :            ' , len(self.field)
        print 'size         :     ' , self.chipSize
        return ''
        
    @property
    def chipSize(self):
        '''
        chipSize : 2x1 numpy.ndarray of type numpy.uint32
            The width and height of the chip
        '''
        return self._chipSize
    
    @chipSize.setter
    def chipSize(self, val):
        self._chipSize = val
        
    @property
    def canvas(self):
        '''
        canvas : ELD_Canvas object
            All patterns are stored on the "canvas" for processing
        '''
        return self._canvas
        
    @property
    def fieldSize(self):
        '''
        fieldSize : list of 2 integers
            The width and height of each field
        '''
        return self._fieldSize
        
    @fieldSize.setter
    def fieldSize(self, val):
        if not type(val) is list:
            raise TypeError('ELD_Chip.fieldSize : This parameter must be a list of 2 integers')
        if len(val) == 2:
            self._fieldSize = val
        else:
            raise ValueError('ELD_Chip.fieldSize : This parameter must be a list of 2 integers')
        
    @property
    def field(self):
        '''
        field : list of ELD_Field objects
            A list of fields
        '''
        return self._field
        
    @field.setter
    def field(self, val):
        self._field = val
        
    @property
    def fieldID(self):
        '''
        fieldID : list of integers
            A list of field indentification number
        '''
        return self._fieldID
        
    @fieldID.setter
    def fieldID(self, val):
        self._fieldID.append(val)
        
    @property
    def scale(self):
        '''
        scale : float
            Specify a scale factor to scale the patterns
        '''
        return self._scale
        
    @scale.setter
    def scale(self, val):
        self._scale = val

    def addField(self, fieldID):
        '''
        addField(fieldID)
        
        Adds a field to the canvas
        
        Parameters
        ----------
        fieldID : integer
            Adds a field with the specified identification number to the canvas
            The fieldID must be unique
        '''
        if fieldID in self.fieldID:
            raise ValueError('ELD_Chip.addField() : The specified fieldID is already defined.')
        else:
            tmp = ELD_Field(fieldID)
            self.field.append(tmp)
            self.fieldID = fieldID

    def addCell(self, cellID = None):
        '''
        addCell(cellID = None)
        
        Adds a cell to the canvas and returns the cellID
        
        Parameters
        ----------
        cellID : integer or None
            Adds a cell with the specified identification number to the canvas
            None    :   Automatically assign a unique identification number
            
        Returns
        -------
        cellID : integer
            The identification number of the new cell
        '''
        if cellID == None:
            try:
                cellID = np.max(self.canvas.cellID) + 1
            except:
                cellID = 0
                
        self.canvas.addCell(cellID)
        
        return self.canvas.cellID[-1]
    
    def addPattern(self, cellID, vertices, shotRank = 0):
        '''
        addPattern(cellID, vertices, shotRank = 0)
        
        Adds a pattern to the specified cell
        
        Parameters
        ----------
        cellID : integer
            Cell identification number
        vertices : list of integers or numpy.ndarray of type numpy.int32
            The vertices of a polygon in the form
            [x0 y0 x1 y1 ... xn yn x0 y0]
        shotRank : integer from 0 to 255
            Shot rank value
        '''
        if isinstance(vertices,list):
            vertices = np.array(vertices,np.int32)
        elif not isinstance(vertices,np.ndarray):
            raise TypeError('ELD_Chip.addPattern() : This parameter must be of type numpy.ndarray')
        self.canvas.addPattern(cellID, vertices, shotRank)
            
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
        self.canvas.setCellArray(cellID,pitchX,pitchY,nX,nY)
            
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
        self.canvas.setCellDisplacement(cellID,displacement)
    
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
        self.canvas.offsetCellDisplacement(cellID,displacement)
            
    def setScale(self, scale):
        '''
        setScale(scale)
        
        Sets the scale parameter for the chip
        
        Parameters
        ----------
        scale : float
            The scale factor used to scale all patterns in the chip
        '''
        self.scale = scale
        
    def setFieldSize(self, fieldSize):
        '''
        setFieldSize(fieldSize)
        
        Sets the field size parameter for the chip
        
        Parameters
        ----------
        fieldSize : 2x1 list of integers or numpy.ndarray of type numpy.uint32
            Sets the width and height ofthe field
        '''
        self.fieldSize = fieldSize

    def canvas2field(self):
        '''
        canvas2field()
        
        Places all patterns on the canvas into the appropriate fields
        
        Description
        -----------
        This function assumes the canvas is partitioned into fields arranged
        on a grid.
        '''
        nRow = self.chipSize[1]/self.fieldSize[1] + 1
        nCol = self.chipSize[0]/self.fieldSize[0] + 1
        aRow = [(i+1)*self.fieldSize[1] for i in range(nRow)]
        aCol = [(i+1)*self.fieldSize[0] for i in range(nCol)]
        
        for i in self.canvas.cell:
            cellID = i.cellID
            for j in i.pattern:
                for k in j.xy:
                    xMax = k[::2].max()
                    xMin = k[::2].min()
                    yMax = k[1::2].max()
                    yMin = k[1::2].min()
                    cCol = (xMax+xMin)/2 + i.displacement[0]
                    cRow = (yMax+yMin)/2 + i.displacement[1]
                    row = nRow-sum(cRow<aRow)
                    col = nCol-sum(cCol<aCol)
                    fieldID = row*nCol + col
                    try:
                        self.addField(fieldID)
                        self.field[-1].displacement = np.array([col*self.fieldSize[1], row*self.fieldSize[0]],dtype=np.int32)
                    except:
                        pass
                    iField = self.fieldID.index(fieldID)
                    self.field[iField].addCell(cellID)
                    k -= np.tile(self.field[iField].displacement,k.size/2)
#                    if i.displacement[0] > 0 or i.displacement[1] > 0:
#                        k += np.tile(i.displacement,k.size/2)
                    self.field[iField].addPattern(cellID,k,j.shotRank)
                    if i.nX == 1 and i.nY == 1:
                        pass
                    else:
                        self.field[iField].setCellArray(cellID, i.pitchX, i.pitchY, i.nX, i.nY)
        for i in self.field:
            i.updateBoundary()
        self.sortField()
                        
    def sortField(self):
        '''
        sortField()
        
        Sorts the field to minimize stage displacement
        
        Description
        -----------
        The fields are sorted along a serpentine path.  A more advanced
        algorithm that minimizes the total displacement may be implemented, but
        this is tough problem similar to the "random walk" or the "traveling
        salesman."
        '''
        fieldID = np.array(self.fieldID)
        sortedIndex = []
        nRow = self.chipSize[1]/self.fieldSize[1] + 1
        nCol = self.chipSize[0]/self.fieldSize[0] + 1
        for i in range(nRow-1,-1,-1):
            if i%2:
                for j in range(nCol):
                    tmp = fieldID == i*nCol + j
                    if np.sum(tmp) == 1:
                        sortedIndex.append(tmp.argmax())
            else:
                for j in range(nCol-1,-1,-1):
                    tmp = fieldID == i*nCol + j
                    if np.sum(tmp) == 1:
                        sortedIndex.append(tmp.argmax())
        self.field = [self.field[i] for i in sortedIndex]
        self._fieldID = [fieldID[i] for i in sortedIndex]
    
    def fracture(self):
        '''
        fracture()
        
        Fractures all polygons in canvas and distribute them into the proper
        fields
        '''
        if self.scale == 0:
            raise ValueError('ELD_Chip.scalePattern : The scale parameter must be positive nonzero')
        else:
            self.canvas.scalePattern(self.scale)
        self.canvas.cart2img()
        self.canvas.arrayFracture(self.fieldSize)
        self.canvas.fieldFracture(self.fieldSize)
        self.canvas.fracture()
        self.canvas.updateBoundary()
        self.chipSize = self.canvas.boundary[2:4]
        self.canvas2field()

if __name__ == '__main__':
    print 'No test defined'
