#!/usr/bin/env ipython

import numpy as np
import re
from GDSII import GDSII

class GDSII_SRef(GDSII):
    '''
    GDSII Stream file format release 6.0
    Structure reference (SRef) Element
    
    The SRef element references a cell and places it at a specified point xy.
    A cell can be referenced before it is defined.
    
    When a cell is referenced it can be subjected to 3 transformation:
    reflection about the x axis, magnification and rotation.  These
    transformations are applied to the cell within its coordinate system.
    Therefore, rotation is centered at the origin, magnification simply scales
    the value of all vertices and reflection mirrors the layout about the x
    axis.
    
    The functions of this class are:
       setSRef         =   Set the structure reference
       genRecord       =   Generate the record binary
       readRecord      =   Reads a structure reference element record
    
    Long Chang, UH, May 2013
    '''

    def __init__(self):
        super(GDSII_SRef,self).__init__()
        self._referenceName = ''
        self._xy = np.array([0,0],dtype=np.int32)
        self._reflection = 0
        self._mag = 1
        self._angle = 0
        self._strans = 0
        
        self._cSRef             = 0x0A00    #Structure reference element begin
        self._cELFLAG           = 0x2601    #ELFLAG property (optional)
        self._cPLEX             = 0x2F03    #PLEX property (optional)
        self._cReferenceName    = 0x1206    #Structure name
        self._cSTrans           = 0x1A01    #Strans property
        self._cMag              = 0x1B05    #Magnification property
        self._cAngle            = 0x1C05    #Angle property
        self._cXY               = 0x1003    #XY property
        self._cEnd              = 0x1100    #Element end

    def __repr__(self):
        print 'Structure reference element'
        print 'referenceName:     ' , self.referenceName
        print 'xy:                ' , self.xy[0] , ',' , self.xy[1]
        print 'reflection:        ' , self.reflection
        print 'mag:               ' , self.mag
        print 'angle:             ' , self.angle
        return ''
        
    @property
    def referenceName(self):
        '''
        referenceName : string
            Name of the cell to reference
            Up to 32 characters
            Characters must be from the set [A-Z,a-z,0-9,_,?,$]
        '''
        return self._referenceName

    @referenceName.setter
    def referenceName(self, val):
        if not isinstance(val,str):
            raise TypeError('GDSII_SRef.referenceName : This parameter must be of type str')
        if len(val) > 32:
            raise ValueError('GDSII_SRef.referenceName : This parameter cannot be longer than 32 characters')
        regex = re.compile('[\W^?^$]')
        if not regex.search(val) == None:
            raise ValueError('GDSII_SRef.referenceName : This parameter must contain only the following characters: A-Z, a-z, 0-9, _, ? and $')
        self._referenceName = val        
        
    @property
    def xy(self):
        '''
        xy : numpy.ndarray of type numpy.int32 with 2 elements or list of 2 integer elements
            The origin, [x y], of the structure reference
        '''
        return self._xy
        
    @xy.setter
    def xy(self, val):
        if isinstance(val,list):
            val = np.array(val,dtype=np.int32)
        elif not isinstance(val,np.ndarray):
            raise TypeError('GDSII_SRef.xy : This parameter must be of type numpy.ndarray')
        if not val.size == 2:
            raise TypeError('GDSII_SRef.xy : This parameter must have only 2 elements')
        self._xy = val
      
    @property
    def reflection(self):
        '''
        reflection : integer from [0,1]
            Reflection enable for reflection about the X axis
        '''
        return self._reflection
        
    @reflection.setter
    def reflection(self, val):
        if not val in [0,1]:
            raise ValueError('GDSII_SRef.reflection : This parameter must be either 0 or 1')
        self._reflection = val
        self._strans = self._reflection*32768 + int(not self._mag == 1)*4 + int(not self._angle == 0)*2
        
    @property
    def mag(self):
        '''
        mag : float
            Magnification factor used to scaled the referenced structure
        '''
        return self._mag
    
    @mag.setter
    def mag(self, val):
        self._mag = val
        self._strans = self._reflection*32768 + int(not self._mag == 1)*4 + int(not self._angle == 0)*2
        
    @property
    def angle(self):
        '''
        angle : float
            Angle in degrees counterclockwise used to rotate the referenced
            structure about the origin
        '''
        return self._angle
        
    @angle.setter
    def angle(self, val):
        self._angle = val
        self._strans = self._reflection*32768 + int(not self._mag == 1)*4 + int(not self._angle == 0)*2
        
    @property
    def strans(self):
        '''
        strans : integer
            Enables the transformation of referenced structure by setting
            specific bits
                Bit Number (0-15)       Transformation Enable
                0                       Reflection about X axis before rotation
                13                      Absolute magnification
                14                      Absolute rotation
                Others                  Set to 0
        '''
        return self._strans
        
    @strans.setter
    def strans(self, val):
        self._strans = val

    def setSRef(self, referenceName, xy, reflection = 0, mag = 1, angle = 0):
        '''
        setARef(referenceName, xy, reflection = 0, mag = 1, angle = 0)
        
        Adds an structure reference element
        
        Parameters
        ----------
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
        self.referenceName = referenceName
        self.xy = xy
        self.reflection = reflection
        self.mag = mag
        self.angle = angle

    @property
    def cSRef(self):
        '''
        cBoundary : 0x0A00
            Command code for structure reference element begin
        '''
        return self._cSRef
    
    @property
    def cReferenceName(self):
        '''
        cReferenceName : 0x1206
            Command code for structure name property
        '''
        return self._cReferenceName
        
    @property
    def cSTrans(self):
        '''
        cSTrans : 0x1A01
            Command code for strans property
        '''
        return self._cSTrans

    @property
    def cMag(self):
        '''
        cMag : 0x1B05
            Command code for the mag property
        '''
        return self._cMag

    @property
    def cAngle(self):
        '''
        cAngle : 0x1C05
            Command code for the angle property
        '''
        return self._cAngle
    
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
        
        Generates the structure reference element binary
        
        Description
        -----------
        The structure reference element is specified by records in the following 
        order:
            SRef
            ELFLAGS         (optional)
            PLEX            (optional)
            ReferenceName   
            STrans          (optional)
            Mag             (optional)
            Angle           (optional)
            XY
        '''
        self.recordClear()
        
        #Structure reference start
        self.record = self.dec2byte(4)
        self.record = self.dec2byte(self.cSRef)
        
        #Define reference structure name
        if len(self.referenceName)%2 == 1:
            self.record = self.dec2byte(len(self.referenceName)+5)
        else:
            self.record = self.dec2byte(len(self.referenceName)+4)
        self.record = self.dec2byte(self.cReferenceName)
        self.record = np.array([ord(i) for i in self.referenceName],dtype=np.uint8)
        if len(self.referenceName)%2 == 1:
            self.record = np.zeros(1,dtype=np.uint8)
        
        #Define strans
        if not self.strans == 0:
            self.record = self.dec2byte(6)
            self.record = self.dec2byte(self.cSTrans)
            self.record = self.dec2byte(self.strans)

        #Define mag
        if not self.mag == 1:
            self.record = self.dec2byte(12)
            self.record = self.dec2byte(self.cMag)
            self.record = self.dec2fbin(self.mag)
            
        #Define angle            
        if not self.angle == 0:
            self.record = self.dec2byte(12)
            self.record = self.dec2byte(self.cAngle)
            self.record = self.dec2fbin(self.angle)
        
        #Define xy
        self.record = self.dec2byte(12)
        self.record = self.dec2byte(self.cXY)
        self.record = self.dec2byte(self.xy[0],4)
        self.record = self.dec2byte(self.xy[1],4)
            
        #Element end
        self.record = self.dec2byte(4)
        self.record = self.dec2byte(self.cEnd)
        
        self.recordClip()
            
    def readRecord(self, record):
        '''
        readRecord(record)
        
        Reads the structure reference record and updates the structure 
        reference element parameters
        '''
        
        self.pointer = 0
        
        #Check if record is an structure reference element
        if self.byte2dec(record[self.opCodePointer]) == self.cSRef:
            self.pointer += 4
        else:
            raise ValueError('GDSII_SRef.readRecord() : The record is not an structure reference (SRef) element')
            
        #Ignore ELFLAG
        if self.byte2dec(record[self.opCodePointer]) == self.cELFLAG:
            self.pointer += 6
        
        #Ignore PLEX
        if self.byte2dec(record[self.opCodePointer]) == self.cPLEX:
            self.pointer += 6
            
        #Structure name
        if self.byte2dec(record[self.opCodePointer]) == self.cReferenceName:
            length = self.byte2dec(record[self.pointer:self.pointer+2])
            if record[self.pointer+length-1] == 0:
                self.referenceName = ''.join([chr(i) for i in record[self.pointer+4:self.pointer+length-1]])
            else:
                self.referenceName = ''.join([chr(i) for i in record[self.pointer+4:self.pointer+length]])
            self.pointer += length
        else:
            raise ValueError('GDSII_SRef.readRecord() : The structure name is not defined')
        
        #Structure transformation
        if self.byte2dec(record[self.opCodePointer]) == self.cSTrans:
            self.strans = self.byte2dec(record[self.pointer+4:self.pointer+6])
            if self.strans > 2**15-1:
                self.reflection = 1
            self.pointer += 6
        
            #Mag
            if self.byte2dec(record[self.opCodePointer]) == self.cMag:
                self.mag = self.fbin2dec(record[self.pointer+4:self.pointer+12])
                self.pointer += 12
                
            #Angle
            if self.byte2dec(record[self.opCodePointer]) == self.cAngle:
                self.angle = self.fbin2dec(record[self.pointer+4:self.pointer+12])
                self.pointer += 12
        else:
            self.mag = 1
            self.reflection = 0
            self.angle = 0
        
        #XY
        if self.byte2dec(record[self.opCodePointer]) == self.cXY:
            self.xy = [self.byte2dec(record[self.pointer+4:self.pointer+8]),
                       self.byte2dec(record[self.pointer+8:self.pointer+12])]
        else:
            raise ValueError('GDSII_SRef.readRecord() : The xy displacements are not defined')

def test():
    a = GDSII_SRef()
    a.setSRef(referenceName='doseArray',xy=[1000,2000],reflection=1,mag=0.57,angle=45.2)
    a.genRecord()
    print a
    b = GDSII_SRef()
    b.readRecord(a.record)
    print b
    

if __name__ == '__main__':
    test()
