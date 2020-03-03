#!/usr/bin/env ipython

'''
Numpy is the fundamental package for scientific computing with Python.
I use it specifically for its array object which is more powerful than the default python array object.
'''
import numpy as np

class v3(object):
    '''
    v3 class
    
    This is the parent class for the Jeol 3.0 format
    
    Data is stored in sequential records that are 4096 bytes/record.
    
    Jeol v3.0 format = PatternDataFile
    
    PatternDataFile =  IDRecord + CMRecord(s) + MPRecord(s) + LBRecord(s) + 
                       TXRecord(s)
    
    IDRecord =         Identifier + Name + Format + DoC + SizeParameters +
                       Units + ShotRank + RecordCounts + DataCountsLower +
                       BlockCounts + DataCountsUpper + DataConversion
    
    CMRecord =         Identifier + Comments
    
    MPRecord =         Identifier + MapLibraryBlock(s) + RecordEnd
    MapLibraryBlock =  MapLibraryID + BasicPatternDef + ArrayDef
    
    LBRecord =         Identifier + NumberOfData + LibraryBlock(s) + RecordEnd
    LibraryBlock =     LibraryDef + PatterDef(s) + LibraryEnd
    
    TXRecord =         Identifier + NumberOfData + ChainData + 
                       MapLibraryRef(s) + TXBlock(s) + RecordEnd
    MapLibraryRef =    MapLibraryCall + FieldEnd/ChipEnd
    TXBlock =          FieldPos + ShotRank + PosSet + TXPatDef +
                       FieldEnd/ChipEnd
    
    Long Chang, UH, May 2013
    '''

    def __init__(self):
        self._maxRecordSize = 4096
        self._numRect = 0
        self._numTrap = 0
        self._numDecRect = 0
        self._numDecTrap = 0
        self._maxShotRank = 0

    def __repr__(self):
        return 'v3 object'

    @property
    def maxRecordSize(self):
        '''
        maxRecordSize : integer (constant)
            Size of each record
        '''
        return self._maxRecordSize

    @property
    def numRect(self):
        '''
        numRect : integer from 0 to 2^64-1
            The number of rectangles in the data
        '''
        return self._numRect

    @numRect.setter
    def numRect(self,val):
        if val < 0 or val >= 2**64:
            raise ValueError("v3.numRect : This parameter must range from 0 to 2^64-1")
        self._numRect = val

    @property
    def numTrap(self):
        '''
        numTrap : integer from 0 to 2^64-1
            The number of trapezoids in the data
        '''
        return self._numTrap

    @numTrap.setter
    def numTrap(self,val):
        if val < 0 or val >= 2**64:
            raise ValueError("v3.numTrap : This parameter must range from 0 to 2^64-1")
        self._numTrap = val

    @property
    def numDecRect(self):
        '''
        numDecRect : integer from 0 to 2^64-1
            The number of decompacted rectangles in the data
        '''
        return self._numDecRect

    @numDecRect.setter
    def numDecRect(self,val):
        if val < 0 or val >= 2**64:
            raise ValueError("v3.numDecRect : This parameter must range from 0 to 2^64-1")
        self._numDecRect = val
        
    @property
    def numDecTrap(self):
        '''
        numDecTrap : integer from 0 to 2^64-1
            The number of decompacted trapezoids in the data
        '''
        return self._numDecTrap

    @numDecTrap.setter
    def numDecTrap(self,val):
        if val < 0 or val >= 2**64:
            raise ValueError("v3.numDecTrap : This parameter must range from 0 to 2^64-1")
        self._numDecTrap = val

    @property
    def maxShotRank(self):
        return self._maxShotRank
        
    @maxShotRank.setter
    def maxShotRank(self,val):
        if val < 0 or val > 255:
            raise ValueError('v3.maxShotRank : This parameter must range from 0 to 255')
        if val > self._maxShotRank:
            self._maxShotRank = val

    def dec2byte(self, val, nByte=2):
        '''dec2byte(val, nByte=2)
    
        Returns an array representing the decimal value where each element is 1 byte.

        Parameters
        ----------
        val : int32
            The decimal value to be converted
        nByte : number of bytes per decimal value
            The number of bytes used to represent each decimal value
    
        Returns
        -------
        out : ndarray
            The output array contains nByte elements of datatype numpy.uint8
        '''
        if not nByte in [2,4]:
            raise ValueError('v3.dec2byte() : The nByte parameter must be in the set [2,4]')
        tmp = np.zeros(nByte)
        for i in range(nByte):
            tmp[i] = val % 2 ** ((i + 1) * 8)//2 ** ((i + 1) * 8 - 8)
        return np.array(tmp[::-1],dtype=np.uint8)

    def big2mid(self, val):
        '''big2mid(val)
        
        Returns a middle-endian representation of the input array.

        Parameters
        ----------
        val : ndarray or type np.uint8
        
        Returns
        -------
        out : ndarray
            Array of type uint8 in middle-endian byte ordering

        Description
        -----------
        Endian refers to the ordering of multiple bytes in computing.
        The interpretation of multiple bytes of data differ depending
        on the type of processor or microcontroller.
        Big-endian     The "Big end" of the data is stored in memory first
        Little-endian     The "Little end" of the data is stored in memory first
        Middle-endian    A perverse ordering used by some minicomputer manufacturers
        
        The JBX-5500FS minicomputer uses the Middle-endian data ordering.
        For example, the value 0x000F4240 (decimal 1000000) is stored as 0x0F004042.
        '''
        if val.size == 1:
            return val
        elif val.size == 2:
            return np.array(val[[1,0]],dtype=np.uint8)
        elif val.size == 4:
            return np.array(val[[1,0,3,2]],dtype=np.uint8)
        else:
            raise ValueError('v3.big2mid() : input ndarray must contain 1, 2 or 4 elements.')    

    def dec2bin(self,val,nByte=2):
        '''
        dec2bin(val, nByte=2)

        Returns the binary representation of the input decimal number using nBytes

        Parameters
        ----------
        val : uint16 or uint32
            The decimal value to be converted
            
        nByte : number of bytes per decimal value
            The number of bytes used to represent the decimal value

        Returns
        -------
        out : ndarray
            Array of type int8 in middle-endian byte ordering
        '''
        return self.big2mid(self.dec2byte(val,nByte))

    def genRecord(self):
        raise ValueError('v3.genRecord : All subclass must implement the genRecord method.')

def test():
    a = v3()
    a.identifier = 'id'
    print ''
    print "v3.identifier should be = 'ID'"
    print a.identifier
    print ''
    print "v3.dec2byte(1000000,4) should be [0,15,66,64]"
    print a.dec2byte(1000000,4)
    print ''
    print "v3.big2mid(v3.dec2byte(1000000,4)) should be [15,0,64,66]"
    print a.big2mid(a.dec2byte(1000000,4))
    print ''

if __name__ == '__main__':
    test()
