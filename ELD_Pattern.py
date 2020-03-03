#!/usr/bin/env ipython

import numpy as np
import sys
if '/Users/Long/desktop/work/scripts/python/20130626_Fracture' not in sys.path:
    sys.path.append('/Users/Long/desktop/work/scripts/python/20130626_Fracture')
from fracture import fracture
if '/Users/Long/desktop/work/scripts/python/20130422_v3' not in sys.path:
    sys.path.append('/Users/Long/desktop/work/scripts/python/20130422_v3')
from v3_Pat import v3_Pat

class ELD_Pattern(object):
    '''
    ELD Pattern class
    
    ELD_Pattern is part of the ELD datastructure.  This class is designed to 
    organize pattern information.
       
    The functions of this class are:
        addPattern              =   Adds a pattern to a cell
        setCellArray            =   Sets the cell array parameters
        fracture                =   Fracture all patterns into primitives
       
    Long Chang, UH, August 2013
    '''

    def __init__(self, shotRank = 0):
        self._shotRank = shotRank
        self._xy = []
        self._boundary = np.array([2**31-1, 2**31-1, 0, 0],dtype=np.int32)
        self.checkPrimitive = v3_Pat().checkPrimitive

    def __repr__(self):
        print 'ELD_Pattern object'
        print 'shotRank :         ' , self.shotRank
        print 'boundary :         ' , self.boundary
        print 'xy :               ' , self.xy
        return ''
        
    @property
    def xy(self):
        '''
        xy : list of Nx1 numpy.ndarray of type numpy.int32
            List of polygon.  Each polygon is represented as an array of
            vertices of the form:
                [x0 y0 x1 y1 ... xn yn x0 y0]
        '''
        return self._xy
        
    @xy.setter
    def xy(self, val):
        self._xy = val
        
    @property
    def shotRank(self):
        '''
        shotRank : integer
            Shot rank value
        '''
        return self._shotRank
        
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
    
    def addPolygon(self, vertices):
        '''
        addPolygon(vertices)
        
        Adds a polygon to this class
        
        Parameters
        ----------
        vertices : list of integers or numpy.ndarray
            The vertices of a polygon in he form
            [x0 y0 x1 y1 ... xn yn x0 y0]
        
        Note
        ----
        vertices are stored as a list of numpy.ndarray of dtype numpy.int32
        '''
        if type(vertices) is list:
            vertices = np.array(vertices,np.int32)
        elif not type(vertices) is np.ndarray:
            raise TypeError('ELD_Pattern.addPolygon() : The vertices must be a list or numpy.ndarray')
        elif not vertices.dtype == np.int32:
            vertices = vertices.astype(np.int32)

        if not np.all(vertices[:2] == vertices[-2:]):
            vertices = np.append(vertices,vertices[:2],axis=0)
        
        if np.min(vertices[::2]) < self.boundary[0]:
            self.boundary[0] = np.min(vertices[::2])
        if np.max(vertices[::2]) > self.boundary[2]:
            self.boundary[2] = np.max(vertices[::2])
        if np.min(vertices[1::2]) < self.boundary[1]:
            self.boundary[1] = np.min(vertices[1::2])
        if np.max(vertices[1::2]) > self.boundary[3]:
            self.boundary[3] = np.max(vertices[1::2])
            
        self.xy.append(vertices)
    
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
        This function DOES NOT scale parameters added later
        '''
        for i in range(len(self.xy)):
            self.xy[i] *= scale
        self.boundary *= scale
        
    def displacePattern(self, displacement):
        '''
        displacePattern(displacement)
        
        Displace all patterns
        
        Parameters
        ----------
        displacement : 1x2 numpy.ndarray of type numpy.int32
        '''
        try:
            for i in self._xy:
                i += np.tile(displacement,i.size/2)
            self.updateBoundary()
        except:
            raise ValueError('ELD_Pattern.displacePattern() : The input parameter displacement must be an 1x2 numpy.ndarray of type numpy.int32')
    
    def updateBoundary(self):
        '''
        updateBoundary()
        
        Updates the boundary parameter
        '''
        self.boundary = np.array([2**31-1, 2**31-1, 0, 0],dtype=np.int32)
        for i in self.xy:
            #Update boundary
            if np.min(i[::2]) < self.boundary[0]:
                self.boundary[0] = np.min(i[::2])
            if np.max(i[::2]) > self.boundary[2]:
                self.boundary[2] = np.max(i[::2])
            if np.min(i[1::2]) < self.boundary[1]:
                self.boundary[1] = np.min(i[1::2])
            if np.max(i[1::2]) > self.boundary[3]:
                self.boundary[3] = np.max(i[1::2])    
    
    def fracture(self):
        '''
        fracture()
        
        Fractures all polygons into primitives
        '''
        tmp = fracture().fracture(self.xy)
        self.xy = [i.astype(np.int32) for i in tmp]
        
    def fieldFracture(self, fieldSize = [2000000, 2000000]):
        '''
        fieldFracture(fieldSize = [2000000, 2000000])
        
        Fractures the patterns along field boundaries
        
        Parameters
        ----------
        fieldSize : list of 2 integers
            Specify the width and height of each field
        '''
        tmp = fracture().fieldFracture(self.xy, fieldSize)
        self.xy = [i.astype(np.int32) for i in tmp]
        
    def lineFracture(self, position, horizontal=True):
        '''
        '''
        tmp = fracture().lineFracture(self.xy, position, horizontal)
        self.xy = [i.astype(np.int32) for i in tmp]

def test():
    a = ELD_Pattern(5)
    xy1 = [10,20,25,23,27,23,43,20,10,20]
    xy2 = [0,0,2,5,2,7,0,10,5,10,10,15,17,8,20,10,25,5,26,5,30,10,35,10,34,8,36,5,33,0,22,0,17,5,9,5,6,0,0,0]
    #xy3 = [40,15,39,18,45,10,40,15]
    xy3 = [40,1249,905,1249,905+19*2,1249-249*2,905+18*2,1249-249*2,40,1249]
    a.addPolygon(xy1)
    a.addPolygon(xy2)
    a.addPolygon(xy3)
#    print a
#    a.setArray(100,100,25,50)
#    print a
#    a.scalePattern(2)
#    print a
#    a.cart2img()
#    print a

    a.fracture()

    import matplotlib.pyplot as plot
    plot.plot(xy1[::2],xy1[1::2],'b-o',linewidth=1)
    plot.plot(xy2[::2],xy2[1::2],'b-o',linewidth=1)
    plot.plot(xy3[::2],xy3[1::2],'b-o',linewidth=1)
    for i in a.xy:
        plot.plot(i[::2],i[1::2],'--',linewidth=4)
    plot.show()
        
    #print a
    

if __name__ == '__main__':
    test()
