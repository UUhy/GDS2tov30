#!/usr/bin/env ipython

import numpy as np
import re
from GDSII import GDSII

class GDSII_ARef(GDSII):
    '''
    GDSII_ARef class : subclass of GDSII
    
    GDSII Stream file format release 6.0
    Array of structure reference (ARef) Element
    
    The ARef element references a cell and repeats it along an array.  A cell 
    can be referenced before it is defined.  The cells are spaced according 
    the the pitchX, pitchY parameters and the number of repeats are specified 
    by the nX, nY parameters.  By default, the array extends along the 
    positive X and positive Y axis.  However, it is possible to rotate the 
    array vector counterclockwise by specifying the  xRot and yRot parameters.  
    Alternatively, the array parameters can be specified by nX, nY, xxy, yxy 
    where xxy is the endpoint for the x array vector and yxy is the endpoint 
    for the y array vector.
    
    When a cell is referenced it can be subjected to 3 transformation:
    reflection about the x axis, magnification and rotation.  These
    transformations are applied to the cell within its coordinate system.
    Therefore, rotation is centered at the origin, magnification simply scales
    the value of all vertices and reflection mirrors the layout about the x
    axis.
    
    The functions of this class are:
       setARef         =   Adds an array of structure reference
       genRecord       =   Generate the record binary
       readRecord      =   Reads a array of structure reference element record
    
    Long Chang, UH, May 2013
    '''

    def __init__(self):
        super(GDSII_ARef,self).__init__()
        self._referenceName = ''
        self._reflection = 0
        self._mag = 0
        self._angle = 0
        self._pitchX = 0
        self._pitchY = 0
        self._nX = 0
        self._nY = 0
        self._xRot = 0
        self._yRot = 0
        self._xy = np.array([0,0],dtype=np.int32)
        self._yy = np.array([0,0],dtype=np.int32)
        self._yy = np.array([0,0],dtype=np.int32)
        self._strans = 0
        
        self._cARef             = 0x0B00    #Array reference element begin
        self._cELFLAG           = 0x2601    #ELFLAG property (optional)
        self._cPLEX             = 0x2F03    #PLEX property (optional)
        self._cReferenceName    = 0x1206    #Structure name
        self._cSTrans           = 0x1A01    #Strans property
        self._cMag              = 0x1B05    #Magnification property
        self._cAngle            = 0x1C05    #Angle property
        self._cColRow           = 0x1302    #Colrow property
        self._cXY               = 0x1003    #XY property
        self._cEnd              = 0x1100    #Element end

    def __repr__(self):
        print 'Array reference element'
        print 'referenceName:      ' , self.referenceName
        print 'xy:                 ' , self.xy[0] , ',' , self.xy[1]
        print 'pitchX:             ' , self.pitchX
        print 'pitchY:             ' , self.pitchY
        print 'nX:                 ' , self.nX
        print 'nY:                 ' , self.nY
        print 'xRot:               ' , self.xRot
        print 'yRot:               ' , self.yRot
        print 'reflection:         ' , self.reflection
        print 'mag:                ' , self.mag
        print 'angle:              ' , self.angle
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
            raise TypeError('GDSII_ARef.referenceName : This parameter must be of type str')
        if len(val) > 32:
            raise ValueError('GDSII_ARef.referenceName : This parameter cannot be longer than 32 characters')
        regex = re.compile('[\W^?^$]')
        if not regex.search(val) == None:
            raise ValueError('GDSII_ARef.referenceName : This parameter must contain only the following characters: A-Z, a-z, 0-9, _, ? and $')
        self._referenceName = val        
        
    @property
    def xy(self):
        '''
        xy : numpy.ndarray of type numpy.int32 with 2 elements or list of 2 integer elements
            The origin, [x y], of the array reference
        '''
        return self._xy
        
    @xy.setter
    def xy(self, val):
        if isinstance(val,list):
            val = np.array(val,dtype=np.int32)
        elif not isinstance(val,np.ndarray):
            raise TypeError('GDSII_ARef.xy : This parameter must be of type numpy.ndarray')
        if not val.size == 2:
            raise TypeError('GDSII_ARef.xy : This parameter must have only 2 elements')
        self._xy = val
        
    @property
    def xx(self):
        '''
        xx : numpy.ndarray of type numpy.int32 with 2 elements or list of 2 integer elements
            The origin, [x y], of the array reference
        '''
        return self._xx
        
    @xx.setter
    def xx(self, val):
        if isinstance(val,list):
            val = np.array(val,dtype=np.int32)
        elif not isinstance(val,np.ndarray):
            raise TypeError('GDSII_ARef.xx : This parameter must be of type numpy.ndarray')
        if not val.size == 2:
            raise TypeError('GDSII_ARef.xx : This parameter must have only 2 elements')
        self._xx = val

    @property
    def yy(self):
        '''
        yy : numpy.ndarray of type numpy.int32 with 2 elements or list of 2 integer elements
            The origin, [x y], of the array reference
        '''
        return self._yy
        
    @yy.setter
    def yy(self, val):
        if isinstance(val,list):
            val = np.array(val,dtype=np.int32)
        elif not isinstance(val,np.ndarray):
            raise TypeError('GDSII_ARef.yy : This parameter must be of type numpy.ndarray')
        if not val.size == 2:
            raise TypeError('GDSII_ARef.yy : This parameter must have only 2 elements')
        self._yy = val

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
            raise ValueError('GDSII_ARef.reflection : This parameter must be either 0 or 1')
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
    def nX(self):
        '''
        nX = integer
            Array repeats along X
        '''
        return self._nX
    
    @nX.setter
    def nX(self, val):
        if val < 0 or val >= 32768:
            raise ValueError('GDSII_ARef.nX : This parameter must range from 0 to 32767')
        self._nX = val
        
    @property
    def nY(self):
        '''
        nY = integer
            Array repeats along Y
        '''
        return self._nY
    
    @nY.setter
    def nY(self, val):
        if val < 0 or val >= 32768:
            raise ValueError('GDSII_ARef.nY : This parameter must range from 0 to 32767')
        self._nY = val
        
    @property
    def xRot(self):
        '''
        xRot = float
            Array x angle in units of [degrees]
        '''
        return self._xRot
    
    @xRot.setter
    def xRot(self, val):
        self._xRot = val
    
    @property
    def yRot(self):
        '''
        yRot = float
            Array y angle in units of [degrees]
        '''
        return self._yRot
    
    @yRot.setter
    def yRot(self, val):
        self._yRot = val

    def setARef(self, referenceName, xy, pitchX, pitchY, nX, nY, xRot = 0, yRot = 0, reflection = 0, mag = 1, angle = 0):
        '''
        setARef(referenceName, xy, pitchX, pitchY, nX, nY, xRot = 0, yRot = 0, reflection = 0, mag = 1, angle = 0)
        
        Adds an array reference element
        
        Parameters
        ----------
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
            
        Note
        ----
        The calculation of self.xx and self.yy is modified to support KLayout
        '''
        self.referenceName = referenceName
        self.xy = xy
        self.pitchX = pitchX
        self.pitchY = pitchY
        self.nX = nX
        self.nY = nY
        self.xRot = xRot
        self.yRot = yRot
        self.reflection = reflection
        self.mag = mag
        self.angle = angle
        
