#!/usr/bin/env ipython

import numpy as np
from GDSII import GDSII

class GDSII_Box(GDSII):
    '''
    GDSII_Box class : subclass of GDSII
    
    GDSII Stream file format release 6.0
    Box Element
    
    The box element is used to define a four-sided unfilled box.  As a result,
    a box element cannot be used to specify a quadrilateral for IC
    manufacturing or ebeam writing.  The box element has a layer and boxtype
    property for grouping purposes.
    
    I may use the box element to specify the field position for ebeam writing.
    
    The functions of this class are:
       setBox          =   Set the box
       genRecord       =   Generate the record binary
       readRecord      =   Reads a box element record
    
    Long Chang, UH, May 2013
    '''

    def __init__(self):
        super(GDSII_Box,self).__init__()
        self._layer = 0
        self._boxtype = 0
        self._xy = np.array([0,0],dtype=np.int32)
        
        self._cBox      = 0x2D00    #Box element begin
        self._cELFLAG   = 0x2601    #ELFLAG property (optional)
        self._cPLEX     = 0x2F03    #PLEX property (optional)
        self._cLayer    = 0x0D02    #Layer property
        self._cBoxtype  = 0x2E02    #Boxtype property
        self._cXY       = 0x1003    #XY property
        self._cEnd      = 0x1100    #Element end

    def __repr__(self):
        print 'Box element'
        print 'layer:             ' , self.layer
        print 'boxtype:           ' , self.boxtype
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
            raise ValueError('GDSII_Box.layer : This parameter must range from 0 to 255')
        self._layer = val
        
    @property
    def boxtype(self):
        '''
        boxtype : integer from 0 to 255
            The boxtype number for this boundary element
        '''
        return self._boxtype
        
    @boxtype.setter
    def boxtype(self, val):
        if val < 0 or val >= 256:
            raise ValueError('GDSII_Box.boxtype : This parameter must range from 0 to 255')
        self._boxtype = val
        
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
            raise TypeError('GDSII_Box.xy : This parameter must be of type numpy.ndarray')
        if not val.size in [8,10]:
            raise ValueError('GDSII_Box.xy : This parameter must have 10 elements')
        if not all(val[0:2] == val[-2:]):
            val = np.append(val,val[0:2],axis=0)
        self._xy = val

    def setBox(self, xy, layer = 0, boxtype = 0):
        '''
        setBox(xy, layer=0, boxtype=0)
        
        Adds a box element
        
        Parameters
        ----------
        xy : numpy.ndarray of type numpy.int32 or a list of integers
            An array containing the verticies of a box in the form
            [x1 y1 x2 y2 x3 y3 x4 y4 x1 y1]
        layer : integer from 0 to 255
            The layer number
        boxtype : integer from 0 to 255
            The boxtype number
        '''
        self.xy = xy
        self.layer = layer
        self.boxtype = boxtype

    @property
    def cBox(self):
        '''
        cBox : 0x2D00
            Command code for boundary element begin
        '''
        return self._cBox
    
    @property
    def cLayer(self):
        '''
        cLayer : 0x0D02
            Command code for layer property
        '''
        return self._cLayer
        
    @property
    def cBoxtype(self):
        '''
        cBoxtype : 0x2E02 
            Command code for boxtype property
        '''
        return self._cBoxtype
    
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
            Box
            ELFLAGS (optional)
            PLEX (optional)
            Layer
            Datatype
            XY
        '''
        self.recordClear()
        
        #Box start
        self.record = self.dec2byte(4)
        self.record = self.dec2byte(self.cBox)
        
        #Define Layer
        self.record = self.dec2byte(6)
        self.record = self.dec2byte(self.cLayer)
        self.record = self.dec2byte(self.layer)
        
        #Define boxtype
        self.record = self.dec2byte(6)
        self.record = self.dec2byte(self.cBoxtype)
        self.record = self.dec2byte(self.boxtype)

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
        if self.byte2dec(record[self.opCodePointer]) == self.cBox:
            self.pointer += 4
        else:
            raise ValueError('GDSII_Box.readRecord() : The record is not a boundary element')
            
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
            raise ValueError('GDSII_Box.readRecord() : The layer number is not defined')
        
        #Boxtype
        if self.byte2dec(record[self.opCodePointer]) == self.cBoxtype:
            self.boxtype = self.byte2dec(record[[self.pointer+4,self.pointer+5]])
            self.pointer += 6
        else:
            raise ValueError('GDSII_Box.readRecord() : The boxtype number is not defined')
        
        #XY
        if self.byte2dec(record[self.opCodePointer]) == self.cXY:
            length = self.byte2dec(record[self.pointer:self.pointer+2])-4
            self.pointer += 4
            tmp = np.zeros(length/4,dtype=np.int32)
            index = 0
            for i in range(self.pointer,self.pointer+length,4):
                tmp[index] = self.byte2dec(record[i:i+4])
                index += 1
            self.xy = tmp
            self.pointer += length

def test():
    a = GDSII_Box()
    a.setBox([0,0,0,100,100,100,100,0,0,0],2,1)
    a.genRecord()
    print a
    b = GDSII_Box()
    b.readRecord(a.record)
    print b
    

if __name__ == '__main__':
    test()
