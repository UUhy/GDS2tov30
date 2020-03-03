#!/usr/bin/env ipython

import numpy as np
import re
import datetime as dt
import copy
from GDSII import GDSII
from GDSII_Structure import GDSII_Structure

class GDSII_Library(GDSII):
    '''
    GDSII_Library class : subclass of GDSII
    
    GDSII Stream file format release 6.0
    Library record
    
    The library record is a container for all structure records.  The library
    record must contain at least 1 structure records.  Structure records are
    containers for element record(s) such as:  
       boundary
       structure reference
       array of structure reference
       text
       box
       path
       node
    
    The GDSII_Library class supports the following functions:
       setLibrary          =   Set the library name and units
       addStructure        =   Adds a structure to the library
       addBoundary         =   Adds a boundary to a structure
       addARef             =   Adds an array of structure reference to a
                               structure
       addSRef             =   Adds a structure reference to a structure
       addBox              =   Adds a box to a structure
       addPath             =   Adds a path to a structure
       addText             =   Adds a text to a structure
       addNode             =   Adds a node to a structure
       readFile            =   Reads a *.gds file into the library
       writeFile           =   Writes the library into a *.gds file
       genHierarchy        =   Creates a hierarchy tree
           
    Long Chang, UH, May 2013
    '''

    def __init__(self, libraryName = 'UHNano'):
        super(GDSII_Library,self).__init__()
        self._version = 600
        self._dom = self.getDate()
        self._doa = self.getDate()
        self._libraryName = libraryName
        self._userUnit = 0.000001
        self._dbUnit = 1000
        self._unit = 0.000000001              #userUnit/dbUnit
        self._structureName = []
        self._structure = []
        
        self._cVersion          = 0x0002
        self._cLibrary          = 0x0102    #Library begin
        self._cLibraryName      = 0x0206    #Library name
        self._cUnit             = 0x0305    #Library unit
        self._cLibraryEnd       = 0x0400    #Library end
        self._cStructure        = 0x0502    #Structure start
        self._cStructureEnd     = 0x0700    #Structure end

    def __repr__(self):
        print 'Library record'
        print 'libraryName:       ' , self.libraryName
        print 'structure:         ' , len(self.structure)
        print 'structureName:     ' , self.structureName
        return ''

    @property
    def version(self):
        '''
        version : integer (constant)
            GDSII version number
                0       Version 0
                3       Version 3
                4       Version 4
                5       Version 5
                600     Version 6
        '''
        return self._version
        
    @version.setter
    def version(self, val):
        if not val in [0,3,4,5,600]:
            raise ValueError('GDSII_Library.version : This parameter must be in the set [0,3,4,5,600]')
        self._version = val

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
            raise TypeError('GDSII_Library.dom : This parameter must be a list of integers')
        if not len(val) == 6:
            raise TypeError('GDSII_Library.dom : This parameter must have 6 elements')
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
            raise TypeError('GDSII_Library.doa : This parameter must be a list of integers')
        if not len(val) == 6:
            raise TypeError('GDSII_Library.doa : This parameter must have 6 elements')
        self._doa = val

    @property
    def libraryName(self):
        '''
        libraryName : string
            Name of the cell to reference
            Up to 32 characters
            Characters must be from the set [A-Z,a-z,0-9,_,?,$]
        '''
        return self._libraryName

    @libraryName.setter
    def libraryName(self, val):
        if not isinstance(val,str):
            raise TypeError('GDSII_Library.libraryName : This parameter must be of type str')
        if len(val) > 32:
            raise ValueError('GDSII_Library.libraryName : This parameter cannot be longer than 32 characters')
        regex = re.compile('[\W^?^$]')
        if not regex.search(val) == None:
            raise ValueError('GDSII_Library.libraryName : This parameter must contain only the following characters: A-Z, a-z, 0-9, _, ? and $')
        self._libraryName = val

    @property
    def userUnit(self):
        '''
        userUnit : float
            Specify user units in [m]
        '''
        return self._userUnit
    
    @userUnit.setter
    def userUnit(self, val):
        self._userUnit = float(val)
        
    @property
    def dbUnit(self):
        '''
        dbUnit : integer
            Specify number of database units per user unit
        '''
        return self._dbUnit
    
    @dbUnit.setter
    def dbUnit(self, val):
        self._dbUnit = val
        
    @property
    def unit(self):
        '''
        unit : float
        '''
        return self._unit

    @property
    def structure(self):
        '''
        structure : GDSII_Structure
            A list of GDSII_Structure
        '''
        return self._structure

    @structure.setter
    def structure(self, val):
        if not isinstance(val, GDSII_Structure):
            raise TypeError('GDSII_Library.structure : This parameter must be a GDSII_Structure object')
        self._structure.append(val)

    @property
    def structureName(self):
        '''
        structureName : list of string
            Each list element is the name of a structure
            The name may contain up to 32 characters
            Characters must be from the set [A-Z,a-z,0-9,_,?,$]
        '''
        return self._structureName

    @structureName.setter
    def structureName(self, val):
        if not isinstance(val,str):
            raise TypeError('GDSII_Library.structureName : This parameter must be of type str')
        if len(val) > 32:
            raise ValueError('GDSII_Library.structureName : This parameter cannot be longer than 32 characters')
        regex = re.compile('[\W^?^$]')
        if not regex.search(val) == None:
            raise ValueError('GDSII_Library.structureName : This parameter must contain only the following characters: A-Z, a-z, 0-9, _, ? and $')
        if val in self._structureName:
            raise ValueError('GDSII_Library.structureName : A structure with the same name already exist in the library')
        self._structureName.append(val)

    @property
    def cVersion(self):
        '''
        cVersion : 0x0002
            Command code for version
        '''
        return self._cVersion

    @property
    def cLibrary(self):
        '''
        cLibrary : 0x0102
            Command code for library begin
        '''
        return self._cLibrary
        
    @property
    def cLibraryEnd(self):
        '''
        cLibraryEnd : 0x0400
            Command code for library end
        '''
        return self._cLibraryEnd
        
    @property
    def cLibraryName(self):
        '''
        cLibraryName : 0x0206
            Command code for library name
        '''
        return self._cLibraryName
        
    @property
    def cUnit(self):
        '''
        cUnit : 0x0305
            Command code for units
        '''
        return self._cUnit

    @property
    def cStructure(self):
        '''
        cStructure : 0x0502
            Command code for structure begin
        '''
        return self._cStructure
        
    @property
    def cStructureEnd(self):
        '''
        cStructureEnd : 0x0700
            Command code for structure end
        '''
        return self._cStructureEnd
        
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

    def setLibrary(self, libraryName, userUnit = 0.000001, dbUnit = 1000):
        '''
        setLibrary(libraryName, userUnit = 0.001, dbUnit = 1000)
        
        Set the libraray parameters
        
        Parameters
        ----------
        libraryName : string
            Name of the cell to reference
            Up to 32 characters
            Characters must be from the set [A-Z,a-z,0-9,_,?,$]
        userUnit : float
            Specify user units in units of [m]
        dbUnit : integer
            Specify database units
        '''
        self.libraryName = libraryName
        self._userUnit = userUnit
        self._dbUnit = dbUnit

    def addStructure(self, val):
        '''
        addStructure(val)
        
        Adds a structure to the library
        
        Parameters
        ----------
        val : GDSII_Structure or string
            A structure object or structure name
        '''
        if isinstance(val,GDSII_Structure):
            self.structureName = val.structureName
            self.structure = val
        elif isinstance(val,str):
            self.structureName = val
            self.structure = GDSII_Structure(val)
        else:
            raise TypeError('GDSII_Library.addStructure : The input parameter must be either a string or a GDSII_Structure')
        
    def addBoundary(self, structureName, xy, layer=0, datatype=0):
        '''
        addBoundary(structureName, xy, layer=0, datatype=0)
        
        Adds a boundary element to a structure
        
        Parameters
        ----------
        structureName : string
            Name of structure
        xy : numpy.ndarray of type numpy.int32 or a list of integers
            An array containing the verticies of a polygon in the form
            [x1 y1 x2 y2 ... xn yn x1 y1]
        layer : integer from 0 to 255
            The layer number
        datatype : integer from 0 to 255
            The datatype number
        '''
        try:
            self.structure[self.structureName.index(structureName)].addBoundary(xy,layer,datatype)
        except:
            raise ValueError('GDSII_Library.addBoundary() : The structureName does not exist in the library')
    
    def addSRef(self, structureName, referenceName, xy, reflection = 0, mag = 1, angle = 0):
        '''
        addARef(structureName, referenceName, xy, reflection = 0, mag = 1, angle = 0)
        
        Adds an structure reference element to a structure
        
        Parameters
        ----------
        structureName : string
            Name of structure
        referenceName : string
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
        try:
            self.structure[self.structureName.index(structureName)].addSRef(referenceName, xy, reflection, mag, angle)
        except:
            raise ValueError('GDSII_Library.addSRef() : The structureName does not exist in the library')
    
    def addARef(self, structureName, referenceName, xy, pitchX, pitchY, nX, nY, xRot = 0, yRot = 0, reflection = 0, mag = 1, angle = 0):
        '''
        addARef(structureName, referenceName, xy, pitchX, pitchY, nX, nY, xRot = 0, yRot = 0, reflection = 0, mag = 1, angle = 0)
        
        Adds an array reference element to a structure
        
        Parameters
        ----------
        structureName : string
            Name of structure
        referenceName : string
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
        try:
            self.structure[self.structureName.index(structureName)].addARef(referenceName, xy, pitchX, pitchY, nX, nY, xRot, yRot, reflection, mag, angle)
        except:
            raise ValueError('GDSII_Library.addARef() : The structureName does not exist in the library')
    
    def addPath(self, structureName, xy, layer=0, datatype=0, width=None, pathtype=None):
        '''
        addPath(structureName, xy, layer=0, datatype=0, width=None, pathtype=None)
        
        Adds a path element to a structure
        
        Parameters
        ----------
        structureName : string
            Name of structure
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
        try:
            self.structure[self.structureName.index(structureName)].addPath(xy, layer, datatype, width, pathtype)
        except:
            raise ValueError('GDSII_Library.addBoundary() : The structureName does not exist in the library')
    
    def addBox(self, structureName, xy, layer=0, boxtype=0):
        '''
        addBox(structureName, xy, layer=0, boxtype=0)
        
        Adds a box element to a structure
        
        Parameters
        ----------
        structureName : string
            Name of structure
        xy : numpy.ndarray of type numpy.int32 or a list of integers
            An array containing the verticies of a box in the form
            [x1 y1 x2 y2 x3 y3 x4 y4 x1 y1]
        layer : integer from 0 to 255
            The layer number
        boxtype : integer from 0 to 255
            The boxtype number
        '''    
        try:
            self.structure[self.structureName.index(structureName)].addBox(xy, layer, boxtype)
        except:
            raise ValueError('GDSII_Library.addBox() : The structureName does not exist in the library')
    
    def addText(self, structureName, text, xy, layer = 0, texttype = 0, presentation = None, pathtype = None, width = None, reflection = 0, mag = 1, angle = 0):
        '''
        addText(structureName, text, xy, layer = 0, texttype = 0, presentation = None, pathtype = None, width = None, reflection = 0, mag = 1, angle = 0)
        
        Adds a text element to a structure
        
        Parameters
        ----------
        structureName : string
            Name of structure
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
        try:
            self.structure[self.structureName.index(structureName)].addText(text, xy, layer, texttype, presentation, pathtype, width, reflection, mag, angle)
        except:
            raise ValueError('GDSII_Library.addText() : The structureName does not exist in the library')
    
    def addNode(self, structureName, xy, layer = 0, nodetype = 0):
        '''
        addNode(structureName, xy, layer = 0, nodetype = 0)
        
        Adds a node element to a structure
        
        Parameters
        ----------
        structureName : string
            Name of structure
        xy : numpy.ndarray of type numpy.int32 or a list of integers
            An array containing the verticies of an electrical net in the form
            [x1 y1 x2 y2 ... x50 y50]
        layer : integer from 0 to 255
            The layer number 
        nodetype : integer from 0 to 255
            The nodetype number
        '''
        try:
            self.structure[self.structureName.index(structureName)].addNode(xy, layer, nodetype)
        except:
            raise ValueError('GDSII_Library.addNode() : The structureName does not exist in the library')
    
    def genRecord(self):
        '''
        genRecord()
        
        Generates the structure record binary
        
        Description
        -----------
        The structure record is specified by records in the following order:
            Library
            LibraryName
            Units
            StructureRecords
            Boundary Element    (optional)
            SRef element        (optional)
            ARef element        (optional)
            Path element        (optional)
            Text element        (optional)
            Box element         (optional)
            Node element        (optional)
        '''
        self.recordClear()
        
        #Version
        self.record = self.dec2byte(6)
        self.record = self.dec2byte(self.cVersion)
        self.record = self.dec2byte(self.version)
        
        #Library start
        self.record = self.dec2byte(28)
        self.record = self.dec2byte(self.cLibrary)
        for i in self.dom:
            self.record = self.dec2byte(i)
        for i in self.doa:
            self.record = self.dec2byte(i)

        #Define library name
        if len(self.libraryName)%2 == 1:
            self.record = self.dec2byte(len(self.libraryName)+5)
        else:
            self.record = self.dec2byte(len(self.libraryName)+4)
        self.record = self.dec2byte(self.cLibraryName)
        self.record = np.array([ord(i) for i in self.libraryName],dtype=np.uint8)
        if len(self.libraryName)%2 == 1:
            self.record = np.zeros(1,dtype=np.uint8)
        
        #Define units
        self.record = self.dec2byte(20)
        self.record = self.dec2byte(self.cUnit)
        self.record = self.dec2fbin(self.userUnit*self.dbUnit)
        self.record = self.dec2fbin(self.userUnit/self.dbUnit)
        
        #Add structure records
        for i in self.structure:
            i.genRecord()
            self.record = i.record
            
        #Library end
        self.record = self.dec2byte(4)
        self.record = self.dec2byte(self.cLibraryEnd)
        
        self.recordClip()
            
    def readRecord(self, record):
        '''
        readRecord(record)
        
        Reads the boundary record and updates the boundary element parameters
        '''
        
        self.pointer = 0

        #Version
        if self.byte2dec(record[self.opCodePointer]) == self.cVersion:
            self.version = self.byte2dec(record[self.pointer+4:self.pointer+6])
            self.pointer += 6
        else:
            raise ValueError('GDSII_Library.readRecord() : The GDSII version is not defined')
        
        #Library record
        if self.byte2dec(record[self.opCodePointer]) == self.cLibrary:
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
            raise ValueError('GDSII_Library.readRecord() : The record is not a library record')
            
        #Library name
        if self.byte2dec(record[self.opCodePointer]) == self.cLibraryName:
            length = self.byte2dec(record[self.pointer:self.pointer+2])
            if record[self.pointer+length-1] == 0:
                self.libraryName = ''.join([chr(i) for i in record[self.pointer+4:self.pointer+length-1]])
            else:
                self.libraryName = ''.join([chr(i) for i in record[self.pointer+4:self.pointer+length]])
            self.pointer += length
        else:
            raise ValueError('GDSII_Library.readRecord() : The library name is not defined')
        
        #Units
        if self.byte2dec(record[self.opCodePointer]) == self.cUnit:
            umd = self.fbin2dec(record[self.pointer+4:self.pointer+12])
            udd = self.fbin2dec(record[self.pointer+12:self.pointer+20])
            self.userUnit = np.sqrt(umd*udd)
            self.dbUnit = int(np.sqrt(umd/udd))
            self.pointer += 20
        else:
            raise ValueError('GDSII_Library.readRecord() : The GDSII units is not defined')        
        
        #Structures
        while not self.byte2dec(record[self.opCodePointer]) == self.cLibraryEnd:
            #Retrieve one structure record
            tp = self.pointer
            tc = [tp+2,tp+3]
            while not self.byte2dec(record[tc]) == self.cStructureEnd:
                tp += self.byte2dec(record[tp:tp+2])
                tc = [tp+2,tp+3]
            tp += 4
            
            #Read structur record
            S = GDSII_Structure()
            S.readRecord(record[self.pointer:tp])
            self.addStructure(S)
            
            #Point to next structure
            self.pointer = tp

    def readFile(self, filename):
        '''
        readFile(filename)
        
        Reads a GDSII file and populate the library object
        
        Parameters
        ----------
        filename : string
            Name of GDSII file
        '''
        if not isinstance(filename,str):
            raise TypeError('GDSII_Library.readFile() : The filename must be a string')
        if filename[-4:].lower() == '.gds':
            filename = filename[:-4]
        f = open(filename + '.gds','rb')
        record = np.fromfile(f, dtype=np.uint8)
        f.close()
        self.readRecord(record)
        
    def writeFile(self, filename):
        '''
        writeFile(filename)
        
        Writes the library object to a file
        
        Parameters
        ----------
        filename : string
            Name of GDSII file
        '''
        if not isinstance(filename,str):
            raise TypeError('GDSII_Library.readFile() : The filename must be a string')
        if filename[-4:].lower() == '.gds':
            filename = filename[:-4]
        f = open(filename + '.gds','wb')
        self.genRecord()
        f.write(self.record)
        f.close()
           
    def genHierarchyTree(self, structureName):
        '''
        genHierarchyTree(structureName)
        
        Generates the hierarchy tree for the specified struture in the library
        
        Parameters
        ----------
        structureName : string
            name of the structure
        
        Results
        -------
        hierarchyList : list of list of integer
            Each sub-list contains the indices for a branch of the structure 
                hierarchy
            The first index in each list refers to structureName
        branchIndexList : list of NxM numpy.ndarray of dtype numpy.int32
            Each sub-list contain a sets of indices for each branch
            The indices are encoded such that
                -1,-2,-n    refers to an ARef index of  0, 1, n-1
                1,2,n       refers to an SRef index of  0, 1, n-1
        branchRepeatNumber : list of integers
            The repeat number of a branch
            
        Note
        ----
        Maximum number of repeat is 256
        '''
        try:
            nameList, indexList = self.recursiveBranching(structureName,self.structureName.index(structureName))
            hierarchyList, accessList = self.branchDecode(nameList, indexList)
            uniqueHierarchyList = [hierarchyList[0]]
            tmpIndexList = [accessList[0]]
            branchIndexList = []
            branchRepeatNumber = [1]
            uniqueHierarchyList = [hierarchyList[0]]
            for i in range(1,len(hierarchyList)):
                if hierarchyList[i] == hierarchyList[i-1]:
                    branchRepeatNumber[-1] += 1
                    tmpIndexList.append(accessList[i])
                else:            
                    uniqueHierarchyList.append(hierarchyList[i])
                    branchRepeatNumber.append(1)
                    branchIndexList.append(np.array(tmpIndexList,dtype=np.int32))
                    tmpIndexList = [accessList[i]]
            branchIndexList.append(np.array(tmpIndexList,dtype=np.int32))
            
            return uniqueHierarchyList, branchIndexList, branchRepeatNumber
        except:
            raise ValueError('GDSII_Library.genHierarchyTree : The specified cell does not have a tree')
        
    def recursiveBranching(self, referenceName, index):
        '''
        recursiveBranching(referenceName)
        
        Recursively finds the branches of a structure hierarchy
        
        Parameters
        ----------
        referenceName : string
            Name of the first structure in the hierarchy
            
        Results
        -------
        nameList : list of strings
            An encoded list of structure names representing the branches of a 
            hierarchy tree
        indexList : list of integers
            An encoded list of structure indices representing the branches of a 
            hierarchy tree
        typeList : list of reference type
            An encoded list of reference type for the corresponding indexList
            
        Description:
        This method recursively steps through the specified structure and
        generates a list of all referenced structure.  The list is encoded to
        optimize the branching algorithm.  For example, the tree below
                                a   
                            b       c
                         c    c     d
                         d    d
         will result in a list:
         ['a', 'b', 'c', 'd', 'd', 'c', 'c', 'd', 'd', 'c', 'b', 'c', 'd', 'd', 'c', 'a']
         A structure name will always encapsulate all referenced structure.
         A structure name that encapsulates nothing means that it does not
         contain a structure reference.
        '''
        nameList = [referenceName]
        indexList = [index]
        
        #Recursively step through each referenced structure
        for i in range(len(self.structure[self.structureName.index(referenceName)].sref)):
            nameTmp, indexTmp = self.recursiveBranching(self.structure[self.structureName.index(referenceName)].sref[i].referenceName, i+1)
            nameList.extend(nameTmp)
            indexList.extend(indexTmp)
        for i in range(len(self.structure[self.structureName.index(referenceName)].aref)):
            nameTmp, indexTmp = self.recursiveBranching(self.structure[self.structureName.index(referenceName)].aref[i].referenceName, -i-1)
            nameList.extend(nameTmp)
            indexList.extend(indexTmp)
            
        #Add referenceName to the end of the list
        nameList.append(referenceName)
        indexList.append(index)
        
        return nameList, indexList
        
    def branchDecode(self, nameList, indexList):
        '''
        branchDecode(nameList, indexList)
        
        Decodes the name list from the recursiveBranch method
        
        Parameters
        ----------
        nameList : List of strings
            An encoded structure reference name list from the recursiveBranch
            method
            
        indexList : List of integers
            An encoded index list from the recursiveBranch method
            
        Results
        -------
        hierarchyList : A list of a list of integer indices
            Each sub-list is a single branch of the hierarchy tree
            
        accessList : A list of a list of integer indices
            Each sub-list is a code for accessing each branch of the tree
            The first element is the index of the top structure
            The remaining elements are codes that refer to SRef or ARef indices
                to access the referenced structure as described by the 
                hierarchyList
                A positive integer codes for SRef indices
                A negative integer codes for ARef indices
                Since zero cannot be negative, all indices begin with 1
                Example:  SRef[2] will be coded as 3
                          ARef[0] will be coded as -1
        
        Note
        ----
        This method supports only 256 levels of hierarchy or structure nests
        '''
        #Convert a list of structure names to a list of structure indices
        structureIndexList = np.array([self.structureName.index(i) for i in nameList],dtype=np.uint32)
        
        #A list that tracks the branch progression
        tmpStructureIndexList = [structureIndexList[0]]
        tmpAccessIndexList = [indexList[0]]
        #Tracks if the branch is progressing forward (deeper) or backwards
        forward = True
        #A list of completed branches
        hierarchyList = []
        accessList = []
        #Steps through the indexList and extract each branch of the hierarchy
        for i in range(1,len(structureIndexList[1:])):
            if not structureIndexList[i] == tmpStructureIndexList[-1]:
                tmpStructureIndexList.append(structureIndexList[i])
                tmpAccessIndexList.append(indexList[i])
                forward = True
            else:
                if forward:
                    hierarchyList.append(copy.copy(tmpStructureIndexList))
                    accessList.append(copy.copy(tmpAccessIndexList))
                forward = False
                tmpStructureIndexList.pop()
                tmpAccessIndexList.pop()
        return hierarchyList, accessList
        
