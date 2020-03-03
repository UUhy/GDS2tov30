#!/usr/bin/env ipython

import numpy as np
from v3 import v3
from v3_Pat import v3_Pat

class v3_TXB(v3):
    '''
    v3_TXB class : subclass of v3
    
    TX Record class for the Jeol v3.0 format
    
    The TX records stores the text blocks and map-library reference
    information.
    
    The following methods are supported by the v3_TXB class:
       addPattern:          Adds a pattern to the text block
       genRecord:           Generates the binary record
    
    This class is constructed such that:
        1)  Contains a single field
        2)  May contain many patterns
    
    Long Chang, UH, May 2013
    '''

    def __init__(self):
        super(v3_TXB,self).__init__()
        self._blockBuffer = 100
        self._block = np.zeros(self._blockBuffer,dtype=np.uint8)
        self._blockIndex = 0
        self._shotRank = 0
        self._pattern = []
        self._libraryBlock = []
        self._libraryNumber = np.zeros(1,dtype=np.uint16)
        self._fieldPositionX = 0
        self._fieldPositionY = 0
        self._positionSetX = 0
        self._positionSetY = 0
        
        self._cFieldEnd = 0xFFF4                #0xFFF4
        self._cRecordEnd = 0xFFF2               #0xFFF2
        self._cShotRank = 0xFF05                #0xFF05 [S]        
        self._cFieldPosition = 0xFFF0           #0xFFF0 [XX YY]
        self._cPositionSet = 0xFFF1             #0xFFF1 [XX YY]
        self._cPatternCompactionMode2 = 0xFFE2  #0xFFE2 [LBN]
        self._cPatternCompactionMode5 = 0xFFE5  #0xFFE5 [LBN LLx LLy Nx Ny]
        
        self._sShotRank = 4
        self._sFieldPosition = 10
        self._sPositionSet = 10
        self._sPatternCompactionMode2 = 4
        self._sPatternCompactionMode5 = 16
        self._sMax = 26

    def __repr__(self):
        print 'pattern:           ' , len(self.pattern)
        print 'fieldPositionX:    ' , self.fieldPositionX
        print 'fieldPositionY:    ' , self.fieldPositionY
        print 'positionSetX:      ' , self.positionSetX
        print 'positionSetY:      ' , self.positionSetY
        print 'maxShotRank:       ' , self.maxShotRank
        print 'numRect:           ' , self.numRect
        print 'numTrap:           ' , self.numTrap
        print 'numDecRect:        ' , self.numDecRect
        print 'numDecTrap:        ' , self.numDecTrap
        return ''

    @property
    def fieldPositionX(self):
        '''
        fieldPositionX : integer from 1 to 230,000,000
            The field x origin with respect to the chip origin
        '''
        return self._fieldPositionX
        
    @fieldPositionX.setter
    def fieldPositionX(self,val):
        if val < 0 or val > 230000000:
            raise ValueError('v3_TXB.fieldPositionX : This parameter must range from 0 to 230,000,000')
        self._fieldPositionX = val
        
    @property
    def fieldPositionY(self):
        '''
        fieldPositionY : integer from 1 to 230,000,000
            The field y origin with respect to the chip origin
        '''
        return self._fieldPositionY
        
    @fieldPositionY.setter
    def fieldPositionY(self,val):
        if val < 0 or val > 230000000:
            raise ValueError('v3_TXB.fieldPositionY : This parameter must range from 0 to 230,000,000')
        self._fieldPositionY = val
        
    @property
    def positionSetX(self):
        '''
        positionSetX : integer from 1 to 2,000,000
            The pattern x origin with respect to the field origin
        '''
        return self._positionSetX
        
    @positionSetX.setter
    def positionSetX(self,val):
        if val < 0 or val > 2000000:
            raise ValueError('v3_TXB.positionSetX : This parameter must range from 0 to 2,000,000')
        self._positionSetX = val
    
    @property
    def positionSetY(self):
        '''
        positionSetY : integer from 0 to 2,000,000
            The pattern y origin with respect to the field origin
        '''
        return self._positionSetY
        
    @positionSetY.setter
    def positionSetY(self,val):
        if val < 0 or val > 2000000:
            raise ValueError('v3_TXB.positionSetY : This parameter must range from 0 to 2,000,000')
        self._positionSetY = val
        
    @property
    def shotRank(self):
        '''
        shotRank : integer from -1 to 255
            The shot rank value for the patterns in this object
                -1  =   No shot rank
        '''
        return self._shotRank

    @shotRank.setter
    def shotRank(self,val):
        if val < 0 or val >= 256:
            raise ValueError("v3_Pat.shotRank : This parameter must range from 0 to 255")
        self._shotRank = val
        self.maxShotRank = self._shotRank
            
    @property
    def pattern(self):
        return self._pattern

    @pattern.setter
    def pattern(self,val):
       self._pattern.append(val)
            
    def addPattern(self, vertices, shotRank = -1, pX = 0, pY = 0, nX = 0, nY = 0, posX = -1, posY = -1):
        '''
        addPattern(vertices, shotRank = -1)
        
        Adds patterns to the the text block
        
        Parameters
        ----------
        vertices : list of numpy.ndarray
            Each list element shoud contain a primitive shape.  The numpy.ndarray
            must be defined depending on the primitive shape:
                trapezoid   =   [X1 Y1 X2 Y2 X3 Y3 X4 Y4]
                rectangle   =   [X Y W H]
                triangle    =   [X1 Y1 X2 Y2 X3 Y3]
        
        shotRank : integer from 0 to 255
            The shot rank value for the patterns in this object
            
        pX : integer
            The distance between neighboring patterns in the array along X
            
        pY : integer
            The distance between neighboring patterns in the array along Y
            
        nX : integer from 0 to 2047
            The number of repeats of the pattern in the array along X
            
        nY : integer from 0 to 2047
            The number of repeats of the pattern in the array along Y
            
        posX : integer
            The pattern origin with respect to the field origin along X
            
        posY : integer
            The pattern origin with respect to the field origin along Y
        '''
        pattern = v3_Pat()
        pattern.addPattern(vertices,shotRank)
        if not nX < 1 and not nY < 1:
            pattern.setPatternArray(pX,pY,nX,nY)
        if not posX < 0 and not posY < 0:
            pattern.setPatternPosition(posX,posY)
        self.pattern = pattern
        
        self.maxShotRank = shotRank
        self.numRect += pattern.numRect
        self.numTrap += pattern.numTrap
        self.numDecRect += pattern.numDecRect
        self.numDecTrap += pattern.numDecTrap

    @property
    def libraryBlock(self):
        return self._libraryBlock
        
    @libraryBlock.setter
    def libraryBlock(self,val):
        self._libraryBlock.append(val)

    def addLibraryBlock(self, libraryBlock):
        '''
        addLibraryblock(libraryBlock)
        
        Adds a library block reference to the text record
        '''
        self.libraryBlock = libraryBlock
        self.numRect += libraryBlock.numRect
        self.numTrap += libraryBlock.numTrap
        self.numDecRect += libraryBlock.numDecRect
        self.numDecTrap += libraryBlock.numDecTrap
        
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

    def blockFracture(self, offset, sByte):
        '''
        blockFracture(offset,cType)
        
        Parameters
        ----------
        offset : integer from 0 to 4096
        
        sByte : integer
        
        Returns
        -------
        offset : integer from 0 to 4096
        '''

        if self.maxRecordSize < offset + sByte:
            self.block = self.dec2bin(self.cRecordEnd)
            self.blockSectionIndex = self.blockIndex
            offset = 0
        return offset

    @property
    def cFieldPosition(self):
        return self._cFieldPosition
        
    @property
    def cPositionSet(self):
        return self._cPositionSet
        
    @property
    def cFieldEnd(self):
        return self._cFieldEnd
        
    @property
    def cRecordEnd(self):
        return self._cRecordEnd
        
    @property
    def cShotRank(self):
        return self._cShotRank
        
    @property
    def sShotRank(self):
        return self._sShotRank

    @property
    def sFieldPosition(self):
        return self._sFieldPosition
    
    @property
    def sPositionSet(self):
        return self._sPositionSet
        
    @property
    def sMax(self):
        return self._sMax

    def genRecord(self,offset=0):
        '''
        genRecord(offset = 0)
    
        Generates the binary TXB record
        
        Parameters
        ----------
        offset : integer from 0 to 4096
            The position in a record.
            Since a record has a fixed size of 2048 words, the blocks must be
            generated properly to avoid overflow.
        
        Results
        -------
        offset : integer from 0 to 4096
            The position in a record after adding this text block
        
        Description
        -----------
        Generates the binary text block from the text block data.  The
        syntax for the text block is:
        <Text Block> =  <Field Position><Shot Rank>
                        !<Position Set>[[<Shot Rank>]<Pattern Data Block*>]!
        <>  Refers to an item
        !!  Items appear one or more times
        []  Items appear zero or more times
        '''

        if offset < 0 or offset > self.maxRecordSize:
            raise ValueError('v3_TXB.genRecord : The offset parameter must range from 0 to 4096')        
        
        self._block = np.zeros(self._blockBuffer,dtype=np.uint8)
        self._blockIndex = 0
        self._blockSectionIndex = [0]
        
        #Field Position
        offset = self.blockFracture(offset,self.sFieldPosition+2)
        self.block = self.dec2bin(self.cFieldPosition)
        self.block = self.dec2bin(self.fieldPositionX,4)
        self.block = self.dec2bin(self.fieldPositionY,4)
        offset += self.sFieldPosition
        
        #Shot rank value
        offset = self.blockFracture(offset,self.sShotRank+2)
        self.block = self.dec2bin(self.cShotRank)
        self.block = self.dec2bin(self.shotRank)
        offset += self.sShotRank          
        
        #Position Set
        offset = self.blockFracture(offset,self.sPositionSet+2)
        self.block = self.dec2bin(self.cPositionSet)
        self.block = self.dec2bin(self.positionSetX,4)
        self.block = self.dec2bin(self.positionSetY,4)
        offset += self.sPositionSet
        
        #Patterns
        for i in self.pattern:
            offset = i.genRecord(offset)
            for j in range(1,len(i.blockSectionIndex)):
                self.blockSectionIndex = i.blockSectionIndex[j] + self.blockIndex
            self.block = i.block
        
        self.block = self.dec2bin(self.cFieldEnd)
        self.clipBlock()
        
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
    a = v3_TXB()
    a.addPattern(v,pX=60,pY=70,nX=100,nY=500)
    
    a.genRecord(4000)
    
    print a.pattern[0]
    print 'The next two list should be identical at the end'
    print a.block[a.blockSectionIndex[0]:a.blockSectionIndex[1]]
    print a.pattern[0].block[a.pattern[0].blockSectionIndex[0]:a.pattern[0].blockSectionIndex[1]]
    print 'The next two list should be identical'
    print a.block[a.blockSectionIndex[1]:]
    print a.pattern[0].block[a.pattern[0].blockSectionIndex[1]:]
    print a.blockSectionIndex

if __name__ == '__main__':
    test()
