#!/usr/bin/env ipython

import numpy as np
from v3_TXB import v3_TXB
from v3_TX import v3_TX
from v3_ID import v3_ID

class v3_Director(object):
    '''
    v3_Director class
    
    This class is used to generate a Jeol 3.0 format ID record
    '''

    def __init__(self):
        self._ID = v3_ID()
        self._TX = v3_TX()
        self._field = []
        self._fieldID = []

    def __repr__(self):
        print 'name:              ' + self.ID.name
        print 'format:            ' + self.ID.format
        print 'doc:               ' + self.ID.doc
        print 'chipSizeX:         ' + str(self.ID.chipSizeX/self.ID.unitChipSize) + ' [um]'
        print 'chipSizeY:         ' + str(self.ID.chipSizeY/self.ID.unitChipSize) + ' [um]'
        print 'fieldSizeX:        ' + str(self.ID.fieldSizeX/self.ID.unitChipSize) + ' [um]'
        print 'fieldSizeY:        ' + str(self.ID.fieldSizeY/self.ID.unitChipSize) + ' [um]'
        print 'posSetAreaSizeX:   ' + str(self.ID.posSetAreaSizeX/self.ID.unitChipSize) + ' [um]'
        print 'posSetAreaSizeY:   ' + str(self.ID.posSetAreaSizeY/self.ID.unitChipSize) + ' [um]'
        print 'unitChipSize:      ' + str(self.ID.unitChipSize) + ' [points/um]'
        print 'unitPosSet:        ' + str(self.ID.unitPosSet) + ' [points/um]'
        print 'unitPatternData:   ' + str(self.ID.unitPatternData) + ' [points/um]'
        print 'maxShotRank:       ' + str(self.ID.maxShotRank)
        print 'numLibraryRecord:  ' + str(self.ID.numLibraryRecord)
        print 'numLibraryBlock:   ' + str(self.ID.numLibraryBlock)
        print 'numTextRecord:     ' + str(self.ID.numTextRecord)
        print 'numTextBlock:      ' + str(self.ID.numTextBlock)
        print 'numRect:           ' + str(self.ID.numRect)
        print 'numTrap:           ' + str(self.ID.numTrap)
        print 'numDecRect:        ' + str(self.ID.numDecRect)
        print 'numDecTrap:        ' + str(self.ID.numDecTrap)
        return ''
        
    @property
    def ID(self):
        return self._ID
        
    @ID.setter
    def ID(self, val):
        self._ID = val
        
    @property
    def TX(self):
        return self._TX
        
    @TX.setter
    def TX(self,val):
        self._TX = val

    def setMode(self, mode = 2):
        if mode == 2:
            self.ID.unitChipSize = 200
            self.ID.unitPosSet = 200
            self.ID.unitPatternData = 200
        elif mode == 4:
            self.ID.unitChipSize = 2000
            self.ID.unitPosSet = 2000
            self.ID.unitPatternData = 2000
        else:
            raise ValueError('v3_Director.setMode() : The "mode" parameter must be either 2 or 4')
                        
    def setChipSize(self,x,y, unit = 0):
        '''
        setChipSize(x,y)
        
        Sets the chip size
        
        Parameters
        ----------
        x : integer ranging from 0 to 25,000
            Specify the chip width
        y : integer rangng from 0 to 25,000
            Specity the chip height
        unit: 0 or 1
            0   :   x, y is in units of [points]
            1   :   x, y is in units of [um]
        '''
        if unit:
            if x < 0 or x > 25000:
                raise ValueError('v3_Director.setChipSize() : The chip width must range from 0 to 25,000 [um]')
            if y < 0 or y > 25000:
                raise ValueError('v3_Director.setChipSize() : The chip height must range from 0 to 25,000 [um]')
            self.ID.chipSizeX = x*self.ID.unitChipSize
            self.ID.chipSizeY = y*self.ID.unitChipSize
        else:
            self.ID.chipSizeX = x
            self.ID.chipSizeY = y
        
    @property
    def fieldID(self):
        return self._fieldID
        
    @fieldID.setter
    def fieldID(self, val):
        if val in self._fieldID:
            raise ValueError('v3_Director.fieldID : The fieldID value ' + str(val) + ' has already been defined')
        self._fieldID.append(val)
    
    @property
    def field(self):
        return self._field
        
    @field.setter
    def field(self, val):
        self._field = val

    def addField(self, fieldID, shotRank=0, fieldX=0, fieldY=0, positionX=0, positionY=0, unit=0):
        '''
        addField(fieldID, shotRank=0, fieldX=0, fieldY=0, positionX=0, positionY=0)
        
        Adds a field
        
        Parameters
        ----------
        fieldID : integer from 0 to 4294967295
            A unique identifier for the field
            
        shotRank : integer from 0 to 255
            The shot rank value for the field
            
        fieldX : integer from 0 to 25,000
            The x position of the field, in units of [um], with respect to the chip origin
            
        fieldY : integer from 0 to 25,000
            The y position of the field, in units of [um], with respect to the chip origin
            
        positionX : integer from 0 to 25,000
            The x position of the pattern area, in units of [um], with respect to the field origin
            
        positionX : integer from 0 to 25,000
            The x position of the pattern area, in units of [um], with respect to the field origin
        '''
        self.fieldID = fieldID
        self.field.append(v3_TXB())
        self.field[-1].shotRank = shotRank
        if unit:
            self.field[-1].fieldPositionX = int(np.ceil(fieldX*self.ID.unitChipSize))
            self.field[-1].fieldPositionY = int(np.ceil(fieldY*self.ID.unitChipSize))
            self.field[-1].positionSetX = int(np.ceil(positionX*self.ID.unitPosSet))
            self.field[-1].positionSetY = int(np.ceil(positionX*self.ID.unitPosSet))
        else:
            self.field[-1].fieldPositionX = fieldX
            self.field[-1].fieldPositionY = fieldY
            self.field[-1].positionSetX = positionX
            self.field[-1].positionSetY = positionX

    def addPattern(self, fieldID, vertices, shotRank=-1, pX = 0, pY = 0, nX = 0, nY = 0, posX = -1, posY = -1):
        '''
        addPattern(fieldID, vertices, shotRank=-1)
        
        Parameters
        ----------
        vertices : list of numpy.ndarray
            Each list element shoud contain a primitive shape.  The numpy.ndarray
            must be defined depending on the primitive shape:
                trapezoid   =   [X1 Y1 X2 Y2 X3 Y3 X4 Y4]
                rectangle   =   [X Y W H]
                triangle    =   [X1 Y1 X2 Y2 X3 Y3]
        
        shotRank : integer from 0 to 255
            The shot rank value for the patterns
            
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
            
        Note
        ----
        1 : 
        '''
        try:
            index = self.fieldID.index(fieldID)
        except ValueError:
            raise ValueError('v3_Director.addPattern() : The fieldID ' + str(fieldID) + ' has not been defined')
        
        self.field[index].addPattern(vertices,shotRank,pX,pY,nX,nY,posX,posY)

    def writeFile(self, filename):
        '''
        writeFile(filename)
    
        Generates the Jeol v3.0 pattern data file
        
        Parameters
        ----------
        filename : string consisting of up to 24 alphanumeric characters
        '''
        if filename[-4:].lower() == '.v30':
            filename = filename[:-4]
        for i in self.field:
            self.TX.addTextBlock(i)
        self.ID.name = filename[filename.rfind('/')+1:]
        self.TX.genRecord()
        self.ID.updateID(self.TX)
        self.ID.genRecord() 
        
        fid = open(filename + '.v30','wb')
        fid.write(self.ID.record)
        fid.write(self.TX.record)
        fid.close()
            
def test(): 
    
    D = v3_Director()
    D.setMode(2)
    D.setChipSize(1000,1000)
    
    #Rectangles
    v1 = np.array([[0,0,3,3],[10,0,5,3],[0,10,3,5],[10,10,5,5]])
    #Rectangles as Trapezoids
    v2 = np.array([[0,15,0,25,20,25,20,15],[25,0,25,20,35,20,35,0]])
    #Triangles
    v3 = np.array([[5,30,10,35,15,30],[0,35,0,45,5,40],[10,45,5,50,15,50],[20,35,15,40,20,45]])
    #Right Triangles
    v4 = np.array([[6,40,6,44,10,44],[14,40,10,44,14,44],[10,36,14,40,14,36],[6,36,6,40,10,36]])
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
    
    D.addField(0)
    D.addPattern(fieldID=0,vertices=v,shotRank=0,pX=60,pY=70,nX=100,nY=500)
    D.writeFile('Director.v30')
    print D.ID
    print D.TX
    

if __name__ == '__main__':
    test()