def test():
#    a = GDSII_Library('libraryTest')
#    a.addStructure('a')
#    a.addStructure('b')
#    a.addStructure('c')
#    a.addStructure('d')
#    a.addStructure('e')
#    a.addStructure('f')
#    a.addBoundary('a',[0,0,0,5,5,5,5,0],2,1)
#    a.addBoundary('a',[10,0,10,5,15,5,15,0],2,2)
#    a.addBoundary('a',[20,0,20,5,25,5,25,0],2,3)
#    a.addBoundary('a',[0,10,0,15,5,15,5,10],2,4)
#    a.addBoundary('a',[10,10,10,15,15,15,15,10],2,5)
#    a.addBoundary('b',[20,10,20,15,25,15,25,10],2,6)
#    a.addBoundary('b',[0,20,0,25,5,25,5,20],2,7)
#    a.addBoundary('b',[10,20,10,25,15,25,15,20],2,8)
#    a.addBoundary('b',[20,20,20,25,25,25,25,20],2,9)
#    a.addText('a','UHNano',xy=[0,0])
#    a.addPath('a',[0,0,1,1,2,2],0,0)
#    a.addBox('a',[0,0,0,10,10,10,10,0,0,0],0,0)
#    a.addNode('a',[0,0,20,20],255,255)
#    a.addSRef('a','b',[0,0])
#    a.addSRef('a','c',[0,0])
#    a.addSRef('a','e',[0,0])
#    a.addSRef('b','c',[0,0])
#    a.addSRef('b','c',[10,10])
#    a.addSRef('c','d',[0,0])
#    a.addSRef('e','b',[0,0])
#    a.addSRef('e','d',[0,0])
#    a.addSRef('e','d',[0,0])
#    a.addSRef('e','d',[0,0])
#    a.addSRef('f','b',[0,0])
#    a.addSRef('f','c',[0,0])
#    a.addSRef('f','d',[0,0])
#    a.genRecord()
#    aHList, abrNum = a.genHierarchyTree('a')
#    b = GDSII_Library()
#    b.readRecord(a.record)
#    
#    print a
#    print aHList
#    print abrNum
#    print b

    c = GDSII_Library('KLayout_Example')    
    c.readFile('KLayout_Example')
    hList, iList, brNum = c.genHierarchyTree('main')
    print c
    print hList
    print brNum
    c.writeFile('GDSII_Write.gds')

if __name__ == '__main__':
    test()
