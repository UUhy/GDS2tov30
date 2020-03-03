#!/usr/bin/env ipython

import numpy as np
from GDSII import GDSII

class GDSII_Text(GDSII):
    '''
    GDSII_Text class : subclass of GDSII
    
    GDSII Stream file format release 6.0
    Text Element
    
    The text element is used to place comments on the layout.
    
    The functions of this class are:
       setText         =   Set the text
       genRecord       =   Generate the record binary
       readRecord      =   Reads a text element record

    Long Chang, UH, May 2013
    '''

    def __init__(self):
        super(GDSII_Text,self).__init__()
        self._layer = 0
        self._texttype = 0
        self._pathtype = None
        self._width = None
        self._xy = np.array([0,0],dtype=np.int32)
        self._presentation = None
        self._text = ''
        self._reflection = 0
        self._mag = 1
        self._angle = 0
        self._strans = 0
        
        self._cText             = 0x0C00    #Text element begin
        self._cELFLAG           = 0x2601    #ELFLAG property (optional)
        self._cPLEX             = 0x2F03    #PLEX property (optional)
        self._cLayer            = 0x0D02    #Layer property
        self._cTexttype         = 0x1602    #Texttype property
        self._cPresentation     = 0x1701    #Presentation property
        self._cPathtype         = 0x2102    #Pathtype
        self._cWidth            = 0x0F03    #Width property
        self._cSTrans           = 0x1A01    #Strans property
        self._cMag              = 0x1B05    #Magnification property
        self._cAngle            = 0x1C05    #Angle property
        self._cXY               = 0x1003    #XY property
        self._cString           = 0x1906    #Text string
        self._cEnd              = 0x1100    #Element end

    def __repr__(self):
        print 'Text element'
        print 'structureName:      '
        print 'text:               ' , self.text
        print 'layer:              ' , self.layer
        print 'texttype:           ' , self.texttype
        print 'pathtype:           ' , self.pathtype
        print 'width:              ' , self.width
        print 'xy:                 ' , self.xy
        print 'reflection:         ' , self.reflection
        print 'mag:                ' , self.mag
        print 'angle:              ' , self.angle
        return ''

    @property
    def layer(self):
        '''
        layer : integer from 0 to 255
            The layer number for this text element
        '''
        return self._layer
        
    @layer.setter
    def layer(self, val):
        if val < 0 or val > 256:
            raise ValueError('GDSII_Text.layer : This parameter must range from 0 to 255')
        self._layer = val

    @property
    def texttype(self):
        '''
        texttype : integer from 0 to 255
            The texttype number for this text element
        '''
        return self._texttype
        
    @texttype.setter
    def texttype(self, val):
        if val < 0 or val >= 256:
            raise ValueError('GDSII_Text.texttype : This parameter must range from 0 to 255')
        self._texttype = val

    @property
    def pathtype(self):
        '''
        pathtype : integer from the set [0,1,2]
            Describe the nature of the text segment ends
                0   Square ends at text terminal
                1   Rounded ends at text terminal
                2   Square ends that overlap terminals by one-half the width
        '''
        return self._pathtype
        
    @pathtype.setter
    def pathtype(self, val):
        if not val in [None,0,1,2]:
            raise ValueError('GDSII_Text.pathtype : This parameter must be in the set [0,1,2]')
        self._pathtype = val
        
    @property
    def width(self):
        '''
        width : integer
            Defines the width of the text.  If width is negative, it will be
            independent of any structure scaling
        '''
        return self._width
        
    @width.setter
    def width(self, val):
        if not val == None and not val == 0:
            raise ValueError('GDSII_Text.width : This parameter can not be 0')
        self._width = val
        
    @property
    def xy(self):
        '''
        xy : numpy.ndarray of type numpy.int32
            An array containing the verticies of the text in the form
            [x1 y1 x2 y2 ... xn yn]
        '''
        return self._xy
        
    @xy.setter
    def xy(self, val):
        if isinstance(val,list):
            val = np.array(val,dtype=np.int32)
        elif not isinstance(val,np.ndarray):
            raise TypeError('GDSII_Text.xy : This parameter must be of type numpy.ndarray')
        if not val.size == 2:
            raise ValueError('GDSII_Text.xy : This parameter must have 2 elements')
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
            raise ValueError('GDSII_Text.reflection : This parameter must be either 0 or 1')
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
    def presentation(self):
        '''
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
        '''
        return self._presentation
        
    @presentation.setter
    def presentation(self, val):
        if val >= 2**16:
            raise ValueError('GDSII_Text : This parameter must range from 0 to 65535')
        self._presentation = val
        
    @property
    def text(self):
        '''
        text : string
            A text string
        '''
        return self._text
        
    @text.setter
    def text(self, val):
        if not isinstance(val,str):
            raise TypeError('GDSII_Text : This parameter must be a string')
        if len(val) > 512:
            raise ValueError('GDSII_Text : This parameter can not have more than 512 characters')
        self._text = val

    def setText(self, text, xy, layer = 0, texttype = 0, presentation = None, pathtype = None, width = None, reflection = 0, mag = 1, angle = 0):
        '''
        setText(text, xy, layer = 0, texttype = 0, presentation = None, pathtype = None, width = None, reflection = 0, mag = 1, angle = 0)
        
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
        self.xy = xy
        self.text = text
        self.layer = layer
        self.texttype = texttype

    @property
    def cText(self):
        '''
        cText : 0x0C00
            Command code for text element begin
        '''
        return self._cText
    
    @property
    def cLayer(self):
        '''
        cLayer : 0x0D02
            Command code for layer property
        '''
        return self._cLayer
        
    @property
    def cTexttype(self):
        '''
        cTexttype : 0x1602
            Command code for texttype property
        '''
        return self._cTexttype

    @property
    def cPresentation(self):
        '''
        cPresentation : 0x1701
            Command code for presentation property
        '''
        return self._cPresentation

    @property
    def cPathtype(self):
        '''
        cPathtype : 0x2102
            Command code for pathtype property
        '''
        return self._cTexttype    

    @property
    def cWidth(self):
        '''
        cWidth : 0x0F03
            Command code for width property
        '''
        return self._cWidth    

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
    def cString(self):
        '''
        cString : 0x1906
            Command code for text string
        '''
        return self._cString
        
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
        
        Generates the text element binary
        
        Description
        -----------
        The text element is specified by records in thefollowing order:
            Text
            ELFLAGS         (optional)
            PLEX            (optional)
            Layer
            Texttype
            Presentation    (optional)
            Pathtype        (optional)
            Width           (optional)
            STrans          (optional)
            Mag             (optional)
            Angle           (optional)
            XY
            TextString
        '''
        self.recordClear()
        
        #Text start
        self.record = self.dec2byte(4)
        self.record = self.dec2byte(self.cText)
        
        #Define Layer
        self.record = self.dec2byte(6)
        self.record = self.dec2byte(self.cLayer)
        self.record = self.dec2byte(self.layer)
        
        #Define texttype
        self.record = self.dec2byte(6)
        self.record = self.dec2byte(self.cTexttype)
        self.record = self.dec2byte(self.texttype)
        
        #Define presentation
        if not self.presentation == None:
            self.record = self.dec2byte(6)
            self.record = self.dec2byte(self.cPresentation)
            self.record = self.dec2byte(self.presentation)        
        
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
            
        #Define text string
        self.record = self.dec2byte(len(self.text)+4)
        self.record = self.dec2byte(self.cString)
        self.record = np.array([ord(i) for i in self.text],dtype=np.uint8)
            
        #Element end
        self.record = self.dec2byte(4)
        self.record = self.dec2byte(self.cEnd)
        
        self.recordClip()
            
    def readRecord(self, record):
        '''
        readRecord(record)
        
        Reads the text record and updates the text element parameters
        '''
        
        self.pointer = 0
        
        #Check if record is a text element
        if self.byte2dec(record[self.opCodePointer]) == self.cText:
            self.pointer += 4
        else:
            raise ValueError('GDSII_Text.readRecord() : The record is not a text element')
            
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
            raise ValueError('GDSII_Text.readRecord() : The layer number is not defined')
        
        #Texttype
        if self.byte2dec(record[self.opCodePointer]) == self.cTexttype:
            self.texttype = self.byte2dec(record[[self.pointer+4,self.pointer+5]])
            self.pointer += 6
        else:
            raise ValueError('GDSII_Text.readRecord() : The texttype number is not defined')

        #Presentation        
        if self.byte2dec(record[self.opCodePointer]) == self.cPresentation:
            self.presentation = self.byte2dec(record[[self.pointer+4,self.pointer+5]])
            self.pointer += 6
            
        #Pathtype
        if self.byte2dec(record[self.opCodePointer]) == self.cTexttype:
            self.pathtype = self.byte2dec(record[[self.pointer+4,self.pointer+5]])
            self.pointer += 6
            
        #Width
        if self.byte2dec(record[self.opCodePointer]) == self.cWidth:
            self.width = self.byte2dec(record[[self.pointer+4,self.pointer+5]])
            self.pointer += 6
            
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
        
        #XY
        if self.byte2dec(record[self.opCodePointer]) == self.cXY:
            self.xy = [self.byte2dec(record[self.pointer+4:self.pointer+8]),
                       self.byte2dec(record[self.pointer+8:self.pointer+12])]
            self.pointer += 12
        else:
            raise ValueError('GDSII_Text.readRecord() : The xy displacements are not defined')
            
        #String
        if self.byte2dec(record[self.opCodePointer]) == self.cString:
            length = self.byte2dec(record[self.pointer:self.pointer+2])
            self.text = ''.join([chr(i) for i in record[self.pointer+4:self.pointer+length]])
            self.pointer += length
        else:
            raise ValueError('GDSII_Text.readRecord() : The text string is not defined')
            
def test():
    a = GDSII_Text()
    a.setText(text='Hello, this GDSII converter is written in Python',xy=[85,72],layer=2,texttype=1)
    a.reflection = 1
    a.mag = 2.5
    a.angle = .45
    a.genRecord()
    print a
    b = GDSII_Text()
    b.readRecord(a.record)
    print b

if __name__ == '__main__':
    test()
