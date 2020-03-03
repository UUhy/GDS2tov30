#!/usr/bin/env ipython

'''
Numpy is the fundamental package for scientific computing with Python.
I use it specifically for its array object which is more powerful than the default python array object.
'''
import numpy as np
from v3 import v3
from v3_Pat import v3_Pat
from v3_TXB import v3_TXB

class v3_TX(v3):
    '''
    v3_ID class : subclass of v3
    
    TX Record class for the Jeol v3.0 format
    
    The TX records stores the text blocks and map-library reference
    information.
    
    The following functions are supported:
       addTextBlock:        Adds a TX block
       genRecord:           Generates TX record binary
    
    Long Chang, UH, May 2013
    '''

    def __init__(self):
        super(v3_TX,self).__init__()
        self._identifier = 'TX'
        self._record = np.zeros(self._maxRecordSize,dtype=np.uint8)
        self._record[0:2] = np.array([ord(i) for i in self._identifier],dtype=np.uint8)    
        self._recordIndex = 4
        self._numTextRecord = 1
        self._numTextBlock = 0
        self._blockBuffer = 100
        self._block = np.zeros(self._blockBuffer,dtype=np.uint8)
        self._blockIndex = 0
        self._blockSectionIndex = []
        self._maxShotRank = 0
        self._chainData = 0
        self._textBlock = []
        self._numData = 0

        self._cChipEnd = 0xFFF5
        self._cRecordEnd = 0xFFF2
        self._aNumData = [2,3]
        
        self._sMax = 34

    def __repr__(self):
        print 'numTextRecord:     ' , self.numTextRecord
        print 'numTextBlock:      ' , self.numTextBlock
        print 'maxShotRank:       ' , self.maxShotRank
        print 'numRect:           ' , self.numRect
        print 'numTrap:           ' , self.numTrap
        print 'numDecRect:        ' , self.numDecRect
        print 'numDecTrap:        ' , self.numDecTrap
        return ''

    @property
    def sMax(self):
        return self._sMax

    @property
    def cRecordEnd(self):
        return self._cRecordEnd
        
    @property
    def cChipEnd(self):
        return self._cChipEnd

    @property
    def identifier(self):
        return self._identifier        
        
    @property
    def numTextRecord(self):
        return self._numTextRecord
        
    @property
    def numTextBlock(self):
        return self._numTextBlock
        
    @property
    def textBlock(self):
        return self._textBlock
        
    @textBlock.setter
    def textBlock(self,val):
        if not isinstance(val,v3_TXB):
            raise TypeError('v3_TX.textBlock : The assigned value must be a v3_TXB object')
        self._textBlock.append(val)
        self._numTextBlock += 1

    @property
    def block(self):
        '''
        block : numpy.ndarray of type numpy.uint8
            The binary pattern data
            
        Description
        -----------
        The block parameter appends its set value
        The block parameter is a dynamically growing array
            The block parameter will grow by self._blockBuffer when appending
            the set value will result in overflow
        '''
        return self._block
    
    @block.setter
    def block(self,val):
        if self._blockIndex + val.size >= self._block.size:
            nBuffer = int(np.ceil(float(val.size)/float(self._blockBuffer)))
            self._block = np.append(self._block,np.zeros(self._blockBuffer*nBuffer,dtype=np.uint8),axis=0)
        self._block[self._blockIndex:self._blockIndex+val.size] = val
        self._blockIndex += val.size

    @property
    def blockIndex(self):
        '''
        blockIndex : integer
            A pointer that tracks the position in the block parameter
            
        Description
        -----------
        The blockIndex automatically points to the next available memory
        position of the block parameter.
        '''
        return self._blockIndex

    @property
    def blockSectionIndex(self):
        '''
        blockSectionIndex : list of integer
            Stores the start position of a block
        '''
        return self._blockSectionIndex
        
    @blockSectionIndex.setter
    def blockSectionIndex(self,val):
        self._blockSectionIndex.append(val)

    def clipBlock(self):
        '''
        clipBlock()
        
        Remove unused elements in the block parameter
        '''
        self._block = np.delete(self._block,np.s_[self._blockIndex::],0)
            
    def addTextBlock(self, textBlock):
        '''
        addTextBlock(textBlock)
        
        Adds a text block to the text record
        
        Parameters
        ----------
        textBlock : v3_TXB
        '''

        self.textBlock = textBlock
        
        self.maxShotRank = textBlock.maxShotRank
        self.numRect += textBlock.numRect
        self.numTrap += textBlock.numTrap
        self.numDecRect += textBlock.numDecRect
        self.numDecTrap += textBlock.numDecTrap
    
    @property
    def numData(self):
        '''
        numData : integer
            Number of field ends, chip ends and record ends in the text record
        '''
        return self._numData
        
    @numData.setter
    def numData(self, val):
        self._numData = val
        
    @property
    def aNumData(self):
        '''
        aNumData : list of two integers
            Address of numData in the record
        '''
        return self._aNumData
    
    @aNumData.setter
    def aNumData(self, val):
        self._aNumData = val
    
    @property
    def chainData(self):
        '''
        chainData : integer
            The length of the next block in units of [words]
        '''
        return self._chainData
        
    @chainData.setter
    def chainData(self,val):
        if val < 1 or val > 2045:
            raise ValueError('v3_TXB.chainData : This parameter must range from 1 to 2045')
        self._chainData = val
        
    @property
    def recordIndex(self):
        return self._recordIndex

    @property
    def record(self):
        return self._record
        
    @record.setter
    def record(self,block):
        if self.recordIndex + block.size >= self._record.size:
            if not all(self._record[self.recordIndex-2:self.recordIndex] == self.dec2bin(self.cRecordEnd)):
                self._record[self.recordIndex:self.recordIndex+2] = self.dec2bin(1)
                self._record[self.recordIndex+2:self.recordIndex+4] = self.dec2bin(self._cRecordEnd)
            self._record = np.append(self._record,np.zeros(self._maxRecordSize,dtype=np.uint8),axis=0)
            #recordIndex points to beginning of new record
            self._recordIndex = self._record.size-self._maxRecordSize
            #Add the 'TX' identifier
            self._record[self.recordIndex:self.recordIndex+2] = np.array([ord(i) for i in self.identifier],dtype=np.uint8)
            self._recordIndex += 2
            #Update the number of data
            self._record[self.aNumData] = self.dec2bin(self.numData)
            self.numData = 0
            #Add the number of data
            self._record[self.recordIndex:self.recordIndex+2] = np.array([0,0],dtype=np.uint8)
            self._aNumData = [self.recordIndex,self.recordIndex+1]
            self._recordIndex += 2
            self._numTextRecord += 1
        #Adds chain data to the record
        self.chainData = block.size/2
        self._record[self.recordIndex:self.recordIndex+2] = self.dec2bin(self.chainData)
        self._recordIndex += 2
        #Appends the block to the record
        self._record[self.recordIndex:self.recordIndex+block.size] = block
        self._recordIndex += block.size
        self.numData += 1

    def genRecord(self):
        '''
        genRecord()
    
        Generates the binary Text record
        
        Description
        -----------
        Generates the binary text record from the text block data.  The
        syntax for the text record is:
        <Text Record> =     <Text Identifier><Number of data>
                            <Text Block*>
        A '?' means that the block is optional
        A '*' means that the block appears one or more times
        '''
        for i in self.textBlock:
            if i.fieldPositionX == 1000000 and i.fieldPositionY == 1200000:
                pass
            i.genRecord(self.recordIndex%self.maxRecordSize)
            tmp = i.blockSectionIndex
            tmp.append(i.block.size)
            for j in range(0,len(tmp)-1):
                self.record = i.block[tmp[j]:tmp[j+1]]
        self.clipBlock()
        
        #The final Field End is changed to a Chip End
        self._record[self._recordIndex-2:self._recordIndex] = self.dec2bin(self.cChipEnd)
        
        #Adds a record end
        self.record = self.dec2bin(self.cRecordEnd)
        
        #Update the number of data for the last text block
        self._record[self.aNumData] = self.dec2bin(self.numData)
        
