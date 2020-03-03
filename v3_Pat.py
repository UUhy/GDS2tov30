#!/usr/bin/env ipython

import numpy as np
from v3 import v3

class v3_Pat(v3):
    '''
    v3_Pat class : subclass of v3
    
    Pattern Data class for the Jeol v3.0 format
    
    The pattern data class stores the pattern specifications and shape 
    information.  This class provides methods to determine the compatibility
    of patterns with the Jeol v3.0 format and generates the binary pattern data
    block.
    
    The following methods are supported by the v3_Pat class:
       checkPrimitive:      Check if the pattern is compatible
       addPattern:          Adds patterns to the object
       setPatternArray:     Sets pattern array parameters
       genRecord:           Generates the binary record
    
    This class is constructed such that:
        1)  All patterns share the same shotrank if specified
        2)  All patterns are arrayed if specified
        3)  All patterns can be displaced by specifying the positionSet
            positionSet should only be used in a text block
    
    Long Chang, UH, May 2013
    '''

    def __init__(self):
        super(v3_Pat,self).__init__()
        self._blockBuffer = 100
        self._block = np.zeros(self._blockBuffer,dtype=np.uint8)
        self._blockIndex = 0
        self._blockSectionIndex = [0]
        self._nPat = 0
        self._lX = 0
        self._lY = 0
        self._nX = 1
        self._nY = 1
        self._positionSetX = -1
        self._positionSetY = -1
        self._shotRank = -1
        self._verticesBuffer = 10
        self._rectXS = np.zeros([1,4],dtype=np.uint16)
        self._rectXM = np.zeros([1,4],dtype=np.uint32)
        self._rectXL = np.zeros([1,4],dtype=np.uint32)
        self._rectYS = np.zeros([1,4],dtype=np.uint16)
        self._rectYM = np.zeros([1,4],dtype=np.uint32)
        self._rectYL = np.zeros([1,4],dtype=np.uint32)
        self._trapXS = np.zeros([1,6],dtype=np.uint32)
        self._trapXM = np.zeros([1,6],dtype=np.uint32)
        self._trapXL = np.zeros([1,6],dtype=np.uint32)
        self._trapYS = np.zeros([1,6],dtype=np.uint16)
        self._trapYM = np.zeros([1,6],dtype=np.uint32)
        self._trapYL = np.zeros([1,6],dtype=np.uint32)
        self._rectXSIndex = 0
        self._rectXMIndex = 0
        self._rectXLIndex = 0
        self._rectYSIndex = 0
        self._rectYMIndex = 0
        self._rectYLIndex = 0
        self._trapXSIndex = 0
        self._trapXMIndex = 0
        self._trapXLIndex = 0
        self._trapYSIndex = 0
        self._trapYMIndex = 0
        self._trapYLIndex = 0

        '''
        Opcodes
        -------
        0xFF##         Opcode
        X        x position (16-bit)
        XX        x position (32-bit)
        Y        y position
        W        width
        H        height
        S        shot rank
        '''
        self._cShotRank     = 0xFF05        #0xFF05 [S]
        self._cPositionSet  = 0xFFF1        #0xFFF1 [XX YY]
        self._cRecordEnd    = 0xFFF2        #0xFFF2
        self._cRectXS       = 0xFF00        #0xFF00 [X Y W H]
        self._cRectYS       = 0xFF01        #0xFF01 [X Y W H]
        self._cRectXM       = 0xFF06        #0xFF06 [X Y W H]
        self._cRectYM       = 0xFF07        #0xFF07 [X Y W H]
        self._cRectXL       = 0xFF10        #0xFF10 [XX YY WW HH]
        self._cRectYL       = 0xFF11        #0xFF11 [XX YY WW HH]
        self._cTrapXS       = 0xFF02        #0xFF02 [X1 Y1 X2 X3 X4 Y4]
        self._cTrapYS       = 0xFF03        #0xFF03 [X1 Y1 Y2 Y3 X4 Y4]
        self._cTrapXM       = 0xFF08        #0xFF08 [X1 Y1 X2 X3 X4 Y4]
        self._cTrapYM       = 0xFF09        #0xFF09 [X1 Y1 Y2 Y3 X4 Y4]
        self._cTrapXL       = 0xFF12        #0xFF12 [XX1 YY1 XX2 XX3 XX4 YY4]
        self._cTrapYL       = 0xFF13        #0xFF13 [XX1 YY1 YY2 YY3 XX4 YY4]
        self._cPatternCompactionMode8 = 0xFFE8      #0xFFE8 [Npt LLx LLy Nx Ny]
                                                    #    Npt = Number of patterns
                                                    #    LLx = Length of array along X (32-bits)
                                                    #    LLy = Length of array along Y (32-bits)
                                                    #    Nx  = Number of repeats along X
                                                    #    Ny  = Number of repeats along Y
        
        '''
        Parameter limitation
        '''
        self._c12 = 12                      #Identifies the shape is Small
        self._c16 = 16                      #Identifies the shape is Medium
        self._c20 = 20                      #Identifies the shape is Large
        
        self._r12_xy = 4095                  #Max value for a small xy position (small rectangle fom spec sheet)
        self._r12_wh = 511                   #Max value for a small wh length
        self._r16_x = 65279                 #Max value for the x position (arge rectangle from the spec sheet)
        self._r16_wyh = 65535                #Max value for the y position and wh length
        self._r20_xywh = 1048575             #This refers to the 20 bit rectangle from the spec shet
        self._t12_all = 4095
        self._t16_x1 = 65279
        self._t16_rest = 65535
        self._t20_all = 1048575
        
        '''
        Minimum bytes required for each opcode and parameters
            sShotRank = dShotRank + 2
            The +2 accounts for adding a cRecordEnd
        '''
        self._sShotRank = 4
        self._sPositionSet = 10
        self._sRectSM = 10
        self._sRectL = 18
        self._sTrapSM = 14
        self._sTrapL = 26
        self._dRectSM = 8
        self._dRectL = 16
        self._dTrapSM = 12
        self._dTrapL = 24
        self._sPatternCompactionMode8 = 16
        self._sMax = 28
            
    def __repr__(self):
        print 'shotRank:          ' , self.shotRank
        print 'nPat:              ' , self.nPat
        print 'nX:                ' , self.nX
        print 'nY:                ' , self.nY
        if self.nX < 2:
            print 'pitchX:            0'
        else:
            print 'pitchX:            ' , self.lX/(self.nX-1)
        if self.nY < 2:
            print 'pitchY:            0'
        else:
            print 'pitchY:            ' , self.lY/(self.nY-1)
        print 'rectXS:            ' , self.rectXSIndex
        print 'rectXM:            ' , self.rectXMIndex
        print 'rectXL:            ' , self.rectXLIndex
        print 'rectYS:            ' , self.rectYSIndex
        print 'rectYM:            ' , self.rectYMIndex
        print 'rectYL:            ' , self.rectYLIndex
        print 'trapXS:            ' , self.trapXSIndex
        print 'trapXM:            ' , self.trapXMIndex
        print 'trapXL:            ' , self.trapXLIndex
        print 'trapYS:            ' , self.trapYSIndex
        print 'trapYM:            ' , self.trapYMIndex
        print 'trapYL:            ' , self.trapYLIndex
        print 'numRect:           ' , self.numRect
        print 'numTrap:           ' , self.numTrap
        print 'numDecRect:        ' , self.numDecRect
        print 'numDecTrap:        ' , self.numDecTrap
        return ''

    @property
    def nPat(self):
        '''
        nPat : integer from 0 to 4095
            Number of patterns in te array
        '''
        return self._nPat
    
    @nPat.setter
    def nPat(self,val):
        if val < 0 or val > 4095:
            raise ValueError('v3_Pat.nPat : This parameter must range from 0 to 4095')
        self._nPat = val

    @property
    def lX(self):
        '''
        lX : integer from 0 to 1000000
            Distance between the first and last pattern in the array along X
        '''
        return self._lX

    @lX.setter
    def lX(self, val):
        if val < 0 or val >= 1000000:
            raise ValueError("v3_Pat.lX : The parameters nX*pX must range from 0 to 1000000")
        self._lX = val

    @property
    def lY(self):
        '''
        lx : integer from 0 to 1000000
            Distance between the first and last pattern in the array along Y
        '''
        return self._lY

    @lY.setter
    def lY(self, val):
        if val < 0 or val >= 1000000:
            raise ValueError("v3_Pat.lY : This parameters nY*pY must range from 0 to 1000000")
        self._lY = val

    @property
    def nX(self):
        '''
        nX : integer from 0 to 2047
            The number of repeats of the pattern in the array along X
        '''
        return self._nX

    @nX.setter
    def nX(self, val):
        if val < 0 or val >= 2047:
            raise ValueError("v3_Pat.nX : This parameter must range from 0 to 2047")
        self._nX = val

    @property
    def nY(self):
        '''
        nY : integer from 0 to 2047
            The number of repeats of the pattern in the array along Y
        '''
        return self._nY

    @nY.setter
    def nY(self, val):
        if val < 0 or val >= 2047:
            raise ValueError("v3_Pat.nY : The value for nY must be larger than 0")
        self._nY = val

    def checkPrimitive(self, vertices):
        '''
        checkPrimitives(vertices)
        
        Returns the type of primitive if the input shape is a Jeol v3.0 format primitive

        Parameters
        ----------
        vertices : numpy.ndarray of unsigned integers containing 4, 6 or 8 elements
                4 elements are used to specify a rectangle [x,y,w,h]
                6 elements are used to specify a triangle  [x1,y1,x2,y2,x3,y3]
                8 elements are used to specify a trapezoid [x1,y1,x2,y2,x3,y3,x4,y4]

        Returns
        -------
        cType : a string specifying the type of primitive
                ['RectXS', 'RectXM', 'RectXL', 'RectYS', 'RectYM', 'RectYL', 
                'TrapXS', 'TrapXM', 'TrapXL', 'TrapYS', 'TrapYM', 'TrapYL']
        trap : a formatted version of vertices to facilitate storage and conversion
        '''
        if not all(vertices >= 0):
                raise ValueError('v3_Pat.checkPrimitive() : The vertices parameter can not be negative')        
            
        if not isinstance(vertices,np.ndarray):
            raise TypeError('v3_Pat.checkPrimitive() : Vertices is not of type numpy.ndarray')
            
        if not vertices.size in [4,6,8]:
            raise ValueError('v3_Pat.checkPrimitive() : The vertices parameter must contain 4, 6, or 8 elements')

        if vertices.size == 8:
            #The elements of vertices is [X1 Y1 X2 Y2 X3 Y3 X4 Y4]
        
            #Determine if the base of the trapezoid is along X or Y
            tmp = np.append(vertices,vertices[0:2])
            isX = sum(np.diff(tmp[1::2]) == 0) == 2
            isY = sum(np.diff(tmp[0::2]) == 0) == 2
            tmp = vertices.reshape(4,2)
            
            #The trapezoid is not supported
            if not isX and not isY:
                raise ValueError('v3_Pat.checkPrimitives : The trapezoid does not have both base parallel to either the X or Y axis')
                
            #The trapezoid is a rectangle
            if isX and isY:
                x = min(tmp[:,0])
                y = min(tmp[:,1])
                w = max(tmp[:,0]) - x
                h = max(tmp[:,1]) - y
                trap = np.array([x,y,w,h],dtype=np.uint32)
                bitSize = self.getBitSize(trap)
                            
                if w >= h:
                    if bitSize is self.c12:
                        cType = self.cRectXS
                    elif bitSize is self.c16:
                        cType = self.cRectXM
                    elif bitSize is self.c20:
                        cType = self.cRectXL
                else:
                    if bitSize is self.c12:
                        cType = self.cRectYS
                    elif bitSize is self.c16:
                        cType = self.cRectYM
                    elif bitSize is self.c20:
                        cType = self.cRectYL
                        
                return cType, trap
            #The trapezoid has both base parallel to X axis
            elif isX:
                #Sort the vertices of the trapezoid
                iA = tmp[:,1] == min(tmp[:,1])
                iB = tmp[:,1] == max(tmp[:,1])
                i1 = (tmp[:,0] == min(tmp[iA,0])) * iA
                i2 = (tmp[:,0] == max(tmp[iA,0])) * iA
                i3 = (tmp[:,0] == max(tmp[iB,0])) * iB
                i4 = (tmp[:,0] == min(tmp[iB,0])) * iB
                trap = np.array([tmp[i1],tmp[i2],tmp[i3],tmp[i4]],dtype=np.uint32).ravel()

                theta1 = np.arctan(abs(int(trap[0])-int(trap[6]))/float(abs(int(trap[1])-int(trap[7]))))
                theta2 = np.arctan(abs(int(trap[2])-int(trap[4]))/float(abs(int(trap[3])-int(trap[5]))))

                if theta1 > np.pi/3:
                    raise ValueError('v3_Pat.checkPrimitive : X Trapezoid Theta1 cannot be larger than 60 degrees')
                if theta2 > np.pi/3:
                    raise ValueError('v3_Pat.checkPrimitive : X Trapezoid Theta2 cannot be larger than 60 degrees')

                bitSize = self.getBitSize(trap)
                if bitSize is self.c12:
                    cType = self.cTrapXS
                elif bitSize is self.c16:
                    cType = self.cTrapXM
                elif bitSize is self.c20:
                    cType = self.cTrapXL
                    
                return cType, trap[[0,1,2,4,6,7]]
            #The trapezoid has both base parallel to the Y axis
            elif isY:
                #Sort the vertices of the trapezoid
                iA = tmp[:,0] == min(tmp[:,0])
                iB = tmp[:,0] == max(tmp[:,0])
                i1 = (tmp[:,1] == min(tmp[iA,1])) * iA
                i2 = (tmp[:,1] == max(tmp[iA,1])) * iA
                i3 = (tmp[:,1] == max(tmp[iB,1])) * iB
                i4 = (tmp[:,1] == min(tmp[iB,1])) * iB
                trap = np.array([tmp[i1],tmp[i2],tmp[i3],tmp[i4]],dtype=np.uint32).ravel()

                theta1 = np.arctan(abs(int(trap[7])-int(trap[1]))/float(abs(int(trap[0])-int(trap[6]))))
                theta2 = np.arctan(abs(int(trap[3])-int(trap[5]))/float(abs(int(trap[2])-int(trap[4]))))

                if theta1 > np.pi/3:
                    raise ValueError('v3_Pat.checkPrimitive : Y Trapezoid Theta1 cannot be larger than 60 degrees')
                if theta2 > np.pi/3:
                    raise ValueError('v3_Pat.checkPrimitive : Y Trapezoid Theta2 cannot be larger than 60 degrees')
    
                bitSize = self.getBitSize(trap)
                if bitSize is self.c12:
                    cType = self.cTrapYS
                elif bitSize is self.c16:
                    cType = self.cTrapYM
                elif bitSize is self.c20:
                    cType = self.cTrapYL
                
                return cType, trap[[0,1,3,5,6,7]]
        elif vertices.size == 6:
            #The element of vertices is [X1 Y1 X2 Y2 X3 Y3]            
            
            #Determineof the base of the triangle is along X or Y
            tmp = np.append(vertices,vertices[0:2])
            isX = sum(np.diff(tmp[1::2]) == 0) == 1
            isY = sum(np.diff(tmp[0::2]) == 0) == 1
            tmp = vertices.reshape(3,2)

            if not isX and not isY:
                raise ValueError('v3_Pat.checkPrimitive : One edge of the triangle must be parallel to either the X or Y axis')

            #Right triangle
            if isX and isY:
                
                #Determine the base and height of a right triangle
                w = max(vertices[0::2])-min(vertices[0::2])
                h = max(vertices[1::2])-min(vertices[1::2])

                #X right triangle
                if h >= w:
                    #Sort the vertices
                    iA = tmp[:,1] == min(tmp[:,1])
                    iB = tmp[:,1] == max(tmp[:,1])
                    i1 = (tmp[:,0] == min(tmp[iA,0])) * iA
                    i2 = (tmp[:,0] == max(tmp[iA,0])) * iA
                    i3 = (tmp[:,0] == max(tmp[iB,0])) * iB
                    i4 = (tmp[:,0] == min(tmp[iB,0])) * iB
                    trap = np.array([tmp[i1],tmp[i2],tmp[i3],tmp[i4]],dtype=np.uint32).ravel()
                    
                    theta1 = np.arctan(abs(int(trap[0])-int(trap[6]))/float(abs(int(trap[1])-int(trap[7]))))
                    theta2 = np.arctan(abs(int(trap[2])-int(trap[4]))/float(abs(int(trap[3])-int(trap[5]))))

                    if theta1 > np.pi/3:
                        raise ValueError('v3_Pat.checkPrimitive : X Triangle Theta1 cannot be larger than 60 degrees')
                    if theta2 > np.pi/3:
                        raise ValueError('v3_Pat.checkPrimitive : X Triangle Theta2 cannot be larger than 60 degrees')
    
                    bitSize = self.getBitSize(trap)
                    if bitSize is self.c12:
                        cType = self.cTrapXS
                    elif bitSize is self.c16:
                        cType = self.cTrapXM
                    elif bitSize is self.c20:
                        cType = self.cTrapXL 

                    return cType, trap[[0,1,2,4,6,7]]
                    
                #Y right triangle
                else:
                    #Sort the vertices
                    iA = tmp[:,0] == min(tmp[:,0])
                    iB = tmp[:,0] == max(tmp[:,0])
                    i1 = (tmp[:,1] == min(tmp[iA,1])) * iA
                    i2 = (tmp[:,1] == max(tmp[iA,1])) * iA
                    i3 = (tmp[:,1] == max(tmp[iB,1])) * iB
                    i4 = (tmp[:,1] == min(tmp[iB,1])) * iB
                    trap = np.array([tmp[i1],tmp[i2],tmp[i3],tmp[i4]],dtype=np.uint32).ravel()
                
                    theta1 = np.arctan(abs(int(trap[7])-int(trap[1]))/float(abs(int(trap[0])-int(trap[6]))))
                    theta2 = np.arctan(abs(int(trap[3])-int(trap[5]))/float(abs(int(trap[2])-int(trap[4]))))

                    if theta1 > np.pi/3:
                        raise ValueError('v3_Pat.checkPrimitive : Y Triangle Theta1 cannot be larger than 60 degrees')
                    if theta2 > np.pi/3:
                        raise ValueError('v3_Pat.checkPrimitive : Y Triangle Theta2 cannot be larger than 60 degrees')
    
                    bitSize = self.getBitSize(trap)
                    if bitSize is self.c12:
                        cType = self.cTrapYS
                    elif bitSize is self.c16:
                        cType = self.cTrapYM
                    elif bitSize is self.c20:
                        cType = self.cTrapYL

                    return cType, trap[[0,1,3,5,6,7]]
                    
            #X triangle
            elif isX:
                #Sort the vertices
                iA = tmp[:,1] == min(tmp[:,1])
                iB = tmp[:,1] == max(tmp[:,1])
                i1 = (tmp[:,0] == min(tmp[iA,0])) * iA
                i2 = (tmp[:,0] == max(tmp[iA,0])) * iA
                i3 = (tmp[:,0] == max(tmp[iB,0])) * iB
                i4 = (tmp[:,0] == min(tmp[iB,0])) * iB
                trap = np.array([tmp[i1],tmp[i2],tmp[i3],tmp[i4]],dtype=np.uint32).ravel()
                    
                theta1 = np.arctan(abs(int(trap[6])-int(trap[0]))/float(abs(int(trap[1])-int(trap[7]))))
                theta2 = np.arctan(abs(int(trap[2])-int(trap[4]))/float(abs(int(trap[3])-int(trap[5]))))

                if theta1 > np.pi/3:
                    raise ValueError('v3_Pat.checkPrimitive : X Triangle Theta1 cannot be larger than 60 degrees')
                if theta2 > np.pi/3:
                    raise ValueError('v3_Pat.checkPrimitive : X Triangle Theta2 cannot be larger than 60 degrees')
    
                bitSize = self.getBitSize(trap)
                if bitSize is self.c12:
                    cType = self.cTrapXS
                elif bitSize is self.c16:
                    cType = self.cTrapXM
                elif bitSize is self.c20:
                    cType = self.cTrapXL

                return cType, trap[[0,1,2,4,6,7]]

            #Y triangle
            elif isY:
                #Sort the vertices
                iA = tmp[:,0] == min(tmp[:,0])
                iB = tmp[:,0] == max(tmp[:,0])
                i1 = (tmp[:,1] == min(tmp[iA,1])) * iA
                i2 = (tmp[:,1] == max(tmp[iA,1])) * iA
                i3 = (tmp[:,1] == max(tmp[iB,1])) * iB
                i4 = (tmp[:,1] == min(tmp[iB,1])) * iB
                trap = np.array([tmp[i1],tmp[i2],tmp[i3],tmp[i4]],dtype=np.uint32).ravel()

                theta1 = np.arctan(abs(int(trap[7])-int(trap[1]))/float(abs(int(trap[0])-int(trap[6]))))
                theta2 = np.arctan(abs(int(trap[3])-int(trap[5]))/float(abs(int(trap[2])-int(trap[4]))))

                if theta1 > np.pi/3:
                    raise ValueError('v3_Pat.checkPrimitive : Y Triangle Theta1 cannot be larger than 60 degrees')
                if theta2 > np.pi/3:
                    raise ValueError('v3_Pat.checkPrimitive : Y Triangle Theta2 cannot be larger than 60 degrees')

                bitSize = self.getBitSize(trap)
                if bitSize is self.c12:
                    cType = self.cTrapYS
                elif bitSize is self.c16:
                    cType = self.cTrapYM
                elif bitSize is self.c20:
                    cType = self.cTrapYL

                return cType, trap[[0,1,3,5,6,7]]

        #Rectangle
        elif vertices.size == 4:
            #The elements of vertices is [X Y W H]
        
            #Determine of the longest edge is along the X or Y axis
            isX = vertices[2] >= vertices[3]
            trap = vertices.astype(np.uint32)
            
            #X rectangle
            if isX:
                bitSize = self.getBitSize(trap)
                if bitSize is self.c12:
                    cType = self.cRectXS
                elif bitSize is self.c16:
                    cType = self.cRectXM
                elif bitSize is self.c20:
                    cType = self.cRectXL
                
            #Y rectangle
            else:
                bitSize = self.getBitSize(trap)
                if bitSize is self.c12:
                    cType = self.cRectYS
                elif bitSize is self.c16:
                    cType = self.cRectYM
                elif bitSize is self.c20:
                    cType = self.cRectYL
            
            return cType,trap
        
        raise ValueError('v3_Pat.checkPrimitive: An unaccounted error occurred')

    @property
    def c12(self):
        return self._c12
        
    @property
    def c16(self):
        return self._c16
    
    @property
    def c20(self):
        return self._c20

    def getBitSize(self, vertices):
        '''
        getBitSize(vertices)

        Returns a value either 12, 16 or 20 to specify the minimum number of 
        bits required to represent the vertices

        Parameters
        ----------
        vertices : a 1D numpy.ndarray

        Returns
        -------
        out : integer from the set [12,16,20]
        '''
        if any(vertices >= self._r20_xywh):
            raise ValueError("v3_Pat.getBitSize : The value for the input argument vertices cannot exceed 2^20 (1048576)")
        
        if vertices.size == 4:
            if not any(np.append(vertices[0:2] >= self._r12_xy,any(vertices[2:] >= self._r12_wh))):
                return self.c12
            elif not any(vertices >= self._r16_x):
                return self.c16
            else:
                return self.c20
        else:
            if not any(vertices >= self._t12_all):
                return self.c12
            elif not any(vertices >= self._t16_x1):
                return self.c16
            else:
                return self.c20
                
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
        if val < -1 or val >= 256:
            raise ValueError("v3_Pat.shotRank : This parameter must range from -1 to 255")
        self._shotRank = val
        self.maxShotRank = self._shotRank

    @property
    def rectXS(self):
        '''
        rectXS : numpy.ndarray of Nx4 elements
            The parameters of a 12-bit X rectangle
        '''
        return self._rectXS

    @rectXS.setter
    def rectXS(self,vertices):
        if self._rectXSIndex == self._rectXS.shape[0]:
            self._rectXS = np.append(self._rectXS,np.zeros((self._verticesBuffer,4),dtype=np.uint16),axis=0)
        self._rectXS[self._rectXSIndex] = vertices
        self._rectXSIndex += 1
        self.numRect += 1

    @property
    def rectXM(self):
        '''
        rectXM : numpy.ndarray of Nx4 elements
            The parameters of a 16-bit X rectangle
        '''
        return self._rectXM

    @rectXM.setter
    def rectXM(self,vertices):
        if self._rectXMIndex == self._rectXM.shape[0]:
            self._rectXM = np.append(self._rectXM,np.zeros((self._verticesBuffer,4),dtype=np.uint16),axis=0)        
        self._rectXM[self._rectXMIndex] = vertices
        self._rectXMIndex += 1
        self.numRect += 1

    @property
    def rectXL(self):
        '''
        rectXL : numpy.ndarray of Nx4 elements
            The parameters of a 20-bit X rectangle
        '''
        return self._rectXL

    @rectXL.setter
    def rectXL(self,vertices):
        if self._rectXLIndex == self._rectXL.shape[0]:
            self._rectXL = np.append(self._rectXL,np.zeros((self._verticesBuffer,4),dtype=np.uint32),axis=0)        
        self._rectXL[self._rectXLIndex] = vertices
        self._rectXLIndex += 1
        self.numRect += 1

    @property
    def rectYS(self):
        '''
        rectYS : numpy.ndarray of Nx4 elements
            The parameters of a 12-bit Y rectangle
        '''
        return self._rectYS

    @rectYS.setter
    def rectYS(self,vertices):
        if self._rectYSIndex == self._rectYS.shape[0]:
            self._rectYS = np.append(self._rectYS,np.zeros((self._verticesBuffer,4),dtype=np.uint16),axis=0)        
        self._rectYS[self._rectYSIndex] = vertices
        self._rectYSIndex += 1
        self.numRect += 1

    @property
    def rectYM(self):
        '''
        rectYM : numpy.ndarray of Nx4 elements
            The parameters of a 16-bit Y rectangle
        '''
        return self._rectYM

    @rectYM.setter
    def rectYM(self,vertices):
        if self._rectYMIndex == self._rectYM.shape[0]:
            self._rectYM = np.append(self._rectYM,np.zeros((self._verticesBuffer,4),dtype=np.uint16),axis=0)    
        self._rectYM[self._rectYMIndex] = vertices
        self._rectYMIndex += 1
        self.numRect += 1

    @property
    def rectYL(self):
        '''
        rectYL : numpy.ndarray of Nx4 elements
            The parameters of a 20-bit Y rectangle
        '''
        return self._rectYL

    @rectYL.setter
    def rectYL(self,vertices):
        if self._rectYLIndex == self._rectYL.shape[0]:
            self._rectYL = np.append(self._rectYL,np.zeros((self._verticesBuffer,4),dtype=np.uint32),axis=0)    
        self._rectYL[self._rectYLIndex] = vertices
        self._rectYLIndex += 1
        self.numRect += 1
    
    @property
    def trapXS(self):
        '''
        trapXS : numpy.ndarray of Nx6 elements
            The parameters of a 12-bit X trapezoid
        '''
        return self._trapXS

    @trapXS.setter
    def trapXS(self,vertices):
        if self._trapXSIndex == self._trapXS.shape[0]:
            self._trapXS = np.append(self._trapXS,np.zeros((self._verticesBuffer,6),dtype=np.uint16),axis=0)        
        self._trapXS[self._trapXSIndex] = vertices
        self._trapXSIndex += 1
        self.numTrap += 1

    @property
    def trapXM(self):
        '''
        trapXM : numpy.ndarray of Nx6 elements
            The parameters of a 16-bit X trapezoid
        '''
        return self._trapXM

    @trapXM.setter
    def trapXM(self,vertices):
        if self._trapXMIndex == self._trapXM.shape[0]:
            self._trapXM = np.append(self._trapXM,np.zeros((self._verticesBuffer,6),dtype=np.uint16),axis=0)        
        self._trapXM[self._trapXMIndex] = vertices
        self._trapXMIndex += 1
        self.numTrap += 1

    @property
    def trapXL(self):
        '''
        trapXL : numpy.ndarray of Nx6 elements
            The parameters of a 20-bit X trapezoid
        '''
        return self._trapXL

    @trapXL.setter
    def trapXL(self,vertices):
        if self._trapXLIndex == self._trapXL.shape[0]:
            self._trapXL = np.append(self._trapXL,np.zeros((self._verticesBuffer,6),dtype=np.uint32),axis=0)        
        self._trapXL[self._trapXLIndex] = vertices
        self._trapXLIndex += 1
        self.numTrap += 1

    @property
    def trapYS(self):
        '''
        trapYS : numpy.ndarray of Nx6 elements
            The parameters of a 12-bit Y trapezoid
        '''
        return self._trapYS

    @trapYS.setter
    def trapYS(self,vertices):
        if self._trapYSIndex == self._trapYS.shape[0]:
            self._trapYS = np.append(self._trapYS,np.zeros((self._verticesBuffer,6),dtype=np.uint16),axis=0)        
        self._trapYS[self._trapYSIndex] = vertices
        self._trapYSIndex += 1
        self.numTrap += 1

    @property
    def trapYM(self):
        '''
        trapYM : numpy.ndarray of Nx6 elements
            The parameters of a 16-bit Y trapezoid
        '''
        return self._trapYM

    @trapYM.setter
    def trapYM(self,vertices):
        if self._trapYMIndex == self._trapYM.shape[0]:
            self._trapYM = np.append(self._trapYM,np.zeros((self._verticesBuffer,6),dtype=np.uint16),axis=0)        
        self._trapYM[self._trapYMIndex] = vertices
        self._trapYMIndex += 1
        self.numTrap += 1

    @property
    def trapYL(self):
        '''
        trapYL : numpy.ndarray of Nx6 elements
            The parameters of a 20-bit Y trapezoid
        '''
        return self._trapYL

    @trapYL.setter
    def trapYL(self,vertices):
        if self._trapYLIndex == self._trapYL.shape[0]:
            self._trapYL = np.append(self._trapYL,np.zeros((self._verticesBuffer,6),dtype=np.uint32),axis=0)    
        self._trapYL[self._trapYLIndex] = vertices
        self._trapYLIndex += 1
        self.numTrap += 1

    @property
    def rectXSIndex(self):
        '''
        rectXSIndex : integer
            Tracks the number of rectXS and points to the next position in the rectXS numpy.ndarray
        '''
        return self._rectXSIndex

    @property
    def rectXMIndex(self):
        '''
        rectXMIndex : integer
            Tracks the number of rectXM and points to the next position in the rectXM numpy.ndarray
        '''
        return self._rectXMIndex

    @property
    def rectXLIndex(self):
        '''
        rectXLIndex : integer
            Tracks the number of rectXL and points to the next position in the rectXL numpy.ndarray
        '''
        return self._rectXLIndex

    @property
    def rectYSIndex(self):
        '''
        rectYSIndex : integer
            Tracks the number of rectYS and points to the next position in the rectYS numpy.ndarray
        '''
        return self._rectYSIndex

    @property
    def rectYMIndex(self):
        '''
        rectYMIndex : integer
            Tracks the number of rectYM and points to the next position in the rectYM numpy.ndarray
        '''
        return self._rectYMIndex

    @property
    def rectYLIndex(self):
        '''
        rectYLIndex : integer
            Tracks the number of rectYL and points to the next position in the rectYL numpy.ndarray
        '''
        return self._rectYLIndex

    @property
    def trapXSIndex(self):
        '''
        trapXSIndex : integer
            Tracks the number of trapXS and points to the next position in the trapXS numpy.ndarray
        '''
        return self._trapXSIndex

    @property
    def trapXMIndex(self):
        '''
        trapXMIndex : integer
            Tracks the number of trapXM and points to the next position in the trapXM numpy.ndarray
        '''
        return self._trapXMIndex

    @property
    def trapXLIndex(self):
        '''
        trapXLIndex : integer
            Tracks the number of trapXL and points to the next position in the trapXL numpy.ndarray
        '''
        return self._trapXLIndex

    @property
    def trapYSIndex(self):
        '''
        trapYSIndex : integer
            Tracks the number of trapYS and points to the next position in the trapYS numpy.ndarray
        '''
        return self._trapYSIndex

    @property
    def trapYMIndex(self):
        '''
        trapYMIndex : integer
            Tracks the number of trapYM and points to the next position in the trapYM numpy.ndarray
        '''
        return self._trapYMIndex

    @property
    def trapYLIndex(self):
        '''
        trapYLIndex : integer
            Tracks the number of trapYL and points to the next position in the trapYL numpy.ndarray
        '''
        return self._trapYLIndex

    def addPattern(self, vertices, shotRank=-1):
        '''
        addPattern(vertices)

        Adds a list of vertices to the v3_Pat object

        Parameters
        ----------
        vertices : a list of numpy.ndarray
                Each list element should contain an np.ndarray of size 4, 6 or 8 elements
        shotRank : a value from 0 to 255
                The shot rank value of all shapes in this object
                    -1  =   No shot rank
        
        Returns
        -------
        nothing
        '''
        if shotRank >= 0:    self.shotRank = shotRank

        for i in vertices:
            cType,trap = self.checkPrimitive(i)
            if   cType is self.cRectXS:
                self.rectXS = trap
            elif cType is self.cRectXM:
                self.rectXM = trap
            elif cType is self.cRectXL:
                self.rectXL = trap
            elif cType is self.cRectYS:
                self.rectYS = trap
            elif cType is self.cRectYM:
                self.rectYM = trap
            elif cType is self.cRectYL:
                self.rectYL = trap
            elif cType is self.cTrapXS:
                self.trapXS = trap
            elif cType is self.cTrapXM:
                self.trapXM = trap
            elif cType is self.cTrapXL:
                self.trapXL = trap
            elif cType is self.cTrapYS:
                self.trapYS = trap
            elif cType is self.cTrapYM:
                self.trapYM = trap
            elif cType is self.cTrapYL:
                self.trapYL = trap
        
        self.numDecRect = self.numRect*self.nX*self.nY
        self.numDecTrap = self.numTrap*self.nX*self.nY

    def setPatternArray(self, pX, pY, nX, nY):
        '''
        setPatternArray(pX,pY,nX,nY)

        Sets the parameters to array all patterns in the object

        Parameters
        ----------
        pX : integer
            The distance between neighboring patterns in the array along X
        pY : integer
            The distance between neighboring patterns in the array along Y
        nX : integer from 0 to 2047
            The number of repeats of the patterns in the array along X
        nY : integer from 0 to 2047
            The number of repeats of the patterns in the array along Y

        '''
        self.lX = pX*(nX-1)
        self.lY = pY*(nY-1)
        self.nX = nX
        self.nY = nY
        
        self.numDecRect = self.numRect*self.nX*self.nY
        self.numDecTrap = self.numTrap*self.nX*self.nY
        
    def setPatternPosition(self, x=0, y=0):
        '''
        setPatternPosition(x=0, y=0)
        '''
        self.positionSetX = x
        self.positionSetY = y

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
            raise ValueError('v3_Pat.positionSetX : This parameter must range from 0 to 2,000,000')
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
            raise ValueError('v3_Pat.positionSetY : This parameter must range from 0 to 2,000,000')
        self._positionSetY = val

    @property
    def cShotRank(self):
        '''
        cShotRank : 0xFF05
            Opcode for shotrank
        '''
        return self._cShotRank

    @property
    def cPositionSet(self):
        '''
        cPositionSet : 0xFFF1
            Opcode for position set
        '''
        return self._cPositionSet        
        
    @property
    def cRecordEnd(self):
        return self._cRecordEnd

    @property
    def cRectXS(self):
        return self._cRectXS

    @property
    def cRectXM(self):
        return self._cRectXM

    @property
    def cRectXL(self):
        return self._cRectXL

    @property
    def cRectYS(self):
        return self._cRectYS

    @property
    def cRectYM(self):
        return self._cRectYM

    @property
    def cRectYL(self):
        return self._cRectYL

    @property
    def cTrapXS(self):
        return self._cTrapXS

    @property
    def cTrapXM(self):
        return self._cTrapXM

    @property
    def cTrapXL(self):
        return self._cTrapXL

    @property
    def cTrapYS(self):
        return self._cTrapYS

    @property
    def cTrapYM(self):
        return self._cTrapYM

    @property
    def cTrapYL(self):
        return self._cTrapYL

    @property
    def cPatternCompactionMode8(self):
        return self._cPatternCompactionMode8

    @property
    def sShotRank(self):
        return self._sShotRank
        
    @property
    def sPositionSet(self):
        return self._sPositionSet
        
    @property
    def sRectSM(self):
        return self._sRectSM
    
    @property
    def sRectL(self):
        return self._sRectL
        
    @property
    def sTrapSM(self):
        return self._sTrapSM
    
    @property
    def sTrapL(self):
        return self._sTrapL
        
    @property
    def dRectSM(self):
        return self._dRectSM
    
    @property
    def dRectL(self):
        return self._dRectL
        
    @property
    def dTrapSM(self):
        return self._dTrapSM
    
    @property
    def dTrapL(self):
        return self._dTrapL
        
    @property
    def sPatternCompactionMode8(self):
        return self._sPatternCompactionMode8

    @property
    def sMax(self):
        return self._sMax

    def blockFracture(self,offset,cType):
        '''
        blockFracture(offset,cType)
        
        Determines if the block should be fractured to fit in a record
        
        Parameters
        ----------
        offset : integer from 0 to 4096
        
        cType : string
        
        Returns
        -------
        offset : integer from 0 to 4096
            New offset position
        
        reset : boolean
            Indicate if a offset was reset
            
        Note
        -----------
        This function could be improved to better fill a block by using the
        actual length of each opCode instead of the maximum length of all
        opCodes (sMax).
        '''

        if self.maxRecordSize < offset + self.sMax:
            self.block = self.dec2bin(self.cRecordEnd)
            self.blockSectionIndex = self.blockIndex
            if not (cType is self.cShotRank or cType is self.cPatternCompactionMode8):
                self.block = self.dec2bin(cType)
            offset = 0
            return offset, True
        return offset, False

    def genRecord(self,offset=0):
        '''
        genRecord(offset=0)
        
        Generates the binary pattern data
        
        Parameters
        ----------
        offset : integer from 0 to 4096
            The position in a record.
            Since a record has a fixed size of 2048 words, the blocks must be
            generated properly to avoid overflow.
        
        Results
        -------
        offset : integer from 0 to 4096
            The position in a record after adding this pattern data block
        
        Description
        -----------
        Generates the binary pattern data block from the pattern data.  The
        syntax for the pattern data block is:
        <Pattern Data Block> =  <Position Set?><Shot Rank?><Pattern Compaction?>
                                <RectXS?><RectXM?><RectXL?><RectYS?><RectYM?>
                                <RectYL?><TrapXS?><TrapXM?><TrapXL?><TrapYS?>
                                <TrapYM?><TrapYL?>
        A '?' means that the block is optional
        '''

        if offset < 0 or offset > self.maxRecordSize:
            raise ValueError('v3_Pat.genRecord : The offset parameter must range from 0 to 4096')
        
        self._block = np.zeros(self._blockBuffer,dtype=np.uint8)
        self._blockIndex = 0
        self._blockSectionIndex = [0]

        #Position Set
        if self.positionSetX >= 0 and self.positionSetY >= 0:
            offset, reset = self.blockFracture(offset,self.cPositionSet)
            self.block = self.dec2bin(self.cPositionSet)
            self.block = self.dec2bin(self.positionSetX,4)
            self.block = self.dec2bin(self.positionSetY,4)
            offset += self.sPositionSet
        
        #Shot rank value
        offset, reset = self.blockFracture(offset,self.cShotRank)
        if self.shotRank >= 0:
            self.block = self.dec2bin(self.cShotRank)
            self.block = self.dec2bin(self.shotRank)
            offset += self.sShotRank
            
        #Pattern compaction mode 8
        if self.nX*self.nY > 1:
            self.nPat = self.numRect + self.numTrap
            self.numDecRect = self.numRect*self.nX*self.nY
            self.numDecTrap = self.numTrap*self.nX*self.nY
            offset, reset = self.blockFracture(offset,self.cPatternCompactionMode8)
            self.block = self.dec2bin(self.cPatternCompactionMode8)
            self.block = self.dec2bin(self.nPat)
            self.block = self.dec2bin(self.lX,4)
            self.block = self.dec2bin(self.lY,4)
            self.block = self.dec2bin(self.nX)
            self.block = self.dec2bin(self.nY)
            offset += self.sPatternCompactionMode8
            
        #Shapes
        if self.rectXSIndex > 0:
            offset, reset = self.blockFracture(offset,self.cRectXS)
            if not reset:
                self.block = self.dec2bin(self.cRectXS)
            offset += 2
            for i in range(self.rectXSIndex):
                if i > 0:
                    offset, reset = self.blockFracture(offset,self.cRectXS)
                self.block = np.array([self.dec2bin(self.rectXS[i,0]),
                        self.dec2bin(self.rectXS[i,1]),
                        self.dec2bin(self.rectXS[i,2]),
                        self.dec2bin(self.rectXS[i,3])],dtype=np.uint8).ravel()
                offset += self.dRectSM
        if self.rectXMIndex > 0:
            offset, reset = self.blockFracture(offset,self.cRectXM)
            if not reset:
                self.block = self.dec2bin(self.cRectXM)
            offset += 2
            for i in range(self.rectXMIndex):
                if i > 0:
                    offset, reset = self.blockFracture(offset,self.cRectXM)
                self.block = np.array([self.dec2bin(self.rectXM[i,0]),
                        self.dec2bin(self.rectXM[i,1]),
                        self.dec2bin(self.rectXM[i,2]),
                        self.dec2bin(self.rectXM[i,3])],dtype=np.uint8).ravel()
                offset += self.dRectSM
        if self.rectXLIndex > 0:
            offset, reset = self.blockFracture(offset,self.cRectXL)
            if not reset:
                self.block = self.dec2bin(self.cRectXL)
            offset += 2
            for i in range(self.rectXLIndex):
                if i > 0:
                    offset, reset = self.blockFracture(offset,self.cRectXL)
                self.block = np.array([self.dec2bin(self.rectXL[i,0],4),
                        self.dec2bin(self.rectXL[i,1],4),
                        self.dec2bin(self.rectXL[i,2],4),
                        self.dec2bin(self.rectXL[i,3],4)],dtype=np.uint8).ravel()
                offset += self.dRectL
        if self.rectYSIndex > 0:
            offset, reset = self.blockFracture(offset,self.cRectYS)
            if not reset:
                self.block = self.dec2bin(self.cRectYS)
            offset += 2
            for i in range(self.rectYSIndex):
                if i > 0:
                    offset, reset = self.blockFracture(offset,self.cRectYS)
                self.block = np.array([self.dec2bin(self.rectYS[i,0]),
                        self.dec2bin(self.rectYS[i,1]),
                        self.dec2bin(self.rectYS[i,2]),
                        self.dec2bin(self.rectYS[i,3])],dtype=np.uint8).ravel()
                offset += self.dRectSM
        if self.rectYMIndex > 0:
            offset, reset = self.blockFracture(offset,self.cRectYM)
            if not reset:
                self.block = self.dec2bin(self.cRectYM)
            offset += 2
            for i in range(self.rectYMIndex):
                if i > 0:
                    offset, reset = self.blockFracture(offset,self.cRectYM)
                self.block = np.array([self.dec2bin(self.rectYM[i,0]),
                        self.dec2bin(self.rectYM[i,1]),
                        self.dec2bin(self.rectYM[i,2]),
                        self.dec2bin(self.rectYM[i,3])],dtype=np.uint8).ravel()
                offset += self.dRectSM
        if self.rectYLIndex > 0:
            offset, reset = self.blockFracture(offset,self.cRectYL)
            if not reset:
                self.block = self.dec2bin(self.cRectYL)
            offset += 2
            for i in range(self.rectYLIndex):
                if i > 0:
                    offset, reset = self.blockFracture(offset,self.cRectYL)
                self.block = np.array([self.dec2bin(self.rectYL[i,0],4),
                        self.dec2bin(self.rectYL[i,1],4),
                        self.dec2bin(self.rectYL[i,2],4),
                        self.dec2bin(self.rectYL[i,3],4)],dtype=np.uint8).ravel()
                offset += self.dRectL
        if self.trapXSIndex > 0:
            offset, reset = self.blockFracture(offset,self.cTrapXS)
            if not reset:
                self.block = self.dec2bin(self.cTrapXS)
            offset += 2
            for i in range(self.trapXSIndex):
                if i > 0:
                    offset, reset = self.blockFracture(offset,self.cTrapXS)
                self.block = np.array([self.dec2bin(self.trapXS[i,0]),
                        self.dec2bin(self.trapXS[i,1]),
                        self.dec2bin(self.trapXS[i,2]),
                        self.dec2bin(self.trapXS[i,3]),
                        self.dec2bin(self.trapXS[i,4]),
                        self.dec2bin(self.trapXS[i,5])],dtype=np.uint8).ravel()
                offset += self.dTrapSM
        if self.trapXMIndex > 0:
            offset, reset = self.blockFracture(offset,self.cTrapXM)
            if not reset:
                self.block = self.dec2bin(self.cTrapXM)
            offset += 2
            for i in range(self.trapXMIndex):
                if i > 0:
                    offset, reset = self.blockFracture(offset,self.cTrapXM)
                self.block = np.array([self.dec2bin(self.trapXM[i,0]),
                        self.dec2bin(self.trapXM[i,1]),
                        self.dec2bin(self.trapXM[i,2]),
                        self.dec2bin(self.trapXM[i,3]),
                        self.dec2bin(self.trapXM[i,4]),
                        self.dec2bin(self.trapXM[i,5])],dtype=np.uint8).ravel()
                offset += self.dTrapSM
        if self.trapXLIndex > 0:
            offset, reset = self.blockFracture(offset,self.cTrapXL)
            if not reset:
                self.block = self.dec2bin(self.cTrapXL)
            offset += 2
            for i in range(self.trapXLIndex):
                if i > 0:
                    offset, reset = self.blockFracture(offset,self.cTrapXL)
                self.block = np.array([self.dec2bin(self.trapXL[i,0],4),
                        self.dec2bin(self.trapXL[i,1],4),
                        self.dec2bin(self.trapXL[i,2],4),
                        self.dec2bin(self.trapXL[i,3],4),
                        self.dec2bin(self.trapXL[i,4],4),
                        self.dec2bin(self.trapXL[i,5],4)],dtype=np.uint8).ravel()
                offset += self.dTrapL
        if self.trapYSIndex > 0:
            offset, reset = self.blockFracture(offset,self.cTrapYS)
            if not reset:
                self.block = self.dec2bin(self.cTrapYS)
            offset += 2
            for i in range(self.trapYSIndex):
                if i > 0:
                    offset, reset = self.blockFracture(offset,self.cTrapYS)
                self.block = np.array([self.dec2bin(self.trapYS[i,0]),
                        self.dec2bin(self.trapYS[i,1]),
                        self.dec2bin(self.trapYS[i,2]),
                        self.dec2bin(self.trapYS[i,3]),
                        self.dec2bin(self.trapYS[i,4]),
                        self.dec2bin(self.trapYS[i,5])],dtype=np.uint8).ravel()
                offset += self.dTrapSM
        if self.trapYMIndex > 0:
            offset, reset = self.blockFracture(offset,self.cTrapYM)
            if not reset:
                self.block = self.dec2bin(self.cTrapYM)
            offset += 2
            for i in range(self.trapYMIndex):
                if i > 0:
                    offset, reset = self.blockFracture(offset,self.cTrapYM)
                self.block = np.array([self.dec2bin(self.trapYM[i,0]),
                        self.dec2bin(self.trapYM[i,1]),
                        self.dec2bin(self.trapYM[i,2]),
                        self.dec2bin(self.trapYM[i,3]),
                        self.dec2bin(self.trapYM[i,4]),
                        self.dec2bin(self.trapYM[i,5])],dtype=np.uint8).ravel()
                offset += self.dTrapSM
        if self.trapYLIndex > 0:
            offset, reset = self.blockFracture(offset,self.cTrapYL)
            if not reset:
                self.block = self.dec2bin(self.cTrapYL)
            offset += 2
            for i in range(self.trapYLIndex):
                if i > 0:
                    offset, reset = self.blockFracture(offset,self.cTrapYL)
                self.block = np.array([self.dec2bin(self.trapYL[i,0],4),
                        self.dec2bin(self.trapYL[i,1],4),
                        self.dec2bin(self.trapYL[i,2],4),
                        self.dec2bin(self.trapYL[i,3],4),
                        self.dec2bin(self.trapYL[i,4],4),
                        self.dec2bin(self.trapYL[i,5],4)],dtype=np.uint8).ravel()
                offset += self.dTrapL
        self.clipBlock()
        return offset
   
def test():
    '''
    test()
    
    Performs a diagnosis of the v3_Pat class
    '''
    a = v3_Pat()
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
    
#    for i in v1:
#        print a.checkPrimitive(i)
#    for i in v2:
#        print a.checkPrimitive(i)
#    for i in v3:
#        print a.checkPrimitive(i)
#    for i in v4:
#        print a.checkPrimitive(i)
#    for i in v5:
#        print a.checkPrimitive(i)
    
    a.addPattern(v1)
    a.addPattern(v2)
    a.addPattern(v3)
    a.addPattern(v4)
    a.addPattern(v5)
    a.setPatternArray(100,100,1000,1000)
    a.genRecord(4040)
    print a
    print a.block[a.blockSectionIndex[0]:a.blockSectionIndex[1]]
    print a.block[a.blockSectionIndex[1]:]

if __name__ == '__main__':
    test()
