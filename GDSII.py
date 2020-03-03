#!/usr/bin/env ipython

import numpy as np
import math

class GDSII(object):
    '''
    GDSII class
    
    GDSII Stream file format release 6.0
    
    Pattern data is contained in a library of cells.  Cells may contain
    geometric elements such as polygons (boundaries), paths, and other cells.
    Elements in the cell are assigned to "layers" and "datatype".  In ebeam
    lithography and photomask production, layers typically represent different
    processing steps and datatypes are used for any purpose such ass for 
    grouping objects for proximity effect compensation.  There is no explicitly
    stated limit to the level of hierarchy (the degree of cell nesting),
    however, most CAD prgrams impose a limit of 32 levels either explicitly or
    implicitly.
    
    A GDSII Stream file containsa single library record.  The library record
    contains a number of cellscalled structure records.  Within each cell are
    element records.
    
    The GDSII Stream file format is composed of variable length record 
    segments.  Each segment is specified sequentically by a segment length,
    command code, data type, and command parameters.  The segment length is
    2 bytes, the command code is 1 byte, the data typeis 1 byte and the command
    parameters have vriable lengths.  The shortest record does not require any
    command parameters so it is 4 bytes long.
    
    Long Chang, UH, May 2013
    '''

    def __init__(self):
        self._recordBuffer = 100
        self._record = np.zeros(self._recordBuffer,dtype=np.uint8)
        self._recordIndex = 0
        self._maxRecordSize = 2**16-1
        self._pointer = 0
        self._opCodePointer = [2,3]

    def __repr__(self):
        return 'GDSII object'

    @property
    def maxRecordSize(self):
        '''
        maxRecordSize : integer (constant)
            Maximum size of each record is 65535
        '''
        return self._maxRecordSize

    @property
    def record(self):
        '''
        record : numpy.ndarray of type numpy.uint8
            The binary pattern data
        '''
        return self._record
    
    @record.setter
    def record(self,val):
        if self._recordIndex + val.size >= self._record.size:
            nBuffer = int(math.ceil(float(val.size)/float(self._recordBuffer)))
            self._record = np.append(self._record,np.zeros(self._recordBuffer*nBuffer,dtype=np.uint8),axis=0)
        self._record[self._recordIndex:self._recordIndex+val.size] = val
        self._recordIndex += val.size

    @property
    def recordIndex(self):
        return self._recordIndex
        
    def recordClear(self):
        '''
        recordClear()
        
        Clears the record parameter
        '''
        self._record = np.zeros(self._recordBuffer,dtype=np.uint8)
        self._recordIndex = 0
    
    def recordClip(self):
        '''
        recordClip()
        
        Clip trailing zeros from the record parameter
        '''
        self._record = np.delete(self._record,np.s_[self._recordIndex::],0)

    @property
    def pointer(self):
        '''
        pointer : integer
            A pointer to the current position in a record
        '''
        return self._pointer
    
    @pointer.setter
    def pointer(self,val):
        self._pointer = val
        self._opCodePointer = [self._pointer+2,self._pointer+3]
        
    @property
    def opCodePointer(self):
        '''
        opCodePointer : List of 2 integers
            A pointer to the command code in a record
        '''
        return self._opCodePointer

    def dec2byte(self, val, nByte=2):
        '''dec2byte(val, nByte=2)
    
        Returns an array representing the decimal value where each element is 1 byte.

        Parameters
        ----------
        val : signed integer or unsigned float less than 1
            The decimal value to be converted
        nByte : number of bytes per decimal value
            The number of bytes used to represent each decimal value
            A byte is 8 bits
    
        Returns
        -------
        out : numpy.ndarray of type numpy.uint8
            An array where each element represents a byte
            The elements are ordered using big-endian style or the most
            significant bit comes first
            
        Description
        -----------
        A decimal value is parsed into an array of bytes.  For example:
        Decimal         2 byte          4 byte
        1000            [3 232]         [0 0 3 232]
        1000000                         [0 15 66 64]
        0.5             [128 0]         [128 0 0 0]
        0.6             [153 153]       [153 153 153 153]
        '''
        tmp = np.zeros(nByte,dtype=np.uint8)
        if isinstance(val,float) and val < 1:
            for i in range(nByte):
                tmp[i] = val % 2 ** (-i * 8)//2 ** (-(i + 1) * 8)
        else:
            for i in range(nByte):
                tmp[i] = val % 2 ** ((i + 1) * 8)//2 ** (i * 8)
            tmp = tmp[::-1]
        return tmp

    def byte2nibble(self, val):
        '''
        byte2nibble(self,val)
        
        Returns an array of bytes to an array of nibbles
        
        Parameters
        ----------
        val : numpy.ndarray of type numpy.uint8
            An array where each element represents a byte
        
        Returns
        -------
        nibble : numpy.ndarray of type numpy.uint8
            An array where each element represents a nibble
        '''
        nibble = np.zeros(val.size*2,dtype=np.uint8)
        for i in range(val.size):
            nibble[2*i] = val[i] % 2 ** 8 / 2 ** 4
            nibble[2*i+1] = val[i] % 2 ** 4
        return nibble 

    def nibble2byte(self, val):
        '''
        nibble2byte(self,val)
        
        Returns an array of bytes to an array of nibbles
        
        Parameters
        ----------
        val : numpy.ndarray of type numpy.uint8
            An array where each element represents a nibble
        
        Returns
        -------
        byte : numpy.ndarray of type numpy.uint8
            An array where each element represents a byte
        '''
        if not val.size%2 == 0:
            val = np.append(val,np.zeros(0,dtype=np.uint8),axis=0)
        byte = np.zeros(val.size/2,dtype=np.uint8)
        for i in range(byte.size):
            byte[i] = val[i*2]*16 + val[i*2+1]
        return byte

    def dec2nibble(self, val, nNibble=4):
        '''dec2nibble(val, nNibble=4)
    
        Returns an array representing the decimal value where each element is 1 byte.

        Parameters
        ----------
        val : signed integer or unsigned float less than 1
            The decimal value to be converted
        nNibble : number of nibbles per decimal value
            The number of nibbles used to represent each decimal value
            A nibble is 4 bits
    
        Returns
        -------
        out : numpy.ndarray of type numpy.uint8
            An array where each element represents a nibble
            The elements are ordered using the big-endian style or the most
            significant bit comes first
            
        Description
        -----------
        A decimal value is parsed into an array of bytes.  For example:
        Decimal         4 nibble                8 nibble
        1000            [0 3 14 8]              [0 0 0 0 0 3 14 8]
        1000000                                 [0 0 0 15 4 2 4 0]
        0.5             [8 0 0 0]               [8 0 0 0 0 0 0 0]
        0.6             [9 9 9 9]               [9 9 9 9 9 9 9 9]
        '''
        if not nNibble%2 == 0 or nNibble < 2:
            raise ValueError('GDSII.dec2nibble() : The nNibble parameter must be an even integer larger than 1')
        byte = self.dec2byte(val,nNibble/2)
        return self.byte2nibble(byte)
    
    def byte2dec(self, val):
        '''
        byte2dec(val)
        
        Parameters
        ----------
        val : numpy.ndarray of type numpy.uint8
            An array where each element represents a byte
        
        Returns
        -------
        dec : signed integer
            Decimal value
        '''
        dec = 0
        if val[0] > 2**7:
            val = -val - 1
            for i in range(val.size):
                dec = dec + val[i]*2**(8*(val.size-i-1))
            dec = -(dec + 1)
        else:
            for i in range(val.size):
                dec = dec + val[i]*2**(8*(val.size-i-1))
        return dec

    def dec2fbin(self, val):
        '''
        dec2fbin(val)
        
        Returns an array representing the decimal value in excess 64 floating
        point binary
        
        Parameters
        ----------
        val : signed float
            A floating point number to be converted
        
        Results
        -------
        fbin = numpy.ndarray of type numpy.uint8
            An 8 element array with the form [SE M M M M M M M] represents the 
            floating point number in excess 64 notation
        
        Description
        -----------
        Converts a real number to binary wih the following notation:
        
        SEEEEEEE MMMMMMMM MMMMMMMM MMMMMMMM MMMMMMM MMMMMMMM MMMMMMMM MMMMMMM
        
        S is the sign bit
        E is the exponent in excess 64 notation
        M is the normalized mantissa
        
        decimal = (S)*(M)*16^(E-64)
        '''
        
        if val == 0:
            E = np.zeros(1,dtype=np.uint8)
            M = np.zeros(7,dtype=np.uint8)
        else:
            if val < 0:
                val = math.abs(val)
                S = 128
            else:
                S = 0

            w = int(val)
            f = val-w
            if w > 2**56:
                raise ValueError('GDSII.dec2bin() : The val parameter must be smaller than 2^56')
            wnum = self.dec2byte(w,7)
            fnum = self.dec2nibble(f,24)
            
            E = 64
            if all(wnum==0):
                for i in range(fnum.size):
                    if fnum[i] == 0:
                        E -= 1
                    else:
                        break
                fnum = self.nibble2byte(fnum[i:])
                M = fnum[0:7]
            else:
                for i in range(wnum.size):
                    if wnum[i] == 0:
                        continue
                    else:
                        E += (wnum.size-i)*2
                        break
                wnum = wnum[i:]
                fnum = self.nibble2byte(fnum)
                M = np.append(wnum,fnum[0:7-wnum.size],axis=0)
                if M.size < 7:
                    M = np.append(M,np.zeros(7-M.size,dtype=np.uint8),axis=0)
                    
        return np.append(np.array(S+E,dtype=np.uint8,ndmin=1),M,axis=0)

    def fbin2dec(self,val):
        '''
        fbin2dec(val)
        
        Returns the decimal value of an floating point binary in excess 64 notation
        
        Parameters
        ----------
        val : numpy.ndarray of type numpy.uint8
            An array where the elements are [SE M M M M M M M] where
                S is the sign bit
                E is a 7-bit exponent
                M is the mantissa
                
        Results
        -------
        dec : float
            Decimal value
        '''
        S = int(val[0]/128)
        if S == 1:
            E = val[0] - 128 - 64
        else:
            E = val[0] - 64
        M = val[1:]
        dec = 0.0
        for i in range(M.size):
            dec += M[i]/2**(8.0*(i+1))
        dec *= 16**E
        if S == 1:
            dec = -dec
        return dec

    def genRecord(self):
        raise ValueError('GDSII.genRecord() : All subclass must implement the genRecord method.')
    
    def readRecord(self):
        raise ValueError('GDSII.readRecord() : All subclass must implement the genRecord method.')

def test():
    a = GDSII()
    print 'The byte2dec(dec2byte(1000000,4)) is :\t' + str(a.byte2dec(a.dec2byte(1000000,4)))
    print 'The fbin2dec(dec2fbin(0.001)) is :\t' + str(a.fbin2dec(a.dec2fbin(.001)))
    

if __name__ == '__main__':
    test()