#        self.xx = [self.xy[0]+int(self.pitchX*(self.nX-1)*np.cos(self.xRot*np.pi/180)),
#                   self.xy[1]+int(self.pitchX*(self.nX-1)*np.sin(self.xRot*np.pi/180))]
#        self.yy = [self.xy[0]+int(self.pitchY*(self.nY-1)*np.cos(self.yRot*np.pi/180-np.pi/2)),
#                   self.xy[1]+int(self.pitchY*(self.nY-1)*np.sin(self.yRot*np.pi/180-np.pi/2))]
        self.xx = [self.xy[0]+int(self.pitchX*(self.nX)*np.cos(self.xRot*np.pi/180)),
                   self.xy[1]+int(self.pitchX*(self.nX)*np.sin(self.xRot*np.pi/180))]
        self.yy = [self.xy[0]+int(self.pitchY*(self.nY)*np.cos(self.yRot*np.pi/180-np.pi/2)),
                   self.xy[1]+int(self.pitchY*(self.nY)*np.sin(self.yRot*np.pi/180-np.pi/2))]

    @property
    def cARef(self):
        '''
        cBoundary : 0x0B00
            Command code for array reference element begin
        '''
        return self._cARef
    
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
    def cColRow(self):
        '''
        cColRow : 0x1302
            Command code for the colrow property
        '''
        return self._cColRow
    
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
        
        Generates the array reference element binary
        
        Description
        -----------
        The array reference element is specified by records in the following 
        order:
            ARef
            ELFLAGS         (optional)
            PLEX            (optional)
            ReferenceName   
            STrans          (optional)
            Mag             (optional)
            Angle           (optional)
            ColRow
            XY
        '''
        self.recordClear()
        
        #Array reference start
        self.record = self.dec2byte(4)
        self.record = self.dec2byte(self.cARef)
        
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
            
        #Define colrow
        self.record = self.dec2byte(8)
        self.record = self.dec2byte(self.cColRow)
        self.record = self.dec2byte(self.nX)
        self.record = self.dec2byte(self.nY)
        
        #Define xy
        self.record = self.dec2byte(28)
        self.record = self.dec2byte(self.cXY)
        self.record = self.dec2byte(self.xy[0],4)
        self.record = self.dec2byte(self.xy[1],4)
        self.record = self.dec2byte(self.xx[0],4)
        self.record = self.dec2byte(self.xx[1],4)
        self.record = self.dec2byte(self.yy[0],4)
        self.record = self.dec2byte(self.yy[1],4)
            
        #Element end
        self.record = self.dec2byte(4)
        self.record = self.dec2byte(self.cEnd)
        
        self.recordClip()
            
    def readRecord(self, record):
        '''
        readRecord(record)
        
        Reads the array reference record and updates the array reference 
        element parameters
        '''
        
        self.pointer = 0
        
        #Check if record is an array reference element
        if self.byte2dec(record[self.opCodePointer]) == self.cARef:
            self.pointer += 4
        else:
            raise ValueError('GDSII_ARef.readRecord() : The record is not an array reference (ARef) element')
            
        #Ignore ELFLAG
        if self.byte2dec(record[self.opCodePointer]) == self.cELFLAG:
            self.pointer += 6
        
        #Ignore PLEX
        if self.byte2dec(record[self.opCodePointer]) == self.cPLEX:
            self.pointer += 6
            
        #Reference structure name
        if self.byte2dec(record[self.opCodePointer]) == self.cReferenceName:
            length = self.byte2dec(record[self.pointer:self.pointer+2])
            if record[self.pointer+length-1] == 0:
                self.referenceName = ''.join([chr(i) for i in record[self.pointer+4:self.pointer+length-1]])
            else:
                self.referenceName = ''.join([chr(i) for i in record[self.pointer+4:self.pointer+length]])
            self.pointer += length
        else:
            raise ValueError('GDSII_ARef.readRecord() : The structure name is not defined')
        
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
            self.reflection = 0
            self.mag = 1
            self.angle = 0
        
        #Column and Row
        if self.byte2dec(record[self.opCodePointer]) == self.cColRow:
            self.nX = self.byte2dec(record[self.pointer+4:self.pointer+6])
            self.nY = self.byte2dec(record[self.pointer+6:self.pointer+8])
            self.pointer += 8
        else:
            raise ValueError('GDSII_ARef.readRecord() : The number of columns and rows are not defined')
            
        #XY
        if self.byte2dec(record[self.opCodePointer]) == self.cXY:
            self.xy = [self.byte2dec(record[self.pointer+4:self.pointer+8]),
                       self.byte2dec(record[self.pointer+8:self.pointer+12])]
            self.xx = [self.byte2dec(record[self.pointer+12:self.pointer+16]),
                       self.byte2dec(record[self.pointer+16:self.pointer+20])]
            self.yy = [self.byte2dec(record[self.pointer+20:self.pointer+24]),
                       self.byte2dec(record[self.pointer+24:self.pointer+28])]
#            self.pitchX = np.sqrt(np.sum(np.int64(self.xx-self.xy)**2))/(self.nX-1)
#            self.pitchY = np.sqrt(np.sum(np.int64(self.yy-self.xy)**2))/(self.nY-1)
            self.pitchX = np.sqrt(np.sum(np.int64(self.xx-self.xy)**2))/self.nX
            self.pitchY = np.sqrt(np.sum(np.int64(self.yy-self.xy)**2))/self.nY           
            tmp = self.xx-self.xy
            self.xRot = np.arctan2(tmp[1],tmp[0])*180/np.pi
            tmp = self.yy-self.xy
            self.yRot = np.arctan2(tmp[1],tmp[0])*180/np.pi+90
        else:
            raise ValueError('GDSII_ARef.readRecord() : The xy displacements are not defined')

def test():
    a = GDSII_ARef()
    a.setARef(referenceName='doseArray',xy=[0,0],pitchX=100,pitchY=100,nX=10,nY=10,reflection=1,mag=2.5,angle=45.2)
    a.genRecord()
    print a
    b = GDSII_ARef()
    b.readRecord(a.record)
    print b
    

if __name__ == '__main__':
    test()
