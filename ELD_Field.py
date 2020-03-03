#!/usr/bin/env ipython

import numpy as np
from ELD_Cell import ELD_Cell

class ELD_Field(object):
    '''
    ELD Field class
    
    ELD_Field is part of the ELD datastructure.  This class is designed to 
    store pattern information within a field.
       
    The functions of this class are:
        addCell                 =   Adds a cell to a field
        addPattern              =   Adds a pattern to a cell
        setCellArray            =   Sets the cell array parameters
       
    Long Chang, UH, August 2013
    '''

    def __init__(self, fieldID = 0):
        self._fieldID = fieldID
        self._cellID = []
        self._cell = []
        self._displacement = np.zeros(2,dtype=np.int32)
        self._boundary = np.array([2**31-1, 2**31-1, 0, 0],dtype=np.int32)
        self._fieldSize = 200000

    def __repr__(self):
        print 'ELD_Field object'
        print 'fieldID  :         ' , self.fieldID
        print 'cell :             ' , len(self.cell)
        print 'displacement :     ' , self.displacement
        print 'boundary :         ' , self.boundary
        return ''
        
    @property
    def fieldSize(self):
        '''
        fieldSize : 2x1 numpy.ndarray of type numpy.uint32
            The width and height of each field
        '''
        return self._fieldSize
        
    @property
    def fieldID(self):
        '''
        fieldID : list of unique integers
            List of field identification numbers
        '''
        return self._fieldID
        
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
    def displacement(self):
        '''
        displacement : 2x1 numpy.ndarray of type numpy.int32
            Displacement from chip origin
            [x_offset, y_offset]
        '''
        return self._displacement
    
    @displacement.setter
    def displacement(self, val):
        self._displacement = val
        
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
                cellID = np.max(self.cellID) + 1
            except:
                cellID = 0
        if cellID not in self.cellID:
            tmp = ELD_Cell(cellID)
            self.cell.append(tmp)
            self.cellID = cellID
        return self.cellID[-1]
    
    def addPattern(self, cellID, vertices, shotRank = 0):
        '''
        addPattern(cellID, vertices, shotRank = 0)
        
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
        if type(vertices) is list:
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
            
    def updateBoundary(self):
        '''
        updateBoundary()
        
        Updates the boundary parameter
        '''
        self.boundary = np.array([2**31-1, 2**31-1, 0, 0],dtype=np.int32)
        for i in range(len(self.cell)):
            #Update boundary
            self.cell[i].updateBoundary()
            if self.cell[i].boundary[0] < self.boundary[0]:
                self.boundary[0] = self.cell[i].boundary[0]
            if self.cell[i].boundary[2] + self.cell[i].pitchX*(self.cell[i].nX-1) > self.boundary[2]:
                self.boundary[2] = self.cell[i].boundary[2] + self.cell[i].pitchX*(self.cell[i].nX-1)
            if self.cell[i].boundary[1] < self.boundary[1]:
                self.boundary[1] = self.cell[i].boundary[1]
            if self.cell[i].boundary[3] + self.cell[i].pitchY*(self.cell[i].nY-1) > self.boundary[3]:
                self.boundary[3] = self.cell[i].boundary[3] + self.cell[i].pitchY*(self.cell[i].nY-1)

def test():
    a = ELD_Field(0)
    a.addCell(0)
    a.addPattern(0,[10,10,20,40,30,10,10,10],5)
    a.addPattern(0,[40,40,50,60,60,40,40,40],3)
    a.setPatternArray(0,5,100,100,100,100)
    a.addCell(1)
    a.addPattern(1,[100,100, 200, 200, 300, 100, 100, 100],1)
    print a
    a.scalePattern(2)
    print a
    a.cart2img()
    a.updateBoundary()
    print a

if __name__ == '__main__':
    test()
