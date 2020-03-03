#!/usr/bin/env ipython

import numpy as np
import re
import datetime as dt
from GDSII import GDSII
from GDSII_ARef import GDSII_ARef
from GDSII_SRef import GDSII_SRef
from GDSII_Boundary import GDSII_Boundary
from GDSII_Text import GDSII_Text
from GDSII_Path import GDSII_Path
from GDSII_Box import GDSII_Box
from GDSII_Node import GDSII_Node

class GDSII_Structure(GDSII):
    '''
    GDSII_Structure class : subclass of GDSII
    
    GDSII Stream file format release 6.0
    Structure record
    
    The structure record is a container for all element records.  A structure
    is called a cell among the CAD/EDS community.  Once a cell is defined,
    it can be referenced in the layout.  Structure references can be nested up
    to 32 levels.  Structures and referencing is important because it enables
    data compression.  For example, in the GDSII format, by replacing each
    repeated polygon (boundary element) by a cell containing the polygon and
    multiple calls to the cell, the file can be compressed 7x.  The
    compression is significantly more significant if the polygons are arranged
    in an array.
    
    The functions of this class are:
       setName             =   Set the name of the cell
       addBoundary         =   Adds a boundary element
       addSRef             =   Adds a cell reference element
       addARef             =   Adds an array of cell reference element
       addPath             =   Adds a path element
       addText             =   Adds a text element
       addNode             =   Adds a node element
       genRecord           =   Generate the record binary
       readRecord          =   Reads a structure record
       
    Long Chang, UH, May 2013
    '''

    def __init__(self, structureName='UHNano'):
        super(GDSII_Structure,self).__init__()
        self._dom = self.getDate()
        self._doa = self.getDate()
        self._structureName = structureName
        self._aref = []
        self._sref = []
        self._boundary = []
        self._path = []
        self._box = []
        self._node = []
        self._text = []
        
        self._cStructure        = 0x0502    #Structure begin
        self._cStructureName    = 0x0606    #Structure name
        self._cStructureEnd     = 0x0700    #Structure end
        self._cBoundary         = 0x0800    #Boundary element begin
        self._cSRef             = 0x0A00    #Structure reference element begin
        self._cARef             = 0x0B00    #Array reference element begin
        self._cText             = 0x0C00    #Text element begin
        self._cBox              = 0x2D00    #Box element begin
        self._cNode             = 0x1500    #Node element begin
        self._cPath             = 0x0900    #Path element begin
        self._cElementEnd       = 0x1100    #Element end

    def __repr__(self):
        print 'Structure record'
        print 'structureName:     ' , self.structureName
        print 'sref:              ' , len(self.sref)
        print 'aref:              ' , len(self.aref)
        print 'boundary:          ' , len(self.boundary)
        print 'path:              ' , len(self.path)
        print 'text:              ' , len(self.text)
        print 'box:               ' , len(self.box)
        print 'node:              ' , len(self.node)
        return ''

    @property
    def dom(self):
        '''
        dom : list of 6 integers
            Date of modification
        '''
        return self._dom
    
    @dom.setter
    def dom(self, val):
        if not isinstance(val,list):
            raise TypeError('GDSII_Structure.dom : This parameter must be a list of integers')
        if not len(val) == 6:
            raise TypeError('GDSII_Structure.dom : This parameter must have 6 elements')
        self._dom = val
        
    @property
    def doa(self):
        '''
        doa : list of 6 integers
            Date of access
        '''
        return self._doa
    
    @doa.setter
    def doa(self, val):
        if not isinstance(val,list):
            raise TypeError('GDSII_Structure.doa : This parameter must be a list of integers')
        if not len(val) == 6:
            raise TypeError('GDSII_Structure.doa : This parameter must have 6 elements')
        self._doa = val

    @property
    def structureName(self):
        '''
        structureName : string
            Name of the cell to reference
            Up to 32 characters
            Characters must be from the set [A-Z,a-z,0-9,_,?,$]
        '''
        return self._structureName

    @structureName.setter
    def structureName(self, val):
        if not isinstance(val,str):
            raise TypeError('GDSII_Structure.structureName : This parameter must be of type str')
        if len(val) > 32:
            raise ValueError('GDSII_Structure.structureName : This parameter cannot be longer than 32 characters')
        regex = re.compile('[\W^?^$]')
        if not regex.search(val) == None:
            raise ValueError('GDSII_Structure.structureName : This parameter must contain only the following characters: A-Z, a-z, 0-9, _, ? and $')
        self._structureName = val   
        
    @property
    def aref(self):
        '''
        aref : list of GDSII_ARef objects
            A list of array of structure references
        '''
        return self._aref
    
    @aref.setter
    def aref(self,val):
        if not isinstance(val,GDSII_ARef):
            raise('GDSII_Structure.aref : This parameter must be an instance of GDSII_ARef')
        self._aref.append(val)
        
    @property
    def sref(self):
        '''
        sref : list of GDSII_SRef objects
            A list of structure references
        '''
        return self._sref
    
    @sref.setter
    def sref(self,val):
        if not isinstance(val,GDSII_SRef):
            raise('GDSII_Structure.sref : This parameter must be an instance of GDSII_SRef')
        self._sref.append(val)
        
    @property
    def boundary(self):
        '''
        boundary : list of GDSII_Boundary objects
            A list of array of boundary elements
        '''
        return self._boundary
    
    @boundary.setter
    def boundary(self,val):
        if not isinstance(val,GDSII_Boundary):
            raise('GDSII_Structure.boundary : This parameter must be an instance of GDSII_Boundary')
        self._boundary.append(val)

    @property
    def text(self):
        '''
        text : list of GDSII_Text objects
            A list of array of structure references
        '''
        return self._text
    
    @text.setter
    def text(self,val):
        if not isinstance(val,GDSII_Text):
            raise('GDSII_Structure.text : This parameter must be an instance of GDSII_Text')
        self._text.append(val)

    @property
    def path(self):
        '''
        path : list of GDSII_Path objects
            A list of path elements
        '''
        return self._path
    
    @path.setter
    def path(self,val):
        if not isinstance(val,GDSII_Path):
            raise('GDSII_Structure.path : This parameter must be an instance of GDSII_Path')
        self._path.append(val)
        
    @property
    def box(self):
        '''
        box : list of GDSII_Box objects
            A list of box elements
        '''
        return self._box
    
    @box.setter
    def box(self,val):
        if not isinstance(val,GDSII_Box):
            raise('GDSII_Structure.box : This parameter must be an instance of GDSII_Box')
        self._box.append(val)
        
    @property
    def node(self):
        '''
        node : list of GDSII_Node objects
            A list of node elements
        '''
        return self._node
    
    @node.setter
    def node(self,val):
        if not isinstance(val,GDSII_Node):
            raise('GDSII_Structure.node : This parameter must be an instance of GDSII_Node')
        self._node.append(val)

    @property
    def cStructure(self):
        '''
        cStructure : 0x0502
            Command code for structure begin
        '''
        return self._cStructure
    
    @property
    def cStructureName(self):
        '''
        cStructureName : 0x0606
            Command code for structure name
        '''
        return self._cStructureName
        
    @property
    def cStructureEnd(self):
        '''
        cStructureEnd : 0x0700
            Command code for structure end
        '''
        return self._cStructureEnd
        
    @property
    def cBoundary(self):
        '''
        cBoundary : 0x0800
            Command code for boundary element begin
        '''
        return self._cBoundary
        
    @property
    def cSRef(self):
        '''
        cSRef : 0x0A00
            Command code for structure reference element begin
        '''
        return self._cSRef
        
    @property
    def cARef(self):
        '''
        cARef : 0x0B00
            Command code for array reference element begin
        '''
        return self._cARef
        
    @property
    def cText(self):
        '''
        cText : 0x0C00
            Command code for text element begin
        '''
        return self._cText
        
    @property
    def cBox(self):
        '''
        cBox : 0x2D00
            Command code for box element begin
        '''
        return self._cBox
        
    @property
    def cNode(self):
        '''
        cNode : 0x1500
            Command code for node element begin
        '''
        return self._cNode
        
    @property
    def cPath(self):
        '''
        cPath : 0x0900
            Command code for path element begin
        '''
        return self._cPath
        
    @property
    def cElementEnd(self):
        '''
        cElementEnd : 0x1100
            Command code for element end
        '''
        return self._cElementEnd

    def getDate(self):
        '''
        getDate()
        
        Returns the time and date as a list
        
        Returns
        -------
        out : list of integers
            The current date and time in the form:
            [year month day hour minute second]
        '''
        tmp = dt.datetime.now()
        return [tmp.year,tmp.month,tmp.day,tmp.hour,tmp.minute,tmp.second]
        
    def addARef(self, structureName, xy, pitchX, pitchY, nX, nY, xRot = 0, yRot = 0, reflection = 0, mag = 1, angle = 0):
        '''
        setARef(structureName, xy, pitchX, pitchY, nX, nY, xRot = 0, yRot = 0, reflection = 0, mag = 1, angle = 0)
        
        Adds an array reference element
        
        Parameters
        ----------
        structureName : string
            Name of the cell to reference
            Up to 32 characters
            Characters must be from the set [A-Z,a-z,0-9,_,?,$]
        xy : numpy.ndarray of type numpy.int32 with 2 elements or list of 2 integer elements
            The origin, [x y], of the array reference
        pitchX : integer
            Array pitch or step along X
        pitchY : integer
            Array pitch or step along Y
        nX : integer
            Array repeats along X
        nY : integer
            Array repeats along Y
        xRot : float
            Array x angle in units of [degrees]
        yRot : float
            Array y angle in units of [degrees]
        reflection : integer from [0,1]
            Reflection enable for reflection about the X axis
        mag : float
            Magnification factor used to scaled the referenced structure
        angle : float
            Angle in units of [degrees] used to rotate the referenced structure
            counterclockwise about the origin
        '''
        tmp = GDSII_ARef()
        tmp.setARef(structureName, xy, pitchX, pitchY, nX, nY, xRot, yRot, reflection, mag, angle)
        self.aref = tmp
    
    def addSRef(self, structureName, xy, reflection = 0, mag = 1, angle = 0):
        '''
        addARef(structureName, xy, reflection = 0, mag = 1, angle = 0)
        
        Adds an structure reference element
        
        Parameters
        ----------
        structureName : string
            Name of the cell to reference
            Up to 32 characters
            Characters must be from the set [A-Z,a-z,0-9,_,?,$]
        xy : numpy.ndarray of type numpy.int32 with 2 elements or list of 2 integer elements
            The origin, [x y], of the structure reference
        reflection : integer from [0,1]
            Reflection enable for reflection about the X axis
        mag : float
            Magnification factor used to scaled the referenced structure
        angle : float
            Angle in units of [degrees] used to rotate the referenced structure
            counterclockwise about the origin
        '''
        tmp = GDSII_SRef()
        tmp.setSRef(structureName, xy, reflection, mag, angle)
        self.sref = tmp
        
    def addBoundary(self, xy, layer=0, datatype=0):
        '''
        addBoundary(xy, layer=0, datatype=0)
        
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
        tmp = GDSII_Boundary()
        tmp.setBoundary(xy, layer, datatype)
        self.boundary = tmp
        
    def addText(self, text, xy, layer=0, texttype=0, presentation = None, pathtype = None, width = None, reflection = 0, mag = 1, angle = 0):
        '''
        addText(xy, layer=0, texttype=0)
        
        Adds a text element
        
        Parameters
        ----------
        text : string
            A text string
        xy : numpy.ndarray of type numpy.int32 or a list of integers
            An array containing the verticies of a polygon in the form
            [x1 y1 x2 y2 ... xn yn x1 y1]
        layer : integer from 0 to 255
            The layer number
        texttype : integer from 0 to 255
            The texttype number
        presentation : integer
            Specifies the font in bits
                Bit Number (0-15)  
                10-11               Specify Font
                12-13               Vertical presentation
                                        0   Top
                                        1   Middle
                                        2   Bottom
                14-15               Horizontal presentation
                                        0   Top
                                        1   Middle
                                        2   Bottom
        pathtype : integer from the set [0,1,2]
            Describe the nature of the text segment ends
                0   Square ends at text terminal
                1   Rounded ends at text terminal
                2   Square ends that overlap terminals by one-half the width
        width : integer
            Defines the width of the text.  If width is negative, it will be
            independent of any structure scaling
        reflection : integer from [0,1]
            Reflection enable for reflection about the X axis
        mag : float
            Magnification factor used to scaled the referenced structure
        angle : float
            Angle in degrees counterclockwise used to rotate the referenced
            structure about the origin
        '''
        tmp = GDSII_Text()
        tmp.setText(text, xy, layer, texttype)
        self.text = tmp

    def addPath(self, xy, layer=0, datatype=0, width=None, pathtype=None):
        '''
        addPath(xy, layer=0, datatype=0, width=None, pathtype=None)
        
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
        tmp = GDSII_Path()
        tmp.setPath(xy, layer, datatype, width, pathtype)
        self.path = tmp
        
    def addBox(self, xy, layer=0, boxtype=0):
        '''
        addBox(xy, layer=0, boxtype=0)
        
        Adds a boundary element
        
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
        tmp = GDSII_Box()
        tmp.setBox(xy, layer, boxtype)
        self.box = tmp
        
    def addNode(self, xy, layer=0, nodetype=0):
        '''
        addNode(xy, layer=0, nodetype=0)
        
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
        tmp = GDSII_Node()
        tmp.setNode(xy, layer, nodetype)
        self.node = tmp

    def genRecord(self):
        '''
        genRecord()
        
        Generates the structure record binary
        
        Description
        -----------
        The structure record is specified by records in the following order:
            Structure
            StructureName
            Boundary Element    (optional)
            SRef element        (optional)
            ARef element        (optional)
            Path element        (optional)
            Text element        (optional)
            Box element         (optional)
            Node element        (optional)
        '''
        self.recordClear()    
        
        #Structure start
        self.record = self.dec2byte(28)
        self.record = self.dec2byte(self.cStructure)
        for i in self.dom:
            self.record = self.dec2byte(i)
        for i in self.doa:
            self.record = self.dec2byte(i)

        #Define structure name
        if len(self.structureName)%2 == 1:
            self.record = self.dec2byte(len(self.structureName)+5)
        else:
            self.record = self.dec2byte(len(self.structureName)+4)
        self.record = self.dec2byte(self.cStructureName)
        self.record = np.array([ord(i) for i in self.structureName],dtype=np.uint8)
        if len(self.structureName)%2 == 1:
            self.record = np.zeros(1,dtype=np.uint8)
        
        #Add boundary elements
        for i in self.boundary:
            i.genRecord()
            self.record = i.record
        
        #Add sref elements
        for i in self.sref:
            i.genRecord()
            self.record = i.record
            
        #Add aref elements
        for i in self.aref:
            i.genRecord()
            self.record = i.record
            
        #Add path elements
        for i in self.path:
            i.genRecord()
            self.record = i.record
            
        #Add text elements
        for i in self.text:
            i.genRecord()
            self.record = i.record
            
        #Add box elements
        for i in self.box:
            i.genRecord()
            self.record = i.record
            
        #Add node elements
        for i in self.node:
            i.genRecord()
            self.record = i.record
            
        #Structure end
        self.record = self.dec2byte(4)
        self.record = self.dec2byte(self.cStructureEnd)
        
        self.recordClip()
            
    def readRecord(self, record):
        '''
        readRecord(record)
        
        Reads the boundary record and updates the boundary element parameters
        '''
        
        self.pointer = 0
        
        #Check if record is a structure record
        if self.byte2dec(record[self.opCodePointer]) == self.cStructure:
            self.dom[0] = self.byte2dec(record[self.pointer+4:self.pointer+6])
            self.dom[1] = self.byte2dec(record[self.pointer+6:self.pointer+8])
            self.dom[2] = self.byte2dec(record[self.pointer+8:self.pointer+10])
            self.dom[3] = self.byte2dec(record[self.pointer+10:self.pointer+12])
            self.dom[4] = self.byte2dec(record[self.pointer+12:self.pointer+14])
            self.dom[5] = self.byte2dec(record[self.pointer+14:self.pointer+16])
            self.doa[0] = self.byte2dec(record[self.pointer+16:self.pointer+18])
            self.doa[1] = self.byte2dec(record[self.pointer+18:self.pointer+20])
            self.doa[2] = self.byte2dec(record[self.pointer+20:self.pointer+22])
            self.doa[3] = self.byte2dec(record[self.pointer+22:self.pointer+24])
            self.doa[4] = self.byte2dec(record[self.pointer+24:self.pointer+26])
            self.doa[5] = self.byte2dec(record[self.pointer+26:self.pointer+28])
            self.pointer += 28
        else:
            raise ValueError('GDSII_Structure.readRecord() : The record is not a structure record')
            
        #Structure name
        if self.byte2dec(record[self.opCodePointer]) == self.cStructureName:
            length = self.byte2dec(record[self.pointer:self.pointer+2])
            if record[self.pointer+length-1] == 0:
                self.structureName = ''.join([chr(i) for i in record[self.pointer+4:self.pointer+length-1]])
            else:
                self.structureName = ''.join([chr(i) for i in record[self.pointer+4:self.pointer+length]])
            self.pointer += length
        else:
            raise ValueError('GDSII_Structure.readRecord() : The structure name is not defined')
        
        #Elements
        while not self.byte2dec(record[self.opCodePointer]) == self.cStructureEnd:
            #Retrieve one element record
            tp = self.pointer
            tc = [tp+2,tp+3]
            while not self.byte2dec(record[tc]) == self.cElementEnd:
                tp += self.byte2dec(record[tp:tp+2])
                tc = [tp+2,tp+3]
            tp += 4
            
            elementType = self.byte2dec(record[self.opCodePointer])
            elementRecord = record[self.pointer:tp]
            
            #Read the element record
            if elementType == self.cBoundary:
                E = GDSII_Boundary()
                E.readRecord(elementRecord)
                self.boundary = E
            elif elementType == self.cSRef:
                E = GDSII_SRef()
                E.readRecord(elementRecord)
                self.sref = E
            elif elementType == self.cARef:
                E = GDSII_ARef()
                E.readRecord(elementRecord)
                self.aref = E
            elif elementType == self.cPath:
                E = GDSII_Path()
                E.readRecord(elementRecord)
                self.path = E
            elif elementType == self.cText:
                E = GDSII_Text()
                E.readRecord(elementRecord)
                self.text = E
            elif elementType == self.cBox:
                E = GDSII_Box()
                E.readRecord(elementRecord)
                self.box = E
            elif elementType == self.cNode:
                E = GDSII_Node()
                E.readRecord(elementRecord)
                self.node = E
            
            #Point to next element
            self.pointer = tp
            

def test():
    a = GDSII_Structure('doseArray');
    a.addBoundary([0,0,0,5,5,5,5,0],2,1);
    a.addBoundary([10,0,10,5,15,5,15,0],2,2);
    a.addBoundary([20,0,20,5,25,5,25,0],2,3);
    a.addBoundary([0,10,0,15,5,15,5,10],2,4);
    a.addBoundary([10,10,10,15,15,15,15,10],2,5);
    a.addBoundary([20,10,20,15,25,15,25,10],2,6);
    a.addBoundary([0,20,0,25,5,25,5,20],2,7);
    a.addBoundary([10,20,10,25,15,25,15,20],2,8);
    a.addBoundary([20,20,20,25,25,25,25,20],2,9);
    a.addText('Hello',xy=[0,0])
    a.addPath([0,0,1,1,2,2],0,0)
    a.addBox([0,0,0,10,10,10,10,0,0,0],0,0)
    a.addNode([0,0,20,20],255,255)
    a.addSRef('sref',[15,15])
    a.addARef('aref',[30,30],100,100,10,10)
    a.genRecord()
    b = GDSII_Structure()
    b.readRecord(a.record)
    print a
    print b
    

if __name__ == '__main__':
    test()
