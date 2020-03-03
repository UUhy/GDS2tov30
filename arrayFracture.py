#!/usr/bin/env ipython

import numpy as np
from ELD_Cell import ELD_Cell
import copy

class arrayFracture(object):  
    '''
    arrayFracture class : subclass of object
    
    The arrayFracture class is used to split a cell containing an array of 
    polygons into multiple cells of subarrays.
    
    The arrayFracture class supports the following functions:
        resize                  =   splits the array into smaller arrays
        resizeAxis              =   resizes a single axis
        fieldFracture           =   splits the array into smaller arrays along
                                    field lines
        sliceAxis               =   splits the array along an axial line
            
    Long Chang, UH, May 2014
    '''
    
    def __init__(self):
        self._maxArrayLength = 2047
        
    def __repr__(self):
        print 'array fracture object'
        return ''     
        
    @property
    def maxArrayLength(self):
        '''
        maxArrayLength : int
            The maximum number of repeats that an array can have.  The v3.0
            format specifies 2047
        '''
        return self._maxArrayLength
        
    @maxArrayLength.setter
    def maxArrayLength(self, val):
        if val > 2047 or val < 0:
            raise ValueError('arrayFracture.maxArrayLength : The maximum array length must be between 0 and 2047')
        self._maxArrayLength = val

    def resize(self, cell, maxArrayLength = 2000):
        '''
        resize(self, cell, maxArrayLength = 2000)
        
        Resizes the array
        
        Parameters
        ----------
        cell : ELD_Cell object
            A cell which contains an array of patterns
        maxArrayLength : integer
            Specify the maximum array repeat value
            
        Returns
        -------
        fCell : a list of ELD_Cell object            
            A list cells which contains the resized fractured arrays
            
        Description
        -----------
        This function resizes an array if it is larger than the specified
        length.  The array is resized by slicing/partitioning into multiple
        arrays which are contained in individual cells.  Those cells are
        collected into a single list and returned.
        '''
        self.maxArrayLength = maxArrayLength
        
        tCell = self.resizeAxis(cell,maxArrayLength,0)
        
        fCell = []
        [fCell.extend(self.resizeAxis(tCell[i],maxArrayLength,1)) for i in range(len(tCell))]
        
        return fCell
        
    def resizeAxis(self, cell, maxArrayLength = 2000, axis = 0):
        '''
        resizeAxis(self, cell, maxArrayLength = 2000, axis = 0)
        
        Resizes the array along one axis
        
        Parameters
        ----------
        cell : ELD_Cell object
            A cell which contains an array of patterns
        maxArrayLength : integer
            Specify the maximum array repeat value
        axis : 0 or 1
            Specify the axis to resize
            0   :   x axis
            1   :   y axis
            
        Returns
        -------
        fCell : a list of ELD_Cell object            
            A list cells which contains the resized fractured arrays
            
        Description
        -----------
        This function resizes an array if it is larger than the specified
        length.  The array is resized by slicing/partitioning into multiple
        arrays which are contained in individual cells.  Those cells are
        collected into a single list and returned.
        '''
        self.maxArrayLength = maxArrayLength
        fCell = []
        
        pattern = copy.deepcopy(cell.pattern)
        shotRank = copy.copy(cell.shotRank)
        pitchX = copy.copy(cell.pitchX)
        pitchY = copy.copy(cell.pitchY)
        dx = pitchX*maxArrayLength
        dy = pitchY*maxArrayLength        
        
        if axis == 0:
            nX = [maxArrayLength for j in range(1,int((cell.nX-1)/maxArrayLength)+2)]
            nX[-1] = cell.nX%maxArrayLength
            if len(nX) == 1:
                fCell.append(cell)
            else:
                fCell = [ELD_Cell(cell.cellID) for i in range(len(nX))]
                nY = copy.copy(cell.nY)
                for i in range(len(nX)):
                        fCell[i].pattern = copy.deepcopy(pattern)
                        if type(shotRank) is list:
                            fCell[i].shotRank.extend(shotRank)
                        else:
                            fCell[i].shotRank = shotRank
                        fCell[i].nX = nX[i]
                        fCell[i].nY = nY
                        fCell[i].pitchX = pitchX
                        fCell[i].pitchY = pitchY
                        fCell[i].displacement = cell.displacement + np.array((i*dx,0),dtype=np.int32)
                        fCell[i].updateBoundary()
        elif axis == 1:
            nY = [maxArrayLength for j in range(1,int((cell.nY-1)/maxArrayLength)+2)]
            nY[-1] = cell.nY%maxArrayLength
            if len(nY) == 1:
                fCell.append(cell)
            else:
                fCell = [ELD_Cell(cell.cellID) for i in range(len(nY))]
                nX = copy.copy(cell.nX)
                for i in range(len(nY)):
                        fCell[i].pattern = copy.deepcopy(pattern)
                        if type(shotRank) is list:
                            fCell[i].shotRank.extend(shotRank)
                        else:
                            fCell[i].shotRank = shotRank
                        fCell[i].nX = nX
                        fCell[i].nY = nY[i]
                        fCell[i].pitchX = pitchX
                        fCell[i].pitchY = pitchY
                        fCell[i].displacement = cell.displacement + np.array((0,i*dy),dtype=np.int32)
                        fCell[i].updateBoundary()
        else:
            raise ValueError('arrayFracture.resizeAxis() : The axis parameter must be either 0 or 1')
        return fCell

    def fieldFracture(self, cell, fieldSize=[200000,200000]):
        '''
        fieldFracture(cell, fieldSize=[200000,200000])
        
        Fractures an array pattern into fields
        
        Parameters
        ----------
        cell : ELD_Cell object
            A cell which contains an array of patterns
        fieldSize : A list of two integers
            The [width, height] of a field
            
        Returns
        -------
        fCell : a list of ELD_Cell            
            A list cells which contains the field decomposed array of patterns
        '''
        #Shifts the array pattern to origin to simplify the math
        cell.zeroPattern()
        cell.updateBoundary()
        
        #Determine the field positions within the boundaries of the pattern
        lC = int(cell.displacement[0]/fieldSize[0])
        uC = int((cell.boundary[4]+cell.displacement[0])/fieldSize[0])
        lR = int(cell.displacement[1]/fieldSize[1])
        uR = int((cell.boundary[5]+cell.displacement[1])/fieldSize[1])
        
        #Fracture horizontally first and store in rowList
        if cell.nY > 1:
            rowList = []
            tmp = cell
            hSlice = [cell]
            for j in range(lR+1,uR+1):
                hSlice = self.sliceAxis(tmp,j*fieldSize[1],axis=0)
                #All but the last cell does not need to be fractured further
                rowList.extend(hSlice[:-1])
                #The last cell may still need to be fractured
                tmp = hSlice[-1]
            rowList.extend(hSlice[-1:])
        else:
            rowList = [cell]
            

        #Fracture vertically and store in polyList
        polyList = []
        if cell.nX > 1:
            for i in rowList:
                tmp = i
                vSlice = [i]
                for j in range(lC+1,uC+1):
                    vSlice = self.sliceAxis(tmp,j*fieldSize[0],axis=1)
                    #All but the last cell does not need to be fractured further
                    polyList.extend(vSlice[:-1])
                    #The last cell may still need to be fractured
                    tmp = vSlice[-1]
                polyList.extend(vSlice[-1:])
        else:
            polyList = rowList
    
        return polyList   

    def sliceAxis(self, cell, position, axis = 0):
        '''
        sliceAxis(self, cell, position, axis = 0)
        
        Slices an array along an axis
        
        Parameters
        ----------
        cell : ELD_Cell object
            A cell which contains an array of patterns
        position : integer
            Specify the position to slice
        axis : 0 or 1
            Specify the axis to slice
            0   :   slice along x axis, horizontal slice
            1   :   slice along y axis, vertical slice
            
        Returns
        -------
        fCell : a list of 2 or 4 ELD_Cell object            
            A list two or 4 cells which contains the sliced array
            
        Description
        -----------
        This function slices an array along an axis
        '''
 
        if axis == 0:
            #Horizontal fracture line
            ly = cell.boundary[1] + cell.displacement[1]
            uy = cell.boundary[5] + cell.displacement[1]
            
            if position <= ly or position >= uy:
                #Field line is not inside the boundary of the array of pattern
                fCell = [cell]
            else:
                #tpos is used to determine if the line intersects a pattern
                tpos = position%cell.pitchY - cell.displacement[1]%cell.pitchY
                if tpos < 0:
                    tpos = cell.pitchY-tpos
                
                if tpos >= cell.boundary[3] or tpos <= cell.boundary[1]:
                    #The line is not slicing through a pattern, so we can split
                    #this cell into 2 cells
                    fCell = [copy.deepcopy(cell) for i in range(2)]
                    nY_1 = (position-cell.displacement[1])/cell.pitchY
                    if tpos >= cell.boundary[3]:
                        #If the line lies beyond a pattern, then increment the
                        #array count by 1
                        nY_1 += 1
                    nY_2 = cell.nY - nY_1
                    
                    fCell[0].nY = nY_1
                    fCell[1].nY = nY_2
                    
                    #Shift the origin of the second subarray
                    fCell[1].displacement[1] += cell.pitchY - tpos + (nY_1-1)*cell.pitchY
                    
                    [fCell[i].updateBoundary() for i in range(2)]
                else:
                    #The line is slicing through a pattern, so we must split
                    #this cell into 3 to 4 cells: left array, left pattern, right
                    #pattern, and right array
                    fCell = [copy.deepcopy(cell) for i in range(4)]
                    nY_1 = (position-cell.displacement[1])/cell.pitchY
                    nY_2 = 1
                    nY_3 = 1
                    nY_4 = cell.nY - nY_1 - 1
                    
                    fCell[0].nY = nY_1
                    fCell[1].nY = nY_2
                    fCell[2].nY = nY_3
                    fCell[3].nY = nY_4
                    
                    #Fracture the pattern along a verical line
                    [fCell[1].pattern[i].lineFracture(tpos,True) for i in range(len(fCell[1].pattern))]
                    fCell[2] = copy.deepcopy(fCell[1])

                    #Remove the patterns below the line
                    for i in fCell[1].pattern:
                        index = []
                        for j in range(len(i.xy)):
                            if all(i.xy[j][1::2] >= tpos):
                                index.append(j)
                        for j in index[::-1]:
                            i.xy.pop(j)
                         
                    #Remove the patterns above the line
                    for i in fCell[2].pattern:
                        index = []
                        for j in range(len(i.xy)):
                            if all(i.xy[j][1::2] <= tpos):
                                index.append(j)
                        for j in index[::-1]:
                            i.xy.pop(j)

                    fCell[1].displacement[1] += (nY_1)*cell.pitchY
                    fCell[2].displacement[1] += (nY_1)*cell.pitchY
                    fCell[3].displacement[1] += cell.pitchY + nY_1*cell.pitchY               

                    #If there is no pattern in the 4th cell, then delete it
                    if nY_4 == 0:
                        fCell.pop(3)
                    
                    [fCell[i].updateBoundary() for i in range(len(fCell))]
        else:
            #Vertical fracture line
            lx = cell.boundary[0] + cell.displacement[0]
            ux = cell.boundary[4] + cell.displacement[0]
            
            if position <= lx or position >= ux:
                fCell = [cell]
            else:
                #tpos is used to determine if the line intersects a pattern
                tpos = position%cell.pitchX - cell.displacement[0]%cell.pitchX
                if tpos < 0:
                    tpos = cell.pitchX-tpos
                
                if tpos >= cell.boundary[2] or tpos <= cell.boundary[0]:
                    #The line is not slicing through a pattern, so we can split
                    #this cell into 2 cells
                    fCell = [copy.deepcopy(cell) for i in range(2)]
                    nX_1 = (position-cell.displacement[0])/cell.pitchX
                    if tpos >= cell.boundary[2]:
                        nX_1 += 1
                    nX_2 = cell.nX - nX_1
                    
                    fCell[0].nX = nX_1
                    fCell[1].nX = nX_2
                    fCell[1].displacement[0] += cell.pitchX - tpos + (nX_1-1)*cell.pitchX
                    
                    [fCell[i].updateBoundary() for i in range(2)]
                else:
                    #The line is slicing through a pattern, so we must split
                    #this cell into 3 to 4 cells: left array, left pattern, right
                    #pattern, and right array
                    fCell = [copy.deepcopy(cell) for i in range(4)]
                    nX_1 = (position-cell.displacement[0])/cell.pitchX
                    nX_2 = 1
                    nX_3 = 1
                    nX_4 = cell.nX - nX_1 - 1
                    
                    fCell[0].nX = nX_1
                    fCell[1].nX = nX_2
                    fCell[2].nX = nX_3
                    fCell[3].nX = nX_4
                    
                    #Fracture the pattern along a verical line
                    [fCell[1].pattern[i].lineFracture(tpos,False) for i in range(len(fCell[1].pattern))]
                    fCell[2] = copy.deepcopy(fCell[1])

                    #Remove the patterns to the right of the line
                    for i in fCell[1].pattern:
                        index = []
                        for j in range(len(i.xy)):
                            if all(i.xy[j][0::2] >= tpos):
                                index.append(j)
                        for j in index[::-1]:
                            i.xy.pop(j)
                         
                    #Remove the patternsto the left of the line
                    for i in fCell[2].pattern:
                        index = []
                        for j in range(len(i.xy)):
                            if all(i.xy[j][0::2] <= tpos):
                                index.append(j)
                        for j in index[::-1]:
                            i.xy.pop(j)

                    fCell[1].displacement[0] += (nX_1)*cell.pitchX
                    fCell[2].displacement[0] += (nX_1)*cell.pitchX
                    fCell[3].displacement[0] += cell.pitchX + nX_1*cell.pitchX               

                    #If there is no pattern in the 4th cell, then delete it
                    if nX_4 == 0:
                        fCell.pop(3)                    
                    
                    [fCell[i].updateBoundary() for i in range(len(fCell))]
        
        return fCell

def test(debug = False):
    from ELD_Canvas import ELD_Canvas
    import matplotlib.pyplot as plot
    a = ELD_Canvas()
    a.addCell(2)
    #a.addPattern(2,[0,0,0,50,50,50,50,0,0,0],5)
    a.addPattern(2,[100,100,100,150,150,150,150,100,100,100],5)
    a.setCellArray(2,100,100,250,250)
    
    b = arrayFracture()
    c = b.resize(a.cell[0],100)
    d = b.fieldFracture(a.cell[0],[10000,10000])
    print c     
     
if __name__ == '__main__':
    test()