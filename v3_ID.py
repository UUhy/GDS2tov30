#!/usr/bin/env ipython

'''
Numpy is the fundamental package for scientific computing with Python.
I use it specifically for its array object which is more powerful than the default python array object.
'''
import numpy as np
import datetime as dt
from v3 import v3

class v3_ID(v3):
    '''
    v3_ID class : subclass of v3
    
    ID Record class for the Jeol v3.0 format
    
    The ID record stores the configuration information for the pattern data
    Some parameters in an ID record must be updated after other record classes
    are created.  One and only one ID record is required for a Jeol v3.0 binary
    file.
    
    This class contains many parameters that configures how patterns are
    interpreted.
        chipSizeX:          Chip width
        chipSizeY:          Chip height
        fieldSizeX:         Field width
        fieldSizeY:         Field height
        posSetAreaSizeX:    Pattern area width
        posSetAreaSizeY:    Pattern area height
        unitChipSize:       Units for chip size, field size and pos set area
        unitPosSet:         Units for position set and arrays
        unitPatternData:    Units for patterns
        scalingFactor:      Scales patterns
        resizeVolume:       Resize patterns
        bwi:                Inversion
        patternDirection:   Rotate pattern
        mirror:             Mirror pattern
        block:              Block process pattern (no clue what this means)
    '''

    def __init__(self):
        super(v3_ID,self).__init__()
        self._identifier = 'ID'
        self._name = 'UHNANO                  '
        self._format = 'JEOL52V3.0'
        self._doc = '05-03-13-05-49-00'
        self._chipSizeX = 200000
        self._chipSizeY = 200000
        self._fieldSizeX = 200000
        self._fieldSizeY = 200000
        self._posSetAreaSizeX = 200000
        self._posSetAreaSizeY = 200000
        self._unitChipSize = 200
        self._unitPosSet = 200
        self._unitPatternData = 200
        self._maxShotRank = 0
        self._numCommentRecord = 0
        self._numMapRecord = 0
        self._numLibraryRecord = 0
        self._numTextRecord = 0
        self._numMapBlock = 0
        self._numLibraryBlock = 0
        self._numTextBlock = 0
        self._numRectL = 0
        self._numRectU = 0
        self._numTrapL = 0
        self._numTrapU = 0
        self._numDecRectL = 0
        self._numDecRectU = 0
        self._numDecTrapL = 0
        self._numDecTrapU = 0
        self._scalingFactor = 0
        self._resizeVolume = 0
        self._bwi = 0
        self._patternDirection = 0
        self._mirror = 0
        self._block = 0
        self._record = np.zeros(self.maxRecordSize,dtype=np.uint8)

        self._aIdentifier = (0,2)
        self._aName = (2,26)
        self._aFormat = (26,36)
        self._aDOC = (38,54)
        self._aChipSizeX = (70,74)
        self._aChipSizeY = (74,78)
        self._aFieldSizeX = (78,82)
        self._aFieldSizeY = (82,86)
        self._aPosSetAreaSizeX = (86,90)
        self._aPosSetAreaSizeY = (90,94)
        self._aUnitChipSize = (116,118)
        self._aUnitPosSet = (118,120)
        self._aUnitPatternData = (120,122)
        self._aMaxShotRank = (128,130)
        self._anumCommentRecord = (132,136)
        self._anumMapRecord = (136,140)
        self._anumLibraryRecord = (140,144)
        self._anumTextRecord = (144,148)
        self._aNumRectL = (148,152)
        self._aNumTrapL = (152,156)
        self._aNumDecRectL = (164,168)
        self._aNumDecTrapL = (168,172)
        self._anumMapBlock = (188,192)
        self._anumLibraryBlock = (192,196)
        self._anumTextBlock = (196,200)
        self._aNumRectU = (224,228)
        self._aNumTrapU = (228,232)
        self._aNumDecRectU = (240,244)
        self._aNumDecTrapU = (244,248)
        self._aScalingFactor = (256,260)
        self._aResizeVolume = (260,264)
        self._aBWI = (264,266)
        self._aPatternDirection = (266,268)
        self._aMirror = (268,270)
        self._aBlock = (270,272)

    def __repr__(self):
        print 'name:              ' , self.name
        print 'format:            ' , self.format
        print 'doc:               ' , self.doc
        print 'chipSizeX:         ' , self.chipSizeX/self.unitChipSize , ' [um]'
        print 'chipSizeY:         ' , self.chipSizeY/self.unitChipSize , ' [um]'
        print 'fieldSizeX:        ' , self.fieldSizeX/self.unitChipSize , ' [um]'
        print 'fieldSizeY:        ' , self.fieldSizeY/self.unitChipSize , ' [um]'
        print 'posSetAreaSizeX:   ' , self.posSetAreaSizeX/self.unitChipSize , ' [um]'
        print 'posSetAreaSizeY:   ' , self.posSetAreaSizeY/self.unitChipSize , ' [um]'
        print 'unitChipSize:      ' , self.unitChipSize , ' [points/um]'
        print 'unitPosSet:        ' , self.unitPosSet , ' [points/um]'
        print 'unitPatternData:   ' , self.unitPatternData , ' [points/um]'
        print 'maxShotRank:       ' , self.maxShotRank
        print 'numLibraryRecord:  ' , self.numLibraryRecord
        print 'numLibraryBlock:   ' , self.numLibraryBlock
        print 'numTextRecord:     ' , self.numTextRecord
        print 'numTextBlock:      ' , self.numTextBlock
        print 'numRect:           ' , self.numRect
        print 'numTrap:           ' , self.numTrap
        print 'numDecRect:        ' , self.numDecRect
        print 'numDecTrap:        ' , self.numDecTrap
        return ''

    def getDate(self):
        '''
        getDate()
        
        Returns the time and date as a formatted string YY-MM-DDhh:mm:ss
        
        Returns
        -------
        out : string
            The current date and time in the form YY-MM-DDhh:mm:ss
        '''
        tmp = dt.datetime.now()
        YY = np.array([(tmp.year%100-tmp.year%10)/10,tmp.year%10],dtype=np.uint8)+48
        MM = np.array([(tmp.month%100-tmp.month%10)/10,tmp.month%10],dtype=np.uint8)+48
        DD = np.array([(tmp.day%100-tmp.day%10)/10,tmp.day%10],dtype=np.uint8)+48
        hh = np.array([(tmp.hour%100-tmp.hour%10)/10,tmp.hour%10],dtype=np.uint8)+48
        mm = np.array([(tmp.minute%100-tmp.minute%10)/10,tmp.minute%10],dtype=np.uint8)+48
        ss = np.array([(tmp.second%100-tmp.second%10)/10,tmp.second%10],dtype=np.uint8)+48

        return chr(YY[0]) + chr(YY[1]) + '-' + chr(MM[0]) + chr(MM[1]) + '-' + chr(DD[0]) + chr(DD[1]) + chr(hh[0]) + chr(hh[1]) + ':' + chr(mm[0]) + chr(mm[1]) + ':' + chr(ss[0]) + chr(ss[1])
                
    @property
    def identifier(self):
        '''
        identifier : string constant 'ID'
            This identifier marks the beginning of an ID record
        '''
        return self._identifier            
                
    @property
    def name(self):
        '''
        name : string consisting of up to 24 alphanumeric characters
            A string specifying the name of the ID record
        '''
        return self._name

    @name.setter
    def name(self,val):
        if not isinstance(val,str):
            raise ValueError('v3_ID.name : This parameter must be a string')
        if len(val)>24:
            raise ValueError('v3_ID.name : This parameter must be less than 24 characters long.')
        val += ''.join([' ' for i in range(24-len(val))])
        self._name = val

    @property
    def format(self):
        '''
        format : string constant 'JEOL52V3.0'
            A string specifying the record format
        '''
        return self._format

    @property
    def doc(self):
        '''
        doc : string (formatted)
            A string specifying the date of creation (doc) of the ID record
            The format is YY-MM-DDhh:mm:ss
        '''
        return self._doc
    
    @doc.setter
    def doc(self, val):
        if not len(val) == 16:
            raise ValueError('v3_ID.doc : This parameter must contain a string in the format "YY-MM-DDhh:mm:ss"')
        self._doc = val

    @property
    def unitChipSize(self):
        '''
        unitChipSize : integer from 1 to 2000
            Specify the units for chip size, field size and pattern area size
            and field position.  The units are [units/um]
        '''
        return self._unitChipSize
    
    @unitChipSize.setter
    def unitChipSize(self,val):
        if val < 1 or val > 2000:
            raise ValueError('v3_ID.unitChipSize : This parameter must range from 1 to 2000')
        self._unitChipSize = val

    @property
    def unitPosSet(self):
        '''
        unitPosSet : integer from 1 to 2000
            Specify the units for position set, array size or data compaction.
            The units are [units/um]
        '''
        return self._unitPosSet

    @unitPosSet.setter
    def unitPosSet(self, val):
        if val < 1 or val > 2000:
            raise ValueError('v3_ID.unitPosSet : This parameter must range from 1 to 2000')
        self._unitPosSet = val

    @property
    def unitPatternData(self):
        '''
        unitPatternData : integer from 1 to 2000
            Specify the units for pattern data.  The units are [units/um]
        '''
        return self._unitPatternData

    @unitPatternData.setter
    def unitPatternData(self, val):
        if val < 1 or val > 2000:
            raise ValueError('v3_ID.unitPatternData : This parameter must range from 1 to 2000')
        self._unitPatternData = val

    @property
    def chipSizeX(self):
        '''
        chipSizeX : integer from 1 to 230,000,000
            Specify the chip width in units
        '''
        return self._chipSizeX

    @chipSizeX.setter
    def chipSizeX(self, val):
        if val < 1 or val > 230000000:
            raise ValueError('v3_ID.chipSizeX : This parameter must range from 1 to 230,000,000')
        self._chipSizeX = val

    @property
    def chipSizeY(self):
        '''
        chipSizeY : integer from 1 to 230,000,000
            Specify the chip height in units
        '''
        return self._chipSizeY

    @chipSizeY.setter
    def chipSizeY(self, val):
        if val < 1 or val > 230000000:
            raise ValueError('v3_ID.chipSizeY : This parameter must range from 1 to 230,000,000')
        self._chipSizeY = val

    @property
    def fieldSizeX(self):
        '''
        fieldSizeX : integer from 1 to 2,000,000
            Specify the field width in units
        '''
        return self._fieldSizeX

    @fieldSizeX.setter
    def fieldSizeX(self, val):
        if val < 50 or val > 2000000:
            raise ValueError('v3_ID.fieldSizeX : This parameter must range from 50 to 2,000,000')
        self._fieldSizeX = val

    @property
    def fieldSizeY(self):
        '''
        fieldSizeY : integer from 1 to 2,000,000
            Specify the field height in units
        '''
        return self._fieldSizeY

    @fieldSizeY.setter
    def fieldSizeY(self, val):
        if val < 50 or val > 2000000:
            raise ValueError('v3_ID.fieldSizeY : This parameter must range from 50 to 2,000,000')
        self._fieldSizeY = val
    
    @property
    def posSetAreaSizeX(self):
        '''
        posSetAreaSizeX : integer from 1 to 2,000,000
            Specify the pattern area width in units
        '''
        return self._posSetAreaSizeX

    @posSetAreaSizeX.setter
    def posSetAreaSizeX(self, val):
        if val < 1 or val > 2000000:
            raise ValueError('v3_ID.PosSetAreaSizeX : This parameter must range from 1 to 2,000,000')
        self._posSetAreaSizeX = val

    @property
    def posSetAreaSizeY(self):
        '''
        posSetAreaSizeY : integer from 1 to 2,000,000
            Specify the pattern area height in units
        '''
        return self._posSetAreaSizeY

    @posSetAreaSizeY.setter
    def posSetAreaSizeY(self, val):
        if val < 1 or val > 2000000:
            raise ValueError('v3_ID.posSetAreaSizeY : This parameter must range from 1 to 2,000,000')
        self._posSetAreaSizeY = val
    
    @property
    def maxShotRank(self):
        '''
        maxShotRank : integer from 0 to 255
            Maximum shot rank value used
        '''
        return self._maxShotRank

    @maxShotRank.setter
    def maxShotRank(self,val):
        if val < 0 or val >= 2**8:
            raise ValueError('v3_ID.maxShotRank : This parameter must range from 0 to 255')
        self._maxShotRank = val

    @property
    def numCommentRecord(self):
        '''
        numCommentRecord : integer from 0 to 4294967295
            Number of comment records
        '''
        return self._numCommentRecord

    @numCommentRecord.setter
    def numCommentRecord(self,val):
        if val <0 or val >= 2**32:
            raise ValueError('v3_ID.numCommentRecord : This parameter must range from 0 to 4294967295')

    @property
    def numMapRecord(self):
        '''
        numMapRecord : integer from 0 to 4294967295
            Number of map library records
        '''
        return self._numMapRecord

    @numMapRecord.setter
    def numMapRecord(self,val):
        if val <0 or val >= 2**32:
            raise ValueError('v3_ID.numMapRecord : This parameter must range from 0 to 4294967295')

    @property
    def numLibraryRecord(self):
        '''
        numLibraryRecord : integer from 0 to 4294967295
            Number of library records
        '''
        return self._numLibraryRecord

    @numLibraryRecord.setter
    def numLibraryRecord(self,val):
        if val <0 or val >= 2**32:
            raise ValueError('v3_ID.numLibraryRecord : This parameter must range from 0 to 4294967295')
        self._numLibraryRecord = val

    @property
    def numTextRecord(self):
        '''
        numTextRecord : integer from 0 to 4294967295
            Number of text records
        '''
        return self._numTextRecord

    @numTextRecord.setter
    def numTextRecord(self,val):
        if val <0 or val >= 2**32:
            raise ValueError('v3_ID.numTextRecord : This parameter must range from 0 to 4294967295')
        self._numTextRecord = val

    @property
    def numMapBlock(self):
        '''
        numMapBlock : integer from 0 to 65535
            Number of map library blocks
        '''
        return self._numMapBlock

    @numMapBlock.setter
    def numMapBlock(self,val):
        if val <0 or val >= 2**16:
            raise ValueError('v3_ID.numMapBlock : This parameter must range from 0 to 65535')
        self._numMapBlock = val

    @property
    def numLibraryBlock(self):
        '''
        numLibraryBlock : integer from 0 to 65535
            Number of library blocks
        '''
        return self._numLibraryBlock

    @numLibraryBlock.setter
    def numLibraryBlock(self,val):
        if val <0 or val >= 2**16:
            raise ValueError('v3_ID.numLibraryBlock : This parameter must range from 0 to 65535')
        self._numLibraryBlock = val

    @property
    def numTextBlock(self):
        '''
        numTextRecordLB : integer from 0 to 4294967295
            Number of text blocks
        '''
        return self._numTextBlock

    @numTextBlock.setter
    def numTextBlock(self,val):
        if val <0 or val >= 2**32:
            raise ValueError('v3_ID.numTextBlock : This parameter must range from 0 to 4294967295')
        self._numTextBlock = val

    @property
    def scalingFactor(self):
        '''
        scalingFactor : integer from 0 to 4294967295
            Performs scaling on the data
                0       =   Disabled
                1000000 =   1.0
        '''
        return self._scalingFactor

    @scalingFactor.setter
    def scalingFactor(self, val):
        self._scalingFactor = val

    @property
    def resizeVolume(self):
        '''
        resizeVolume : integer from 0 to 4294967295
            Performs resizing on the data
                0       =   Disabled
                1000000 =   1 [um]
        '''
        return self._resizeVolume

    @resizeVolume.setter
    def resizeVolume(self, val):
        self._resizeVolume = val

    @property
    def bwi(self):
        '''
        bwi : integer from 0 to 1
            Performs black and white inversion on the data
                0   =   Disable
                1   =   Inversion
        '''
        return self._bwi

    @bwi.setter
    def bwi(self, val):
        if not val in (0,1):
            raise ValueError('v3_ID.bwi : This parameter must be either 0 or 1')
        self._bwi = val
    
    @property
    def patternDirection(self):
        '''
        patternDirection : integer from 0 to 7
            Performs rotation and reflection on the data
                0   =   Disable
                1   =   Rotate 90 CCW
                2   =   Rotate 180 CCW
                3   =   Rotate 270 CCW
                4   =   Reflect across horizontal axis
                5   =   Reflect across horizontal axis + Rotate 90 CCW
                6   =   Reflect across horizontal axis + Rotate 180 CCW
                7   =   Reflect across horizontal axis + Rotate 270 CCW
        '''
        return self._patternDirection

    @patternDirection.setter
    def patternDirection(self, val):    
        if val < 0 or val >= 7:
            raise ValueError('v3_ID.patternDirection : This parameter must range from 0 to 7')
        self.patternDirection = val

    @property
    def mirror(self):
        '''
        mirror : integer from 0 to 1
            Performs mirroring on the data
                0   =   Disable
                1   =   Mirror
        '''
        return self._mirror
    
    @mirror.setter
    def mirror(self, val):
        if not val in (0,1):
            raise ValueError('v3_ID.mirror : This parameter must be either 0 or 1')
        self._mirror = val

    @property
    def block(self):
        '''
        block : integer from 0 to 1
            Performs block processing on the data
                0   =   Disabled
                1   =   Block processing
        '''
        return self._block
    
    @block.setter
    def block(self, val):
        if not val in (0,1):
            raise ValueError('v3_ID.block : This parameter must be either 0 or 1')
        self._block = val

    @property
    def numRectL(self):
        '''
        numRectL : integer from 0 to 4294967295
            Lower 32-bits representation of the number of rectangles
        '''
        return self._numRectL

    @numRectL.setter
    def numRectL(self, val):
        if val < 0 or val >= 2**32:
            raise ValueError('v3_ID.numRectL : This parameter must range from 0 to 4294967295')
        self._numRectL = val

    @property
    def numRectU(self):
        '''
        numRectU : integer from 0 to 4294967295
            Upper 32-bits representation of the number of rectangles
        '''
        return self._numRectU

    @numRectU.setter
    def numRectU(self, val):
        if val < 0 or val >= 2**32:
            raise ValueError('v3_ID.numRectU : This parameter must range from 0 to 4294967295')
        self._numRectU = val

    @property
    def numTrapL(self):
        '''
        numTrapL : integer from 0 to 4294967295
            Lower 32-bits representation of the number of trapezoids
        '''
        return self._numTrapL

    @numTrapL.setter
    def numTrapL(self, val):
        if val < 0 or val >= 2**32:
            raise ValueError('v3_ID.numTrapL : This parameter must range from 0 to 4294967295')
        self._numTrapL = val

    @property
    def numTrapU(self):
        '''
        numTrapU : integer from 0 to 4294967295
            Upper 32-bits representation of the number of trapezoids
        '''
        return self._numTrapU

    @numTrapU.setter
    def numTrapU(self, val):
        if val < 0 or val >= 2**32:
            raise ValueError('v3_ID.numTrapU : This parameter must range from 0 to 4294967295')
        self._numTrapU = val

    @property
    def numDecRectL(self):
        '''
        numDecRectL : integer from 0 to 4294967295
            Lower 32-bits representation of the number of decompacted rectangles
        '''
        return self._numDecRectL

    @numDecRectL.setter
    def numDecRectL(self, val):
        if val < 0 or val >= 2**32:
            raise ValueError('v3_ID.numDecRectL : This parameter must range from 0 to 4294967295')
        self._numDecRectL = val

    @property
    def numDecRectU(self):
        '''
        numDecRectU : integer from 0 to 4294967295
            Upper 32-bits representation of the number of decompacted rectangles
        '''
        return self._numDecRectU

    @numDecRectU.setter
    def numDecRectU(self, val):
        if val < 0 or val >= 2**32:
            raise ValueError('v3_ID.numDecRectU : This parameter must range from 0 to 4294967295')
        self._numDecRectU = val

    @property
    def numDecTrapL(self):
        '''
        numDecTrapL : integer from 0 to 4294967295
            Lower 32-bits representation of the number of decompacted trapezoids
        '''
        return self._numDecTrapL

    @numDecTrapL.setter
    def numDecTrapL(self, val):
        if val < 0 or val >= 2**32:
            raise ValueError('v3_ID.numDecTrapL : This parameter must range from 0 to 4294967295')
        self._numDecTrapL = val

    @property
    def numDecTrapU(self):
        '''
        numDecTrapU : integer from 0 to 4294967295
            Upper 32-bits representation of the number of decompacted trapezoids
        '''
        return self._numDecTrapU

    @numDecTrapU.setter
    def numDecTrapU(self, val):
        if val < 0 or val >= 2**32:
            raise ValueError('v3_ID.numDecTrapU : This parameter must range from 0 to 4294967295')
        self._numDecTrapU = val

    def updateID(self, R):
        '''
        updateID(R)

        Updates some essential ID parameters

        Parameters
        ----------
        R : v3_TX or v3_LB instance
    
        Description
        -----------
        This function must be used before generating an ID record because some
        parameters from the v3_TX and v3_LB objects must be accumulated in this
        v3_ID object.
        '''
        if R.identifier == 'TX':
            self.numTextRecord += R.numTextRecord
            self.numTextBlock += R.numTextBlock
        elif R.identifier == 'LB':
            self.numLibraryRecord += R.numLibraryRecord
            self.numLibraryBlock += R.numLB
            
        #Determine max shot rank
        self.maxShotRank = R.maxShotRank

        #Count the number of shapes
        self.numRect += R.numRect
        self.numTrap += R.numTrap
        self.numDecRect += R.numDecRect
        self.numDecTrap += R.numDecTrap

        #Convert 64-bit numbers to a couple of 32-bit numbers
        if self.numRect >= 2**32:
            self.numRectL = self.numRect%2**32
            self.numRectU = int(self.numRect/2**32)
        else:    self.numRectL = self.numRect
        if self.numTrap >= 2**32:
            self.numTrapL = self.numTrap%2**32
            self.numTrapU = int(self.numTrap/2**32)
        else:    self.numTrapL = self.numTrap
        if self.numDecRect >= 2**32:
            self.numDecRectL = self.numDecRect%2**32
            self.numDecRectU = int(self.numDecRect/2**32)
        else:    self.numDecRectL = self.numDecRect
        if self.numDecTrap >= 2**32:
            self.numDecTrapL = self.numDecTrap%2**32
            self.numDecTrapU = int(self.numDecTrap/2**32)
        else:    self.numDecTrapL = self.numDecTrap


    @property
    def record(self):
        '''
        record: nd.array of uint8
            The ID record in binary
        '''
        return self._record

    @record.setter
    def record(self,val):
        self._record = val    

    def genRecord(self):
        '''
        genRecord()
    
        Generates the binary ID record
        '''
        self.doc = self.getDate()
        self.record[self._aIdentifier[0]:self._aIdentifier[1]] = np.array([ord(i) for i in self.identifier],dtype=np.uint8)
        self.record[self._aName[0]:self._aName[1]] = np.array([ord(i) for i in self.name],dtype=np.uint8)
        self.record[self._aFormat[0]:self._aFormat[1]] = np.array([ord(i) for i in self.format],dtype=np.uint8)
        self.record[self._aDOC[0]:self._aDOC[1]] = np.array([ord(i) for i in self.doc],dtype=np.uint8)
        self.record[self._aChipSizeX[0]:self._aChipSizeX[1]] = self.dec2bin(self.chipSizeX,4)
        self.record[self._aChipSizeY[0]:self._aChipSizeY[1]] = self.dec2bin(self.chipSizeY,4)
        self.record[self._aFieldSizeX[0]:self._aFieldSizeX[1]] = self.dec2bin(self.fieldSizeX,4)
        self.record[self._aFieldSizeY[0]:self._aFieldSizeY[1]] = self.dec2bin(self.fieldSizeY,4)
        self.record[self._aPosSetAreaSizeX[0]:self._aPosSetAreaSizeX[1]] = self.dec2bin(self.posSetAreaSizeX,4)
        self.record[self._aPosSetAreaSizeY[0]:self._aPosSetAreaSizeY[1]] = self.dec2bin(self.posSetAreaSizeY,4)
        self.record[self._aUnitChipSize[0]:self._aUnitChipSize[1]] = self.dec2bin(self.unitChipSize)
        self.record[self._aUnitPosSet[0]:self._aUnitPosSet[1]] = self.dec2bin(self.unitPosSet)
        self.record[self._aUnitPatternData[0]:self._aUnitPatternData[1]] = self.dec2bin(self.unitPatternData)
        self.record[self._aMaxShotRank[0]:self._aMaxShotRank[1]] = self.dec2bin(self.maxShotRank)
        self.record[self._anumCommentRecord[0]:self._anumCommentRecord[1]] = self.dec2bin(self.numCommentRecord,4)
        self.record[self._anumMapRecord[0]:self._anumMapRecord[1]] = self.dec2bin(self.numMapRecord,4)
        self.record[self._anumLibraryRecord[0]:self._anumLibraryRecord[1]] = self.dec2bin(self.numLibraryRecord,4)
        self.record[self._anumTextRecord[0]:self._anumTextRecord[1]] = self.dec2bin(self.numTextRecord,4)
        self.record[self._aNumRectL[0]:self._aNumRectL[1]] = self.dec2bin(self.numRectL,4)
        self.record[self._aNumTrapL[0]:self._aNumTrapL[1]] = self.dec2bin(self.numTrapL,4)
        self.record[self._aNumDecRectL[0]:self._aNumDecRectL[1]] = self.dec2bin(self.numDecRectL,4)
        self.record[self._aNumDecTrapL[0]:self._aNumDecTrapL[1]] = self.dec2bin(self.numDecTrapL,4)
        self.record[self._anumMapBlock[0]:self._anumMapBlock[1]] = self.dec2bin(self.numMapBlock,4)
        self.record[self._anumLibraryBlock[0]:self._anumLibraryBlock[1]] = self.dec2bin(self.numLibraryBlock,4)
        self.record[self._anumTextBlock[0]:self._anumTextBlock[1]] = self.dec2bin(self.numTextBlock,4)
        self.record[self._aNumRectU[0]:self._aNumRectU[1]] = self.dec2bin(self.numRectU,4)
        self.record[self._aNumTrapU[0]:self._aNumTrapU[1]] = self.dec2bin(self.numTrapU,4)
        self.record[self._aNumDecRectU[0]:self._aNumDecRectU[1]] = self.dec2bin(self.numDecRectU,4)
        self.record[self._aNumDecTrapU[0]:self._aNumDecTrapU[1]] = self.dec2bin(self.numDecTrapU,4)
        self.record[self._aScalingFactor[0]:self._aScalingFactor[1]] = self.dec2bin(self.scalingFactor,4)
        self.record[self._aResizeVolume[0]:self._aResizeVolume[1]] = self.dec2bin(self.resizeVolume,4)
        self.record[self._aBWI[0]:self._aBWI[1]] = self.dec2bin(self.bwi)
        self.record[self._aPatternDirection[0]:self._aPatternDirection[1]] = self.dec2bin(self.patternDirection)
        self.record[self._aMirror[0]:self._aMirror[1]] = self.dec2bin(self.mirror)
        self.record[self._aBlock[0]:self._aBlock[1]] = self.dec2bin(self.block)
        
def test():
    a = v3_ID()
    a.genRecord()
    print a

if __name__ == '__main__':
    test()
