#!/usr/bin/env ipython

import numpy as np
from GDSII import GDSII

class GDSII_Boundary(GDSII):
    '''
    GDSII_Boundary class : subclass of GDSII
    
    GDSII Stream file format release 6.0
    Boundary Element
    
    The boundary element is used to specify a filled polygon.  The GDSII v6.0
    format supports a boundary element with up to 200 vertices.  Layouts
    designed for IC manufacturing and Ebeam writing uses the boundary elements
    to specify patterns that will be exposed.
    
    Boundary elements can be assigned a layer number and a datatype number.
    Layers are used to group layout patterns for different processes.  
    Similarly datatypes are used to group the layout patterns for special
    purposes such as exposure modulation in ebeam writing.
    
    The functions of this class are:
       setBoundary      =   Populate the boundary element parameters
       genRecord        =   Generate the record binary
       readRecord       =   Reads a boundary element record
       
    Long Chang, UH, May 2013
    '''

    def __init__(self):
        super(GDSII_Boundary,self).__init__()
        self._layer = 0
        self._datatype = 0
        self._xy = np.array([0,0],dtype=np.int32)
        
        self._cBoundary = 0x0800    #Boundary element begin
        self._cELFLAG   = 0x2601    #ELFLAG property (optional)
        self._cPLEX     = 0x2F03    #PLEX property (optional)
        self._cLayer    = 0x0D02    #Layer property
        self._cDatatype = 0x0E02    #Datatype property
        self._cXY       = 0x1003    #XY property
        self._cEnd      = 0x1100    #Element end

    def __repr__(self):
        print 'Boundary element'
        print 'layer:             ' , self.layer
        print 'datatype:          ' , self.datatype
        print 'xy:                ' , self.xy
        return ''

    @property
    def layer(self):
        '''
        layer : integer from 0 to 255
            The layer number for this boundary element
        '''
        return self._layer
        
    @layer.setter
    def layer(self, val):
        if val < 0 or val > 256:
            raise ValueError('GDSII_Boundary.layer : This parameter must range from 0 to 255')
        self._layer = val
        
    @property
    def datatype(self):
        '''
        datatype : integer from 0 to 255
            The datatype number for this boundary element
        '''
        return self._datatype
        
    @datatype.setter
    def datatype(self, val):
        if val < 0 or val >= 256:
            raise ValueError('GDSII_Boundary.datatype : This parameter must range from 0 to 255')
        self._datatype = val
        
    @property
    def xy(self):
        '''
        xy : numpy.ndarray of type numpy.int32
            An array containing the verticies of a polygon in the form
            [x1 y1 x2 y2 ... xn yn x1 y1]
        '''
        return self._xy
        
    @xy.setter
    def xy(self, val):
        if isinstance(val,list):
            val = np.array(val,dtype=np.int32)
        elif not isinstance(val,np.ndarray):
            raise TypeError('GDSII_Boundary.xy : This parameter must be of type numpy.ndarray')
        if not val.size%2 == 0:
            raise ValueError('GDSII_Boundary.xy : This parameter must have an even number of elements')
        if not all(val[0:2] == val[-2:]):
            val = np.append(val,val[0:2],axis=0)
        self._xy = val

    def setBoundary(self, xy, layer=0, datatype=0):
        '''
        setBoundary(xy, layer=0, datatype=0)
        
        Adds a boundary element
        
        Parameters
        ----------
        xy : numpy.ndarray of type numpy.int32 or a list of integers
            An array containing the verticies of a polygon in the form
            [x1 y1 x2 y2 ... xn yn x1 y1]
        layer : integer from 0 to 255
            The layer number
        datatype : integer from 0 to 255
            The datatype number
        '''
        self.xy = xy
        self.layer = layer
        self.datatype = datatype

    @property
    def cBoundary(self):
        '''
        cBoundary : 0x0800
            Command code for boundary element begin
        '''
        return self._cBoundary
    
    @property
    def cLayer(self):
        '''
        cLayer : 0x0D02
            Command code for layer property
        '''
        return self._cLayer
        
    @property
    def cDatatype(self):
        '''
        cDatatype : 0x0E02 
            Command code for datatype property
        '''
        return self._cDatatype
    
    @property
    def cXY(self):
        '''
        cXY : 0x1003
            Command code for XY property
        '''
        return self._cXY
        
    @property
    def cEnd(self):
        '''
        cEnd : 0x1100
            Command code for element end
        '''
        return self._cEnd
        
    @property
    def cELFLAG(self):
        return self._cELFLAG
        
    @property
    def cPLEX(self):
        return self._cPLEX

    def genRecord(self):
        '''
        genRecord()
        
        Generates the boundary element binary
        
        Description
        -----------
        The boundary element is specified by records in thefollowing order:
            Boundary
            ELFLAGS     (optional)
            PLEX        (optional)
            Layer
            Datatype
            XY
        '''
        self.recordClear()
        
        #Boundary start
        self.record = self.dec2byte(4)
        self.record = self.dec2byte(self.cBoundary)
        
        #Define Layer
        self.record = self.dec2byte(6)
        self.record = self.dec2byte(self.cLayer)
        self.record = self.dec2byte(self.layer)
        
        #Define datatype
        self.record = self.dec2byte(6)
        self.record = self.dec2byte(self.cDatatype)
        self.record = self.dec2byte(self.datatype)

        #Define xy    
        self.record = self.dec2byte(self.xy.size*4+4)
        self.record = self.dec2byte(self.cXY)
        for i in self.xy:
            self.record = self.dec2byte(i,4)
            
        #Element end
        self.record = self.dec2byte(4)
        self.record = self.dec2byte(self.cEnd)
        
        self.recordClip()
            
    def readRecord(self, record):
        '''
        readRecord(record)
        
        Reads the boundary record and updates the boundary element parameters
        '''
        
        self.pointer = 0
        
        #Check if record is a boundary element
        if self.byte2dec(record[self.opCodePointer]) == self.cBoundary:
            self.pointer += 4
        else:
            raise ValueError('GDSII_Boundary.readRecord() : The record is not a boundary element')
            
        #Ignore ELFLAG
        if self.byte2dec(record[self.opCodePointer]) == self.cELFLAG:
            self.pointer += 6
        
        #Ignore PLEX
        if self.byte2dec(record[self.opCodePointer]) == self.cPLEX:
            self.pointer += 6
            
        #Layer
        if self.byte2dec(record[self.opCodePointer]) == self.cLayer:
            self.layer = self.byte2dec(record[[self.pointer+4,self.pointer+5]])
            self.pointer += 6
        else:
            raise ValueError('GDSII_Boundary.readRecord() : The layer number is not defined')
        
        #Datatype
        if self.byte2dec(record[self.opCodePointer]) == self.cDatatype:
            self.datatype = self.byte2dec(record[[self.pointer+4,self.pointer+5]])
            self.pointer += 6
        else:
            raise ValueError('GDSII_Boundary.readRecord() : The datatype number is not defined')
        
        #XY
        if self.byte2dec(record[self.opCodePointer]) == self.cXY:
            length = self.byte2dec(record[self.pointer:self.pointer+2]) - 4
            self.pointer += 4
            tmp = np.zeros(length/4,dtype=np.int32)
            index = 0
            for i in range(self.pointer,self.pointer+length,4):
                tmp[index] = self.byte2dec(record[i:i+4])
                index += 1
            self.xy = tmp
            self.pointer += length

def test():
    a = GDSII_Boundary()
    a.setBoundary([1111,2222,-3333,-4444,-5555,-6666,7777,0],2,1)
    a.genRecord()
    print a
    b = GDSII_Boundary()
    b.readRecord(a.record)
    print b
    

if __name__ == '__main__':
    test()
