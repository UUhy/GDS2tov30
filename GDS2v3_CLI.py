#!/usr/bin/env ipython

import sys
import copy
from v3_Director import v3_Director
from GDSII_Library import GDSII_Library
from ELD_Chip import ELD_Chip

class GDS2v3(object):
    
    def __init__(self):
        self._v = v3_Director()
        self._g = GDSII_Library()
        self._c = ELD_Chip()
        self._fieldSize = [2000000, 2000000]
        self._filename = ''
        self._hierarchyList = None
        self._hierarchyIndex = None
        self._hierarchyRepeat = None
        
    @property
    def v(self):
        '''
        v : v3_Director object
            Jeol v3.0 layout
        '''
        return self._v
        
    @property
    def g(self):
        '''
        g : GDSII_Library object
            GDSII stream layout
        '''
        return self._g
        
    @property
    def c(self):
        '''
        c : ELD_Chip object
            Electron-beam Lithography Datastructure layout
        '''
        return self._c
        
    @property
    def fieldSize(self):
        '''
        fieldSize : list of 2 integers
            The width and height of each field
        '''
        return self._fieldSize
    
    @fieldSize.setter
    def fieldSize(self,val):
        self._fieldSize = val
        
    @property
    def filename(self):
        '''
        filename : string
            Name of file to convert
        '''
        return self._filename

    @filename.setter
    def filename(self, val):
        self._filename = val        
        
    @property
    def hierarchyList(self):
        '''
        hierarchyList : a list of list of strings
            The GDSII hierarchy tree
        '''
        return self._hierarchyList
    
    @hierarchyList.setter
    def hierarchyList(self, val):
        self._hierarchyList = val
        
    @property
    def hierarchyIndex(self):
        '''
        hierarchyIndex : a list of list of integers
            The GDSII hierarchy tree using indices
        '''
        return self._hierarchyIndex
    
    @hierarchyIndex.setter
    def hierarchyIndex(self, val):
        self._hierarchyIndex = val
        
    @property
    def hierarchyRepeat(self):
        '''
        hierarchyRepeat : list of integers
            Number of times a hierarchyList is repeated
        '''
        return self._hierarchyRepeat
        
    @hierarchyRepeat.setter
    def hierarchyRepeat(self, val):
        self._hierarchyRepeat = val

    def setMode(self, mode = 2):
        '''
        setMode(mode = 2)
        
        Sets the JBX-5500FS mode for the conversion
        
        Parameters
        ----------
        mode : integer of either 2 or 4
            JBX-5500 EOS mode 2 or 4
        '''
        if mode in [2,4]:
            self.v.setMode(mode)
            self.fieldSize = [self.v.ID.fieldSizeX, self.v.ID.fieldSizeY]
        else:
            raise ValueError('GDS2v3.setMode() : The mode parameter must be in the set [2,4]')    
    
    def readGDS(self, filename):
        '''
        readGDS(filename)
        
        Reads a GDS file and populate the GDS layout
        
        Parameters
        ----------
        filename : string
            Name of gds file to be read
        '''
        if filename[-4:].lower() == '.gds':
            self.filename = filename[:-4]
        else:
            self.filename = filename
        self.g.readFile(self.filename)
        
    def selectCell(self, cellName = 'main'):
        '''
        selectCell(cellName = 'main')
        
        Selects a cell to be processed/converted
        
        Parameters
        ----------
        cellName : string
            Name of cell to be processed
        '''
        if not cellName in self.g.structureName:
            raise ValueError('GDS2v3.selectCell() : The specified cell name does not exist.')
        try:
            self.hierarchyList, self.hierarchyIndex, self.hierarchyRepeat = self.g.genHierarchyTree(cellName)
        except:
            self.hierarchyList = None
            self.hierarchyIndex = self.g.structureName.index(cellName)
                
    def convGDS2ELD(self):
        '''
        convGDS2ELD()

        Converts the GDS layout to the ELD layout
        
        Note
        ----
        KLayout v0.21.19 stores the array pitch incorrectly I think, so the
        code may fail to work with other GDS files or when KLayout is fixed.
        '''
        if self.hierarchyList is None:
            cellID = self.c.addCell()
            for i in self.g.structure[self.hierarchyIndex].boundary:
                self.c.addPattern(cellID,copy.copy(i.xy),i.datatype)
        else:
            for i in range(len(self.hierarchyList)):
                branch = self.hierarchyList[i]
                for j in range(self.hierarchyRepeat[i]):
                    cellID = self.c.addCell()
                    #Add patterns
                    for k in self.g.structure[branch[-1]].boundary:
                        self.c.addPattern(cellID,copy.copy(k.xy),k.datatype)
                    #Add aref/sref displacement
                    try:
                        index = self.hierarchyIndex[i][j]
                        for k in range(len(branch[:-1])):
                            if index[k+1] < 0:
                                l = self.g.structure[branch[k]].aref[-index[k+1]-1]
                                self.c.offsetCellDisplacement(cellID,l.xy.copy())
                                self.c.setCellArray(cellID,l.pitchX,l.pitchY,l.nX,l.nY)
                            else:
                                l = self.g.structure[branch[k]].sref[index[k+1]-1]
                                self.c.offsetCellDisplacement(cellID,l.xy.copy())
                    except:
                        pass
        scale = self.g.unit/(1.0/self.v.ID.unitPatternData*1e-6)
        self.c.setScale(scale)
        self.c.setFieldSize(self.fieldSize)
        self.c.fracture()

    def convELD2v3(self):
        '''
        convELD2v3
        
        Converts the ELD layout to the v3 layout
        '''
        self.v.setChipSize(self.c.chipSize[0],self.c.chipSize[1])
        for i in self.c.field:
            fieldID = i.fieldID
            try:
                self.v.addField(fieldID,0,i.displacement[0],i.displacement[1],0,0)
            except:
                pass
            for j in i.cell:
                for k in j.pattern:
                    try:
                        self.v.addPattern(fieldID, [l[:-2] for l in k.xy], k.shotRank, j.pitchX, j.pitchY, j.nX, j.nY)
                    except:
                        pass
    def writev3(self):
        self.v.writeFile(self.filename)
        
    def plotELD(self):
        import matplotlib.pyplot as plot
        for l in self.c.field:
            for i in l.cell:
                for j in i.pattern:
                    for k in j.xy:
                        plot.plot(k[::2]+l.displacement[0],k[1::2]+l.displacement[1],'--',linewidth=2)
        plot.gca().invert_yaxis()
        plot.show()
        
def convert(argv):
    import time
    start = time.time()
    filename = argv[0]
    if argv[1] == '2' or argv[1] == '4':
        mode = int(argv[1])
    else:
        print 'Error_Input: The second argument should be 2 or 4'
    cellname = argv[2]

    z = GDS2v3()
    z.setMode(mode)
    z.readGDS(filename)
    try:
    	z.selectCell(cellname)
    except ValueError:
    	print 'Error_Input: The specified cell does not exist'
    z.convGDS2ELD()
    z.convELD2v3()
    z.writev3()

    end = time.time()
    print int(end-start)
   
if __name__ == '__main__':
    convert(sys.argv[1:])