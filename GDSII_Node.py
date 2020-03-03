#!/usr/bin/env ipython

import numpy as np
from GDSII import GDSII

class GDSII_Node(GDSII):
    '''
    GDSII_Node class : subclass of GDSII
    
    GDSII Stream file format release 6.0
    Node Element
    
    The node element is used to specify electrical nets.  Up to 50 points can
    be used to specify the vertices on the electrical net.  The information in
    this element is not graphical and does not affect the manufactured
    circuit.  It is for other CAD systems that use topological information.
    
    The functions of this class are:
       setNode         =   Set the node
       genRecord       =   Generate the record binary
       readRecord      =   Reads a node element record
       
    Long Chang, UH, May 2013
    '''

    def __init__(self):
        super(GDSII_Node,self).__init__()
        self._layer = 0
        self._nodetype = 0
        self._xy = np.array([0,0],dtype=np.int32)
        
        self._cNode     = 0x1500    #Node element begin
        self._cELFLAG   = 0x2601    #ELFLAG property (optional)
        self._cPLEX     = 0x2F03    #PLEX property (optional)
        self._cLayer    = 0x0D02    #Layer property
        self._cNodetype = 0x2A02    #Nodetype property
        self._cXY       = 0x1003    #XY property
        self._cEnd      = 0x1100    #Element end

    def __repr__(self):
        print 'Node element'
        print 'layer:             ' , self.layer
        print 'nodetype:          ' , self.nodetype
        print 'xy:                ' , self.xy
        return ''

    @property
    def layer(self):
        '''
        layer : integer from 0 to 255
            The layer number for this node element
        '''
        return self._layer
        
    @layer.setter
    def layer(self, val):
        if val < 0 or val > 256:
            raise ValueError('GDSII_Node.layer : This parameter must range from 0 to 255')
        self._layer = val
        
    @property
    def nodetype(self):
        '''
        nodetype : integer from 0 to 255
            The nodetype number for this node element
        '''
        return self._nodetype
        
    @nodetype.setter
    def nodetype(self, val):
        if val < 0 or val >= 256:
            raise ValueError('GDSII_Node.nodetype : This parameter must range from 0 to 255')
        self._nodetype = val
        
    @property
    def xy(self):
        '''
        xy : numpy.ndarray of type numpy.int32
            An array containing the verticies of an electrical net in the form
            [x1 y1 x2 y2 ... x50 y50]
        '''
        return self._xy
        
    @xy.setter
    def xy(self, val):
        if isinstance(val,list):
            val = np.array(val,dtype=np.int32)
        elif not isinstance(val,np.ndarray):
            raise TypeError('GDSII_Node.xy : This parameter must be of type numpy.ndarray')
        if val.size > 100:
            raise ValueError('GDSII_Node.xy : This parameter must have no more than 100 elements or 50 vertices')
        if not val.size%2 == 0:
            raise ValueError('GDSII_Node.xy : This parameter must have an even number of elements')
        self._xy = val

    def setNode(self, xy, layer = 0, nodetype = 0):
        '''
        setNode(xy, layer = 0, nodetype = 0)
        
        Adds a node element
        
        Parameters
        ----------
        xy : numpy.ndarray of type numpy.int32 or a list of integers
            An array containing the verticies of an electrical net in the form
            [x1 y1 x2 y2 ... x50 y50]
        layer : integer from 0 to 255
            The layer number 
        nodetype : integer from 0 to 255
            The nodetype number
        '''
        self.xy = xy
        self.layer = layer
        self.nodetype = nodetype

    @property
    def cNode(self):
        '''
        cNode : 0x1500
            Command code for node element begin
        '''
        return self._cNode
    
    @property
    def cLayer(self):
        '''
        cLayer : 0x0D02
            Command code for layer property
        '''
        return self._cLayer
        
    @property
    def cNodetype(self):
        '''
        cNodetype : 0x2A02
            Command code for nodetype property
        '''
        return self._cNodetype
    
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
        
        Generates the node element binary
        
        Description
        -----------
        The node element is specified by records in thefollowing order:
            Node
            ELFLAGS     (optional)
            PLEX        (optional)
            Layer
            Nodetype
            XY
        '''
        self.recordClear()
        
        #Node start
        self.record = self.dec2byte(4)
        self.record = self.dec2byte(self.cNode)
        
        #Define Layer
        self.record = self.dec2byte(6)
        self.record = self.dec2byte(self.cLayer)
        self.record = self.dec2byte(self.layer)
        
        #Define nodetype
        self.record = self.dec2byte(6)
        self.record = self.dec2byte(self.cNodetype)
        self.record = self.dec2byte(self.nodetype)

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
        
        Reads the node record and updates the node element parameters
        '''
        
        self.pointer = 0
        
        #Check if record is a node element
        if self.byte2dec(record[self.opCodePointer]) == self.cNode:
            self.pointer += 4
        else:
            raise ValueError('GDSII_Node.readRecord() : The record is not a node element')
            
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
            raise ValueError('GDSII_Node.readRecord() : The layer number is not defined')
        
        #Nodetype
        if self.byte2dec(record[self.opCodePointer]) == self.cNodetype:
            self.nodetype = self.byte2dec(record[[self.pointer+4,self.pointer+5]])
            self.pointer += 6
        else:
            raise ValueError('GDSII_Node.readRecord() : The nodetype number is not defined')
        
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
    a = GDSII_Node()
    a.setNode([0,0,1,1,2,2,3,3],2,1)
    a.genRecord()
    print a
    b = GDSII_Node()
    b.readRecord(a.record)
    print b
    

if __name__ == '__main__':
    test()
