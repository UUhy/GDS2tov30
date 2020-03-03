#!/usr/bin/env ipython

import numpy as np
from ELD_Pattern import ELD_Pattern

class ELD_Cell(object):
    '''
    ELD Cell class
    
    ELD_Cell is part of the ELD datastructure.  This class is designed to 
    contain groups of patterns.  
       
    The functions of this class are:
        addField                =   Adds a field
        addCell                 =   Adds a cell to a field
        addPattern              =   Adds a pattern to a cell
        setPatternArray         =   Sets the pattern array parameters
        setCellArray            =   Sets the cell array parameters
        setCellDisplacement     =   Sets cell displacement
        offsetCellDisplacement  =   Offsets the cell displacement
        displacePattern         =   Displace all patterns
        scalePattern            =   Scale all patterns
        cart2img                =   Transform cartesian to image coordinates
        fracture                =   Fracture all patterns into primitives
        fieldFracture           =   Fracture all patterns into fields
       
    Long Chang, UH, August 2013
    '''

    def __init__(self, cellID = 0):
        self._cellID = cellID
        self._pattern = []
        self._shotRank = []
        self._displacement = np.zeros(2,dtype=np.int32)
        self._boundary = np.array([2**31-1, 2**31-1, 0, 0, 0, 0],dtype=np.int32)
        self._nX = 1
        self._nY = 1
        self._pitchX = 0
        self._pitchY = 0
        self._cellArray = False
        self._patternArray = False

    def __repr__(self):
        print 'ELD_Cell object'
        print 'cellID :           ' , self.cellID
        print 'shotRank :         ' , self.shotRank
        print 'pattern :          ' , len(self.pattern)
        print 'displacement :     ' , self.displacement
        print 'boundary :         ' , self.boundary
        print 'nX :               ' , self.nX
        print 'nY :               ' , self.nY
        print 'pitchX :           ' , self.pitchX
        print 'pitchY :           ' , self.pitchY
        return ''
        
    @property
    def cellID(self):
        '''
        cellID : list of unique integers
            List of cell identification numbers
        '''
        return self._cellID
        
    @property
    def shotRank(self):
        '''
        shotRank : integer
            Shot rank value
        '''
        return self._shotRank
        
    @shotRank.setter
    def shotRank(self, val):
        self._shotRank.append(val)
        
    @property
    def boundary(self):
        '''
        boundary : list of 6 integers
            The smallest box that contains all patterns
            [x_min, y_min, x_max, y_max, ax_max, ay_max]
        '''
        return self._boundary
    
    @boundary.setter
    def boundary(self, val):
        self._boundary = val
        
    @property
    def displacement(self):
        '''
        displacement : 2x1 numpy.ndarray of type numpy.int32
            Displacement from canvas or field origin
            [x_offset, y_offset]
        '''
        return self._displacement
    
    @displacement.setter
    def displacement(self, val):
        self._displacement = val
        
    @property
    def nX(self):
        '''
        nX : integer
            Array repeats along X
        '''
        return self._nX
    
    @nX.setter
    def nX(self, val):
        self._nX = int(val)
        
    @property
    def nY(self):
        '''
        nY : integer
            Array repeats along Y
        '''
        return self._nY
    
    @nY.setter
    def nY(self, val):
        self._nY = int(val)
        
    @property
    def pitchX(self):
        '''
        pitchX = integer
            Array pitch or step along X
        '''
        return self._pitchX
    
    @pitchX.setter
    def pitchX(self, val):
        self._pitchX = int(val)
        
    @property
    def pitchY(self):
        '''
        pitchY = integer
            Array pitch or step along Y
        '''
        return self._pitchY
    
    @pitchY.setter
    def pitchY(self, val):
        self._pitchY = int(val)
        
    @property
    def pattern(self):
        '''
        pattern : list of ELD_Pattern instances
            A list of patterns
        '''
        return self._pattern
        
    @pattern.setter
    def pattern(self, val):
        self._pattern = val
    
    def addPattern(self, vertices, shotRank = 0):
        '''
        addPattern(vertices, shotRank = 0)
        
        Adds a polygon to this cell
        
        Parameters
        ----------
        vertices : list of integers or numpy.ndarray of type numpy.int32
            The vertices of a polygon in he form
            [x0 y0 x1 y1 ... xn yn x0 y0]
        shotRank : integer from 0 to 255
            Shot rank value
        '''
        if type(vertices) is list:
            vertices = np.array(vertices,np.int32)
        elif not isinstance(vertices,np.ndarray):
            raise TypeError('ELD_Pattern.addCell() : The vertices must be a numpy.ndarray of type numpy.int32')
        elif not vertices.dtype == np.int32:
            raise TypeError('ELD_Pattern.addCell() : The vertices must be of type numpy.int32')
        try:
            self.pattern[self.shotRank.index(shotRank)].addPolygon(vertices)
            self.updateBoundary()
        except:
            tmp = ELD_Pattern(shotRank)
            tmp.addPolygon(vertices)
            self.pattern.append(tmp)
            self.shotRank = shotRank
            self.updateBoundary()
            
    def setCellArray(self, pitchX = 0, pitchY = 0, nX = 1, nY = 1):
        '''
        setCellArray(pitchX, pitchY, nX, nY)
        
        Sets the cell array parameters
        
        Parameters
        ----------
        pitchX : integer
            Array pitch or step along X
        pitchY : integer
            Array pitch or step along Y
        nX : integer
            Array repeats along X
        nY : integer
            Array repeats along Y
        '''
        self.pitchX = pitchX
        self.pitchY = pitchY
        self.nX = nX
        self.nY = nY
        self.updateBoundary()
    
    def scalePattern(self, scale):
        '''
        scalePattern(scale)
        
        Scales the pattern
        
        Parameters
        ----------
        scale : float
            Scale factor
            
        Note
        ----
        This function DOES NOT scale patterns or parameters added later
        '''
        for i in range(len(self.pattern)):
            self.pattern[i].scalePattern(scale)
        self.displacement *= scale
        self.pitchX *= scale
        self.pitchY *= scale
        self.updateBoundary()

    def displacePattern(self):
        '''
        displacePattern()
        
        Displace all patterns
        '''
        try:
            for i in self.pattern:
                i.displacePattern(self.displacement)
            self.displacement = np.zeros(2,dtype=np.int32)
            self.updateBoundary()
        except:
            raise ValueError('ELD_Chip.displacePattern() : The specified field does not exist')

    def zeroPattern(self):
        '''
        zeroPattern()
        
        Displace all patterns to such that the lower boundary is 0,0
        '''
        self.updateBoundary()
        if self.boundary[0] != 0 or self.boundary[1] != 0:
            try:
                self.displacement += self.boundary[0:2]
                for i in self.pattern:
                    i.displacePattern(-1*self.boundary[0:2])
                self.updateBoundary()
            except:
                raise ValueError('ELD_Cell.zeroPattern() : An unknown error has occured')         
       
    def cart2img(self):
        '''
        cart2img()
        
        Transform from cartesian coordinates to image coordinates
        '''
        self.updateBoundary()
        if self.boundary[0] != 0 or self.boundary[1] != 0:
            dxy = -self.boundary[0:2]
            for i in self.pattern:
                i.displacePattern(dxy)
            self.displacement -= dxy
            
        self.updateBoundary()
        offset = self.boundary[3]
        for i in self.pattern:
            for j in i.xy:
                j[1::2] = offset - j[1::2]
            
    def updateBoundary(self):
        '''
        updateBoundary()
        
        Updates the boundary parameter
        '''
        self.boundary = np.array([2**31-1, 2**31-1, 0, 0, 0, 0],dtype=np.int32)
        for i in self.pattern:
            #Update boundary
            i.updateBoundary()
            if i.boundary[0] < self.boundary[0]:
                self.boundary[0] = i.boundary[0]
            if i.boundary[2] > self.boundary[2]:
                self.boundary[2] = i.boundary[2]
            if i.boundary[1] < self.boundary[1]:
                self.boundary[1] = i.boundary[1]
            if i.boundary[3] > self.boundary[3]:
                self.boundary[3] = i.boundary[3]
        self.boundary[4] = self.boundary[2] + self.pitchX*(self.nX-1)
        self.boundary[5] = self.boundary[3] + self.pitchY*(self.nY-1)

    def fracture(self):
        '''
        fracture()
        
        Fractures all polygons into primitives
        '''
        for i in self.pattern:
            i.fracture()
    
    def fieldFracture(self, fieldSize = [200000,200000]):
        '''
        fieldFracture(fieldSize = [200000, 200000])
        
        Fractures the patterns along field boundaries
        
        Parameters
        ----------
        fieldSize : list of 2 integers
            Specify the width and height of each field
        '''
        for i in self.pattern:
            i.fieldFracture(fieldSize)
        self.updateBoundary()

def test():
    import matplotlib.pyplot as plot
    a = ELD_Cell()
    a.addPattern([10,10,20,40,30,10,10,10],5)
    a.addPattern([40,40,50,60,60,40,40,40],3)
    plot.plot(a.pattern[0].xy[0][::2],a.pattern[0].xy[0][1::2])
    plot.plot(a.pattern[1].xy[0][::2],a.pattern[1].xy[0][1::2])
    plot.show()
    a.setCellArray(100,100,100,100)
    a.cart2img()
    print a
    plot.plot(a.pattern[0].xy[0][::2],a.pattern[0].xy[0][1::2])
    plot.plot(a.pattern[1].xy[0][::2],a.pattern[1].xy[0][1::2])
    plot.gca().invert_yaxis()
    plot.show()

if __name__ == '__main__':
    test()