def test(): 
    
    #Rectangles
    v1 = np.array([[0,0,3,3],[10,0,5,3],[0,10,3,5],[10,10,5,5]])
    #Rectangles as Trapezoids
    v2 = np.array([[0,15,0,25,20,25,20,15],[25,0,25,20,35,20,35,0]])
    #Triangles
    v3 = np.array([[5,30,10,35,15,30],[0,35,0,45,5,40],[10,45,5,50,15,50],[20,35,15,40,20,45]])
    #Right Triangles
    v4 = np.array([[6,20,6,44,10,44],[14,20,10,44,14,44],[10,36,14,40,14,36],[6,36,6,40,10,36]])
    #Trapezoids
    v5 = np.array([[25,25,30,30,35,30,40,25],[25,30,25,45,30,40,30,35],[40,30,35,35,35,40,40,45],[30,45,23,50,40,50,35,45]])
    
    v = []
    for i in v1:
        v.append(i)
    for i in v2:
        v.append(i)
    for i in v3:
        v.append(i)
    for i in v4:
        v.append(i)
    for i in v5:
        v.append(i)
        
    TXB = v3_TXB()
    TXB.addPattern(v,pX=60,pY=70,nX=100,nY=500)
    #for i in range(15):
    TX = v3_TX()
    TX.addTextBlock(TXB)
        
    TX.genRecord()
    
#    f = open('text.v30','w')
#    f.write(TX.record)
#    f.close()
    
    print TX

if __name__ == '__main__':
    test()
