#!/usr/bin/env ipython

import numpy as np
from GDSII import GDSII

class GDSII_Path(GDSII):
    '''
    GDSII_Path class : subclass of GDSII
    
    GDSII Stream file format release 6.0
    Path Element
    
    The path element is used to specify lines.  
    
    The functions of this class are:
       setPath         =   Set the path
       genRecord       =   Generate the record binary
       readRecord      =   Reads a path element record

    Long Chang, UH, May 2013
    '''

    def __init__(self):
        super(GDSII_Path,self).__init__()
        self._layer = 0
        self._datatype = 0
        self._pathtype = None
        self._width = None
        self._xy = np.array([0,0],dtype=np.int32)
        
        self._cPath     = 0x0900    #Path element begin
        self._cELFLAG   = 0x2601    #ELFLAG property (optional)
        self._cPLEX     = 0x2F03    #PLEX property (optional)
        self._cPathtype = 0x2102    #Pathtype property
        self._cWidth    = 0x0F03    #Width property
        self._cLayer    = 0x0D02    #Layer property
        self._cDatatype = 0x0E02    #Datatype property
        self._cXY       = 0x1003    #XY property
        self._cEnd      = 0x1100    #Element end

    def __repr__(self):
        print 'Path element'
        print 'layer:             ' , self.layer
        print 'datatype:          ' , self.datatype
        print 'pathtype:          ' , self.pathtype
        print 'width:             ' , self.width
        print 'xy:                ' , self.xy
        return ''

    @property
    def layer(self):
        '''
        layer : integer from 0 to 255
            The layer number for this path element
        '''
        return self._layer
        
    @layer.setter
    def layer(self, val):
        if val < 0 or val > 256:
            raise ValueError('GDSII_Path.layer : This parameter must range from 0 to 255')
        self._layer = val

    @property
    def pathtype(self):
        '''
        pathtype : integer from the set [0,1,2]
            Describe the nature of the path segment ends
                0   Square ends at path terminal
                1   Rounded ends at path terminal
                2   Square ends that overlap terminals by one-half the width
        '''
        return self._pathtype
        
    @pathtype.setter
    def pathtype(self, val):
        if not val in [None,0,1,2]:
            raise ValueError('GDSII_Path.pathtype : This parameter must be in the set [0,1,2]')
        self._pathtype = val
        
    @property
    def width(self):
        '''
        width : integer
            Defines the width of the path.  If width is negative, it will be
            independent of any structure scaling
        '''
        return self._width
        
    @width.setter
    def width(self, val):
        if not val == None and not val == 0:
            raise ValueError('GDSII_Path.width : This parameter can not be 0')
        self._width = val
    
    @property
    def datatype(self):
        '''
        datatype : integer from 0 to 255
            The datatype number for this path element
        '''
        return self._datatype
        
    @datatype.setter
    def datatype(self, val):
        if val < 0 or val >= 256:
            raise ValueError('GDSII_Path.datatype : This parameter must range from 0 to 255')
        self._datatype = val
        
    @property
    def xy(self):
        '''
        xy : numpy.ndarray of type numpy.int32
            An array containing the verticies of the path in the form
            [x1 y1 x2 y2 ... xn yn]
        '''
        return self._xy
        
    @xy.setter
    def xy(self, val):
        if isinstance(val,list):
            val = np.array(val,dtype=np.int32)
        elif not isinstance(val,np.ndarray):
            raise TypeError('GDSII_Path.xy : This parameter must be of type numpy.ndarray')
        if not val.size%2 == 0:
            raise ValueError('GDSII_Path.xy : This parameter must have an even number of elements')
        self._xy = val

    def setPath(self, xy, layer = 0, datatype = 0, width = None, pathtype = None):
        '''
        setPath(xy, layer = 0, datatype = 0, width = None, pathtype = None)
        
        Adds a path element
        
        Parameters
        ----------
        xy : numpy.ndarray of type numpy.int32 or a list of integers
            An array containing the verticies of a polygon in the form
            [x1 y1 x2 y2 ... xn yn x1 y1]
        layer : integer from 0 to 255
            The layer number
        datatype : integer from 0 to 255
            The datatype number
        width : integer (nonzero)
            Width of the path
        pathtype : integer from the set [0,1,2]
            Describe the nature of the path segment ends
                0   Square ends at path terminal
                1   Rounded ends at path terminal
                2   Square ends that overlap terminals by one-half the width
        '''
        self.xy = xy
        self.layer = layer
        self.datatype = datatype
        self.width = width
        self.pathtype = pathtype

    @property
    def cPath(self):
        '''
        cPath : 0x0800
            Command code for path element begin
        '''
        return self._cPath
    
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
    def cWidth(self):
        '''
        cWidth : 0x0F03
            Command code for width property
        '''
        return self._cWidth    
    
    @property
    def cPathtype(self):
        '''
        cPathtype : 0x2102
            Command code for pathtype property
        '''
        return self._cPathtype    
    
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
        
        Generates the path element binary
        
        Description
        -----------
        The path element is specified by records in thefollowing order:
            Path
            ELFLAGS     (optional)
            PLEX        (optional)
            Layer
            Datatype
            Pathtype    (optional)
            Width       (optional)
            XY
        '''
        self.recordClear()
        
        #Path start
        self.record = self.dec2byte(4)
        self.record = self.dec2byte(self.cPath)
        
        #Define Layer
        self.record = self.dec2byte(6)
        self.record = self.dec2byte(self.cLayer)
        self.record = self.dec2byte(self.layer)
        
        #Define datatype
        self.record = self.dec2byte(6)
        self.record = self.dec2byte(self.cDatatype)
        self.record = self.dec2byte(self.datatype)
        
        #Define pathtype
        if not self.pathtype == None:
            self.record = self.dec2byte(6)
            self.record = self.dec2byte(self.cPathtype)
            self.record = self.dec2byte(self.pathtype)
        
        #Define width
        if not self.width == None:
            self.record = self.dec2byte(6)
            self.record = self.dec2byte(self.cWidthtype)
            self.record = self.dec2byte(self.widthtype)

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
        
        Reads the path record and updates the path element parameters
        '''
        
        self.pointer = 0
        
        #Check if record is a path element
        if self.byte2dec(record[self.opCodePointer]) == self.cPath:
            self.pointer += 4
        else:
            raise ValueError('GDSII_Path.readRecord() : The record is not a path element')
            
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
            raise ValueError('GDSII_Path.readRecord() : The layer number is not defined')
        
        #Datatype
        if self.byte2dec(record[self.opCodePointer]) == self.cDatatype:
            self.datatype = self.byte2dec(record[[self.pointer+4,self.pointer+5]])
            self.pointer += 6
        else:
            raise ValueError('GDSII_Path.readRecord() : The datatype number is not defined')
        
        #Pathtype
        if self.byte2dec(record[self.opCodePointer]) == self.cPathtype:
            self.pathtype = self.byte2dec(record[[self.pointer+4,self.pointer+5]])
            self.pointer += 6
            
        #Width
        if self.byte2dec(record[self.opCodePointer]) == self.cWidth:
            self.width = self.byte2dec(record[[self.pointer+4,self.pointer+5]])
            self.pointer += 6
        
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
    a = GDSII_Path()
    a.setPath([0,0,100,100,200,200,300,300],2,1)
    a.genRecord()
    print a
    b = GDSII_Path()
    b.readRecord(a.record)
    print b

if __name__ == '__main__':
    test()
