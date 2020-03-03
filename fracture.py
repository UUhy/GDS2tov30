#!/usr/bin/env ipython

import numpy as np

class fracture(object):  
    '''
    fracture class : subclass of object
    
    The fracture class is used to decompose a non-self-intersecting polygon
    by slicing it along the x or y axis.
    
    The fracture class require polygons to be specified as:
        1)  [x0, y0, x1, y1...xn, yn, x0, y0]
        2)  Same as 1, but as an Nx2 numpy.ndarray
    Most functions require the polygon to be represented as (2) for ease of
    manipulation.  (1) is a convenient for compatibility with other classes
    such as the GDSII class and the ELD class
    
    The fracture class supports the following functions:
        fracture                =   fracture polygon to trapezoids, rectangles,
                                    and triangles
        recursiveXY             =   recursively fracture along x and y
        trapezoidalize          =   fracture into trapezoids
        recursiveSlice          =   recursively slice polygon into trapezoids
        slicePolygon            =   slice polygon along x or y
        isInsidePoly            =   check if point is inside a polygon
        isInsidePolyByPoint     =   check if point is inside poly
        isEdgePoly              =   check if point is on the edge of a polygon
        fieldFracture           =   fracture polygon along all field lines
        sliceField              =   slice polygon along a single field line
        recursiveSlicePoint     =   recursively slice polygon along a line
        slicePoint              =   slice polygon along a line
        insertVertex            =   inserts a vertex into a polygon
        checkPrimitive          =   check if a shape is a primitive
           
    Note:  This algorithm does not work on complex/self-intersecting polygons.
    A non-obvious example is when the vertex/edge of a polygon lies on another
    vertex/edge of the same polygon.  It is impossible to tell whether an 
    intersection exists.  In this case, the algorithm also fails.
           
    Long Chang, UH, August 2013
    '''
    
    def __init__(self):
        self._eps = .1
        
    def __repr__(self):
        print 'fracture object'
        print 'eps :    ' , self.eps
        return ''
        
    @property
    def eps(self):
        '''
        eps : float
            Specify a value smaller than the resolution of a pixel
            The eps is used to determine if a point is inside a polygon
        '''
        return self._eps
        
    @eps.setter
    def eps(self, val):
        self._eps = val
    
    def fracture(self, xy):
        '''
        fracture(xy)
        
        Fractures all polygons into primitives (trapezoids, rectangles, triangles)
        
        Parameters
        ----------
        xy : list of Nx1 numpy.ndarray
            The list of polygons to be fractured
            
        Returns
        -------
        parts : list of Nx1 numpy.ndarray
            The list of the decomposed polygons
        
        Description
        -----------
        The fracture algorithm does the following:
        1)  Trapezoidalize horizontally
        2)  Trapezoidalize vertically if not primitive
        3)  TrapezoidalizeXY recursively until primitive or square area <= 10
        
        Note
        ----
        Round or Ceil or Floor determines whether or not some polygons will
            survive step 3.
        
        Speed
        -----
        6.75 seconds to fracture a microfluid channel with 1388 vertices
        '''
        parts = []
        #Split polygon into horizontal trapezoids
        for j in xy:
            hparts = self.trapezoidalize(j)
            hparts = [np.round(i) for i in hparts]
            #Check each trapezoid and fracture vertically if needed
            for k in hparts:
                isPrimitive, failLog = self.checkPrimitive(k[:-2])
                if isPrimitive:
                    parts.append(k)
                else:
                    vparts = self.trapezoidalize(k,False)
                    vparts = [np.round(i) for i in vparts]
                    for l in vparts:
                        isPrimitive, failLog = self.checkPrimitive(l[:-2])
                        if isPrimitive:
                            parts.append(l)
                        else:
                            parts.extend(self.recursiveXY(l))
        return parts     
   
    def recursiveXY(self, xy, horizontal=True):
        '''
        recursiveXY(xy, horizontal=True)
        
        Returns the decomposed polygon by slicing alternating X Y
        
        Parameters
        ----------
        xy : Nx1 numpy.ndarray
            A polygon specified as [x0, y0, x1, y1...xn, yn, x0, y0]
            
        horizontal : boolean
            Specify first slicing direction
            
        Returns
        -------
        primList : list of Nx1 numpy.ndarray
            A list of the decomposed polygon
            
        Description
        -----------
        The recursiveXY algorithm is as follows:
        1)  Trapezoidalize along X or Y
        2)  Check all trapezoids
            a)  If yes, return
            b)  If no, go to step 1 and switch slice axis
        '''
        primList = []
        tmp = self.trapezoidalize(xy,horizontal)
        tmp = [np.round(i) for i in tmp]
        for i in range(len(tmp)):
            isPrimitive, failLog = self.checkPrimitive(tmp[i][:-2])
            if isPrimitive:
                primList.append(tmp[i])
            else:
                if (tmp[i][::2].max()-tmp[i][::2].min())*(tmp[i][1::2].max()-tmp[i][1::2].min()) > 10:
                    if not np.any(np.logical_and(np.diff(tmp[i][::2])==0,np.diff(tmp[i][1::2])==0)):
                        primList.extend(self.recursiveXY(tmp[i],not horizontal))
        return primList   
   
    def trapezoidalize(self, xy, horizontal=True):
        '''
        trapezoidalize(xy)
        
        Returns a set of trapezoids composing the polygon
        
        Parameters
        ----------
        xy : A list of integers/float or an Nx1 numpy.ndarray
            A polygon represented as a list of vertices in the form:
            [x0, y0, x1, y1, x2, y3, ... xn, yn, x0, y0]
        
        Returns
        -------
        trapezoids : a list of Nx1 numpy.ndarray of type numpy.float
            A list of trapezoids composing the polygon
            The vertices of each trapezoid has the form
                [x0 y0 x1 y1 x2 y2 x3 y3 x0 y0] or
                [x0 y0 x1 y1 x2 y2 x0 y0]
                
        Description
        -----------
        The trapezoidalize algorithm is as follows:
        1)  Ensure the proper datatype for the input parameter xy
        2)  Run recursiveSlice
        3)  Return results
                
        Speed
        -----
        NCalls  Vertices    Time/Call[s]    TimeTotal[s] 
        1000    11          0.009           8.746
        1000    20          0.014           14.035
        1000    50          0.030           30.494
        1000    200         0.149           149.003
        1       1388        5.298
        '''
        if type(xy) is list:
            if len(xy)%2 == 1:
                raise ValueError('fracture.trapezoidalize : The input xy must contain an even number of elements')
            elif xy[0:2] != xy[-2:]:
                xy = np.reshape(np.array(xy.extend(xy[0:2]),dtype=np.float),(len(xy)/2,2))
            else:
                xy = np.reshape(np.array(xy,dtype=np.float),(len(xy)/2,2))
        elif type(xy) is np.ndarray:
            if len(xy.shape) == 1:
                if xy.size%2 == 1:
                    raise ValueError('fracture.trapezoidalize : The input xy must contain an even number of elements')
                elif np.all(xy[0:2] != xy[-2:]):
                    xy = np.append(xy,xy[0:2],axis=0)
                    xy = np.reshape(xy,(xy.size/2,2))
                else:
                    xy = np.reshape(xy,(xy.size/2,2))
            else:
                if np.all(xy[0] != xy[-1]):
                    xy = np.append(xy,xy[0])
            if xy.dtype != np.float:
                xy = xy.astype(np.float)
        else:
            raise TypeError('facture.trapezoidalize : The input xy must be a list of integers')
        
        trapezoids = self.recursiveSlice(xy,horizontal)
    
        for i in range(len(trapezoids)):
            trapezoids[i] = trapezoids[i].ravel()
    
        return trapezoids

    def recursiveSlice(self, xy, horizontal=True):
        '''
        recursiveSlice(xy)
        
        Returns the polygon decomposed into trapezoids
        
        Parameters
        ----------
        xy : Nx2 numpy.ndarray
            The polygon represented as an array of ordered vertices
            
        Returns
        -------
        trapList : list of Nx2 numpy.ndarray
            A list of trapezoids
            
        Description
        -----------
        The recursiveSlice algorithm is as follows:
        1)  Slice polygon into 2 pieces
            a)  Number of vertices < 6
                i)  True    : return
                ii) False   : send polygon to 1
        '''
        trapList = []
        
        if horizontal:
            dy = np.diff(xy[:,1]) == 0
        else:
            dy = np.diff(xy[:,0]) == 0
            
        if xy.shape[0] < 6 and sum(dy) == 2:
            return [xy]
        elif xy.shape[0] < 5 and np.any(dy):
            return [xy]
        else:
            for i in range(xy.shape[0]):
                try:
                    s1,s2 = self.slicePolygon(i,xy,horizontal)
                    tmp = self.recursiveSlice(s1,horizontal)
                    trapList.extend(tmp)
                    tmp = self.recursiveSlice(s2,horizontal)
                    trapList.extend(tmp)
                    break
                except:
                    pass
                    
        return trapList
        
    def slicePolygon(self, pointIndex, xy, horizontal = True):
        '''
        slicePolygon(pointIndex, xy, horizontal = True)
        
        Slices a polygon into two sub-polygons
        
        Parameters
        ----------
        pointIndex : integer
            An integer specifying the vertex to slice            
            
        xy : Nx2 numpy.ndarray
            An array of points representing a polygon
            
        horizontal : boolean
            Slice horizontally (true) or vertically (false)
            Slicing vertically takes more time since xy is changed to yx before
                slicing horizontally and then yx is changed back to xy
                Vertical slicing can be sped up by independent implementation
                
        Results
        -------
        slice1 : Nx2 numpy.ndarray
            An array of points representing one slice of the polygon
        
        slice2 : Nx2 numpy.ndarry
            An array of points representing the other slice of the polygon
            
        Description
        -----------
        The algorithm is as follows:
        1)  Determine if the point_x+eps is inside the polygon and not on the edge
            True  : Determine every edge crossed by moving point_x along +x axis
            False : Go to step 3
        2)  Determine index of nearest edge by comparing x-intercept
            Go to step 4
        3)  Determine if the point_x-eps is inside the polygon and not on the edge
            True  : Determine every edge crossed by moving point_x along -x axis
                    Go to step 2
            False : Raise a ValueError
        4)  Split the input polygon into two polygon (slices)
        5)  Remove duplicate points in the two slices
        6)  Remove duplicate colinear points in the two slices
        7)  Return the two slices
        
        Speed
        -----
        N       Time[s]     Type
        201     0.240       Horizontal
        201     0.265       Vertical
        1001    2.959       Horizontal
        1001    3.177       Vertical
        Vertical takes up to 7%-10% more time due to matrix transformations
        '''
     
        point = xy[pointIndex]
        if not horizontal:
            xy[:,[0,1]] = xy[:,[1,0]]
            point = xy[pointIndex]

        rightEdge = self.isEdgePoly((point[0]+self.eps,point[1]), xy)
        leftEdge = self.isEdgePoly((point[0]-self.eps,point[1]), xy)
        leftInside, leftCrossIndex, rightInside, rightCrossIndex = self.isInsidePoly(pointIndex,xy)
        
        if not rightEdge and rightInside:
            #Identify the nearest cross edge
            index = 0
            dMax = np.inf
            for i in range(rightCrossIndex.size):
                if rightCrossIndex[i]:
                    if i != pointIndex:
                        if xy[i+1,0] == xy[i,0]:
                            d = (point[0]-xy[i,0])**2
                        elif xy[i+1,1] == xy[i,1]:
                            if np.abs(point[0]-xy[i+1,0]) < np.abs(point[0]-xy[i,0]):
                                d = (point[0]-xy[i+1,0])**2
                            else:
                                d = (point[0]-xy[i,0])**2
                        else:
                            dxdy = (xy[i+1,0]-xy[i,0])/float(xy[i+1,1]-xy[i,1])
                            cy = point[1] - xy[i,1]
                            d = (point[0] - xy[i,0] - dxdy*cy)**2
                        if d < dMax:
                            index = i
                            dMax = d                  
        elif not leftEdge and leftInside:
            #Identify the nearest cross edge
            index = 0
            dMax = np.inf
            for i in range(leftCrossIndex.size):
                if leftCrossIndex[i]:
                    if i != pointIndex:
                        if xy[i+1,0] == xy[i,0]:
                            d = (point[0]-xy[i,0])**2
                        elif xy[i+1,1] == xy[i,1]:
                            if np.abs(point[0]-xy[i+1,0]) < np.abs(point[0]-xy[i,0]):
                                d = (point[0]-xy[i+1,0])**2
                            else:
                                d = (point[0]-xy[i,0])**2
                        else:
                            dxdy = (xy[i+1,0]-xy[i,0])/float(xy[i+1,1]-xy[i,1])
                            cy = point[1] - xy[i,1]
                            d = (point[0] - xy[i,0] - dxdy*cy)**2
                        if d < dMax:
                            index = i
                            dMax = d
        else:
            if not horizontal:
                xy[:,[0,1]] = xy[:,[1,0]]
            raise ValueError('This polygon cannot be sliced at the specified vertex')
            
        #Split the polygon into two
        if xy[index+1,0] == xy[index,0]:
            newPoint = np.array([[xy[index,0],point[1]]])
        elif xy[index+1,1] == xy[index,1]:
            if np.abs(xy[index+1,0] - point[0]) < np.abs(xy[index,0] - point[0]):
                newPoint = xy[[index+1]]
            else:
                newPoint = xy[[index]]
        else:
            dxdy = (xy[index+1,0]-xy[index,0])/float(xy[index+1,1]-xy[index,1])
            cy = point[1] - xy[index,1]
            xint = xy[index,0] + dxdy*cy
            newPoint = np.array([[xint,point[1]]])
            
        if index < pointIndex:
            slice1 = np.append(np.append(xy[index+1:pointIndex+1],newPoint,axis=0),xy[[index+1]],axis=0)
            slice2 = np.append(np.append(xy[:index+1],newPoint,axis=0),xy[pointIndex:],axis=0)
        else:
            slice1 = np.append(np.append(xy[pointIndex:index+1],newPoint,axis=0),xy[[pointIndex]],axis=0)
            slice2 = np.append(np.append(xy[:pointIndex+1],newPoint,axis=0),xy[index+1:],axis=0)  

        #Remove a single duplicate consecutive point
        z = np.array([0,0])
        ri1 = np.where(np.all(slice1[1:]-slice1[:-1] == z,axis=1))
        ri2 = np.where(np.all(slice2[1:]-slice2[:-1] == z, axis=1))
        try:
            slice1 = np.append(slice1[:ri1[0][0]],slice1[ri1[0][0]+1:],axis=0)
        except:
            pass
        try:
            slice2 = np.append(slice2[:ri2[0][0]],slice2[ri2[0][0]+1:],axis=0)
        except:
            pass
        
        #Remove a single 3-point horizontal line
        ds1 = slice1[1:,1]-slice1[:-1,1] == 0
        ds2 = slice2[1:,1]-slice2[:-1,1] == 0
        ri1 = np.where(np.logical_and(ds1[:-1],ds1[1:]))
        ri2 = np.where(np.logical_and(ds2[:-1],ds2[1:]))
        try:
            for i in range(ri1[0].size):
                slice1 = np.append(slice1[:ri1[0][i]-i+1],slice1[ri1[0][i]-i+2:],axis=0)
        except:
            pass
        if ds1[0] and ds1[-1]:
            slice1 = np.append(slice1[1:-1],slice1[1:2],axis=0)
        try:
            for i in range(ri2[0].size):
                slice2 = np.append(slice2[:ri2[0][i]-i+1],slice2[ri2[0][i]-i+2:],axis=0)
        except:
            pass
        if ds2[0] and ds2[-1]:
            slice2 = np.append(slice2[1:-1],slice2[1:2],axis=0)

        if not horizontal:
            xy[:,[0,1]] = xy[:,[1,0]]
            slice1[:,[0,1]] = slice1[:,[1,0]]
            slice2[:,[0,1]] = slice2[:,[1,0]]
        
        return slice1, slice2
        
    def isInsidePoly(self, index, xy):
        '''
        isInsidePoly(point, xy)
        
        Returns true of point is inside the polygon xy
        
        Parameters
        ----------
        point : list of 2 integers
            The point to test
        
        xy : Nx2 numpy.ndarray
            A list of vertices ordered clockwise or counterclockwise
            
        Returns
        -------
        insideLeft : boolean
            Specify if the point is inside the polygon moving left
            
        leftCrossIndex : boolean
            Indices of edges to the left of the point
            
        insideRight : boolean
            Specify if the point is inside the polygon moving right            
            
        rightCrossIndex : boolean
            Indices of edges to the right of the point
            
        Description
        -----------
        This function is core to the performance and capabilities of the
        fracture class
        
        This algorithm determines whether a point is inside/outside a polygon
        by counting the number of times the point crosses an edge as it moves
        directly left and right.  An odd number of crossing in both direction
        means that the point is inside the polygon.
        
        Speed
        -----
        isInsidePoly is much faster than the pointInPoly algorithm:
        nCalls    nVertices   pointInPoly[s]    isInsidePoly[s]   isEdgePoly[s]
        10000     11          1.008             0.511             0.528
        10000     100         8.350             0.690             0.704
        10000     1000        81.955            1.291             1.367
        
        The speed of isInsidePoly is slowerby 26% since its algorithm has been
        updated to work with self-intersecting polygons.
        '''
        
        px, py = xy[index]
        dy = xy[:,1] - py

        #Determine whether or not a line is crossed (changes sign)        
        a = dy[:-1]
        b = dy[1:]

        positive_ab = np.logical_and(a>0,b>0)
        negative_ab = np.logical_and(a<0,b<0)
        zero_ab = np.logical_and(a==0,b==0)
        signChange = np.logical_not(positive_ab+negative_ab+zero_ab)
        
        length = signChange.size
        left = np.zeros((length,)) == 1
        right = np.zeros((length,)) == 1

        #Determine which lines are crossed to the left and right of the vertex
        for i in range(signChange.size):
            if signChange[i]:
                if xy[i+1,0] < px and xy[i,0] < px:
                    left[i] = True
                elif xy[i+1,0] > px and xy[i,0] > px:
                    right[i] = True
                else:
                    dxdy = (xy[i+1,0]-xy[i,0])/float(xy[i+1,1]-xy[i,1])
                    cy = py - xy[i,1]
                    xint = xy[i,0] + dxdy*cy
                    if px == xint:
                        left[i] = True
                        right[i] = True
                    elif px > xint:
                        left[i] = True
                    else:
                        right[i] = True
        
        #Ignores lines that contain the vertex
        left[index] = False
        left[index-1] = False
        right[index] = False
        right[index-1] = False

        #In the case of 2 consecutive True, then a vertex is crossed, so ignore 1 of the lines
        #Need to consider a better way to adjust for intersections at vertices
        tmp_zero_ab = np.append(zero_ab,zero_ab[0:2])
        tmp_dy = np.append(dy,dy[0:3])
        tmp_left = np.append(left,left[0:2])
        tmp_right = np.append(right,right[0:2])
        correction_left = 0
        correction_right = 0
    
        for i in range(length-1):
            if tmp_left[i]:
                if tmp_left[i+1]:
                    if tmp_dy[i]*tmp_dy[i+2] < 0:
                        correction_left -= 1
                elif tmp_zero_ab[i+1]:
                    if tmp_left[i+2]:
                        if tmp_dy[i]*tmp_dy[i+3] < 0:
                            correction_left -= 1
            if tmp_right[i]:
                if tmp_right[i+1]:
                    if tmp_dy[i]*tmp_dy[i+2] < 0:
                        correction_right -= 1
                elif tmp_zero_ab[i+1]:
                    if tmp_right[i+2]:
                        if tmp_dy[i]*tmp_dy[i+3] < 0:
                            correction_right -= 1

        crossLeft = np.logical_and(signChange,left)
        crossRight = np.logical_and(signChange,right)
        
        insideLeft = (np.sum(crossLeft)+correction_left)%2 == 1 
        insideRight = (np.sum(crossRight)+correction_right)%2 == 1        
        
        #If vertex lies on self-intersecting set of lines, the vertex is not considered inside a polygon
        self_intersect = np.where(np.logical_and(left,right))[0]
        if self_intersect.size > 0:
            insideLeft = False
            insideRight = False

        return insideLeft, crossLeft, insideRight, crossRight

    def isInsidePolyByPoint(self, point, xy, crossIndex=False):
        '''
        isInsidePoly(point, xy, crossIndex=False)
        
        Returns true of point is inside the polygon xy
        
        Parameters
        ----------
        point : list of 2 integers
            The point to test
        
        xy : Nx2 numpy.ndarray
            A list of vertices ordered clockwise or counterclockwise
            
        crossIndex : boolean
            Specify whether to return the indices of each edge that is crossed
            
        Returns
        -------
        inside : boolean
            Specify whether or not the point is inside the polygon
            
        leftCrossIndex : boolean
            Indices of edges to the left of the point
            
        rightCrossIndex : boolean
            Indices of edges to the right of the point
            
        Description
        -----------
        This function is core to the performance and capabilities of the
        fracture class
        
        This algorithm determines whether a point is inside/outside a polygon
        by counting the number of times the point crosses an edge as it moves
        directly left and right.  An odd number of crossing in both direction
        means that the point is inside the polygon.
        
        Speed
        -----
        isInsidePoly is much faster than the pointInPoly algorithm:
        nCalls    nVertices   pointInPoly[s]    isInsidePoly[s]   isEdgePoly[s]
        10000     11          1.008             0.511             0.528
        10000     100         8.350             0.690             0.704
        10000     1000        81.955            1.291             1.367
        
        Note
        ----
        This algorithm fails when a vertex of a polygon lies on a line of the
        same polygon.  For example
        xy = [0,0,0,20000,20000,20000,20000,0,5000,0,5000,5000,15000,5000,15000,15000,5000,15000,5000,0,0,0]
        x           y
        0           0
        0           20000
        20000       20000
        20000       0
        5000        0
        5000        5000        A
        15000       5000
        15000       15000
        5000        15000       B
        5000        0           C
        0           0
        
        Observe that the vertex A lies on the line BC.  In this situation, it
        is impossible to determine that traversing from A towards the line BC
        we actually leave the polygon before entering the polygon again.  One
        can probably account for this situation through an exception, hopefully
        efficiently. . .
        '''
        
        px, py = point
        dy = xy[:,1] - py
        signChange = np.logical_xor(dy[:-1] >= 0, dy[1:] >= 0)
        left = np.zeros(signChange.shape) == 1
        right = np.zeros(signChange.shape) == 1
        hleft = np.zeros(signChange.shape) == 1
        hright = np.zeros(signChange.shape) == 1
        for i in range(signChange.size):
            if signChange[i]:
                if xy[i+1,0] < px and xy[i,0] < px:
                    left[i] = True
                elif xy[i+1,0] > px and xy[i,0] > px:
                    right[i] = True
                else:
                    dxdy = (xy[i+1,0]-xy[i,0])/float(xy[i+1,1]-xy[i,1])
                    cy = py - xy[i,1]
                    xint = xy[i,0] + dxdy*cy
                    if px > xint:
                        left[i] = True
                    else:
                        right[i] = True
            else:
                if dy[i] == 0:
                    if xy[i+1,0] < px and xy[i,0] < px:
                        hleft[i] = True
                    else:
                        hright[i] = True
                        
        crossLeft = np.logical_and(signChange,left)
        crossRight = np.logical_and(signChange,right)
        
        inside = np.sum(crossLeft)%2 == 1 and np.sum(crossRight)%2 == 1

        if crossIndex:
            return inside, np.logical_or(crossLeft,hleft), np.logical_or(crossRight,hright)
        else:
            return inside

    def isEdgePoly(self, point, xy):
        '''
        isEdgePoly(point, xy)
        
        Returns true of point is on the edge of the polygon xy
        
        Parameters
        ----------
        point : list of 2 integers
            The point to test
        
        xy : Nx2 numpy.ndarray
            A list of vertices ordered clockwise or counterclockwise
            
        Returns
        -------
        edge : boolean
            Specify whether or not the point is inside the polygon
            
        Description
        -----------
        This algorithm determines whether a point is on the edge of a polygon
        using trivial logic and math
        '''
        edge = False
        px, py = point
        y = xy[:,1] - py
        x = xy[:,0] - px
        
        iy = np.logical_or(np.logical_and(y[:-1] <= 0, y[1:] >= 0),np.logical_and(y[:-1] >= 0, y[1:] <= 0))
        ix = np.logical_or(np.logical_and(x[:-1] <= 0, x[1:] >= 0),np.logical_and(x[:-1] >= 0, x[1:] <= 0))
        
        index = np.logical_and(ix,iy)
        for i in range(index.size):
            if index[i]:
                if xy[i+1,1] == xy[i,1]:
                    if xy[i,0] <= px and xy[i+1,0] >= px or xy[i,0] >= px and xy[i+1,0] <= px:
                        edge = True
                else:
                    dxdy = (xy[i+1,0]-xy[i,0])/float(xy[i+1,1]-xy[i,1])
                    cy = py - xy[i,1]
                    xint = xy[i,0] + dxdy*cy
                    if px == xint:
                        edge = True
        return edge

    def fieldFracture(self, xy, fieldSize = [200000, 200000]):
        '''
        fracture(xy)
        
        Fractures all polygons into fields
        
        Parameters
        ----------
        xy : list of Nx1 numpy.ndarray
            The list of polygons to be fractured
        fieldSize : a list of 2 integers
            The [width, height] of a field
            
        Returns
        -------
        parts : list of Nx1 numpy.ndarray
            The list of the field decomposed polygons
        '''
        parts = []
        for i in xy:
            parts.extend(self.sliceField(i, fieldSize))
        return parts

    def lineFracture(self, xy, position, horizontal=True):
        '''
        lineFracture(xy,position,horizontal=True)
        
        Fractures all polygons along a line
        
        Parameters
        ----------
        xy : list of Nx1 numpy.ndarray
            The list of polygons to be fractured
            
        Returns
        -------
        parts : list of Nx1 numpy.ndarray
            The list of the line decomposed polygons
        '''
        parts = []
        for i in xy:
            parts.extend(self.sliceLine(i,position,horizontal))
        return parts

    def sliceLine(self, xy, position, horizontal=True):
        '''
        sliceLine(xy, position, horizontal=True)
        
        Slices the polygon along a line
        
        Parameters
        ----------
        xy : Nx2 numpy.ndarray
            An array of points representing a polygon
        position : integer
            Position to slice the polygon
        horizontal : boolean
            Slice direction is either horizontal or vertical (true or false)

        Returns
        -------
        polyList : List of Nx1 numpy.ndarray
            List of polygon
        
        Description:
        The sliceField algorithm is as follows:
        1)  Ensure the proper datatype for the polygon
        2)  Define the line position
        3)  Slice polygon along the line
        '''
        if type(xy) is list:
            if len(xy)%2 == 1:
                raise ValueError('fracture.sliceLine : The input xy must contain an even number of elements')
            elif xy[0:2] != xy[-2:]:
                xy = np.reshape(np.array(xy.extend(xy[0:2]),dtype=np.float),(len(xy)/2,2))
            else:
                xy = np.reshape(np.array(xy,dtype=np.float),(len(xy)/2,2))
        elif type(xy) is np.ndarray:
            if len(xy.shape) == 1:
                if xy.size%2 == 1:
                    raise ValueError('fracture.sliceLine : The input xy must contain an even number of elements')
                elif np.all(xy[0:2] != xy[-2:]):
                    xy = np.append(xy,xy[0:2],axis=0)
                    xy = np.reshape(xy,(xy.size/2,2))
                else:
                    xy = np.reshape(xy,(xy.size/2,2))
            else:
                if np.all(xy[0] != xy[-1]):
                    xy = np.append(xy,xy[0])
            if xy.dtype != np.float:
                xy = xy.astype(np.float)
        else:
            raise TypeError('facture.sliceLine : The input xy must be a list of integers')
        if horizontal:
            point = [0,position]
        else:
            point = [position,0]
            
        polyList = self.recursiveSlicePoint(point,xy,horizontal)
        
        for i in range(len(polyList)):
            polyList[i] = polyList[i].ravel()
    
        return polyList

    def sliceField(self, xy, fieldSize = [2000000, 2000000]):
        '''
        sliceField(xy, fieldSize = [2000000, 2000000])
        
        Slices the polygon into fields
        
        Parameters
        ----------
        xy : Nx2 numpy.ndarray
            An array of points representing a polygon
            
        fieldSize : list of two integers
            The size of the field specified as [width, height]

        Returns
        -------
        polyList : List of polygons
        
        Description:
        The sliceField algorithm is as follows:
        1)  Ensure the proper datatype for the polygon
        2)  Define field positions
        3)  Slice polygon along field lines
        
        Todo:
        This field fracturing algorithm assumes a repeating grid.  A more
        general algorithm should be to recieve a list of slice positions.
        '''
        if type(xy) is list:
            if len(xy)%2 == 1:
                raise ValueError('fracture.sliceField : The input xy must contain an even number of elements')
            elif xy[0:2] != xy[-2:]:
                xy = np.reshape(np.array(xy.extend(xy[0:2]),dtype=np.float),(len(xy)/2,2))
            else:
                xy = np.reshape(np.array(xy,dtype=np.float),(len(xy)/2,2))
        elif type(xy) is np.ndarray:
            if len(xy.shape) == 1:
                if xy.size%2 == 1:
                    raise ValueError('fracture.sliceField : The input xy must contain an even number of elements')
                elif np.all(xy[0:2] != xy[-2:]):
                    xy = np.append(xy,xy[0:2],axis=0)
                    xy = np.reshape(xy,(xy.size/2,2))
                else:
                    xy = np.reshape(xy,(xy.size/2,2))
            else:
                if np.all(xy[0] != xy[-1]):
                    xy = np.append(xy,xy[0])
            if xy.dtype != np.float:
                xy = xy.astype(np.float)
        else:
            raise TypeError('facture.sliceField : The input xy must be a list of integers')
            
        if type(fieldSize) is list:
            if len(fieldSize) == 1:
                fieldSize = [fieldSize, fieldSize]
        else:
            raise ValueError('fracture.sliceField : The input fieldSize must be a list of 2 integers')
        
        nC = int(np.ceil(np.max(xy[:,0])/fieldSize[0]))+1
        nR = int(np.ceil(np.max(xy[:,1])/fieldSize[1]))+1
        
        rowList = []
        tmp = [xy.copy()]
        for j in range(1,nR):
            tmpList = []
            for k in tmp:
                hSlice = self.recursiveSlicePoint([0,j*fieldSize[1]],k)
                for l in hSlice:
                    if l[:,1].max() <= j*fieldSize[1]:
                        rowList.append(l)
                    else:
                        tmpList.append(l)
            tmp = tmpList
        
        polyList = []
        for i in rowList:
            tmp = [i.copy()]
            for j in range(1,nC):
                tmpList = []
                for k in tmp:
                    vSlice = self.recursiveSlicePoint([j*fieldSize[0],0],k,False)
                    for l in vSlice:
                        if l[:,0].max() <= j*fieldSize[0]:
                            polyList.append(l)
                        else:
                            tmpList.append(l)
                tmp = tmpList
    
        for i in range(len(polyList)):
            polyList[i] = polyList[i].ravel()
    
        return polyList   
      
    def recursiveSlicePoint(self, point, xy, horizontal=True):
        '''
        recursiveSlicePoint(point, xy, horizontal = True)
        
        Slices the polygon along the axis of the point recursively until a
        line drawn from the point no longer intersects the polygon
        
        Parameters
        ----------
        point : integer
            The point to slice from          
            
        xy : Nx2 numpy.ndarray
            An array of points representing a polygon
            
        horizontal : boolean
            Slice horizontally (true) or vertically (false) from the point
            Slicing vertically takes more time since xy is changed to yx before
                slicing horizontally and then yx is changed back to xy
                Vertical slicing can be sped up by independent implementation
        
        Returns
        -------
        s1 : Nx2 numpy.ndarray
            The first slice of the polygon
        S2 : integer
            The second slice of the polygon
            
        Description
        -----------
        1)  A horizontal/vertical line is drawn from the point.  
        2)  A new vertex is inserted into a polygon at the first intersection 
            of an edge of the polygon with the horizontal/vertical line.
        3)  The polygon is sliced horizontally/vertically from the inserted 
            vertex into 2 polygons
        4)  The 2 polygon are sent to (1) until they can not be further sliced
        '''
        polyList = []
        
        if horizontal:
            lb = np.min(xy[:,1])
            ub = np.max(xy[:,1])
            if (lb <= point[1] and ub <= point[1]) or (lb >= point[1] and ub >= point[1]):
                return [xy]
        else:
            lb = np.min(xy[:,0])
            ub = np.max(xy[:,0])
            if (lb <= point[0] and ub <= point[0]) or (lb >= point[0] and ub >= point[0]):
                return [xy]
        try:    
            s1,s2 = self.slicePoint(point,xy,horizontal)
            tmp = self.recursiveSlicePoint(point,s1,horizontal)
            polyList.extend(tmp)
            tmp = self.recursiveSlicePoint(point,s2,horizontal)
            polyList.extend(tmp)
        except:
            pass
                    
        return polyList
        
    def slicePoint(self, point, xy, horizontal=True):
        '''
        slicePoint(point, xy, horizontal = True)
        
        Slices the polygon along the axis of the point and returns 2 polygons
        
        Parameters
        ----------
        pointIndex : integer
            The point to slice from
            
        xy : Nx2 numpy.ndarray
            An array of points representing a polygon
            
        horizontal : boolean
            Slice horizontally (true) or vertically (false)
            Slicing vertically takes more time since xy is changed to yx before
                slicing horizontally and then yx is changed back to xy
                Vertical slicing can be sped up by independent implementation
        
        Returns
        -------
        s1 : Nx2 numpy.ndarray
            One slice of the polygon
        S2 : integer
            The second slice of the polygon
            
        Description
        -----------
        1)  A horizontal/vertical line is drawn from the point.  
        2)  A new vertex is inserted into a polygon at the first intersection 
            of an edge of the polygon with the horizontal/vertical line.
        3)  The polygon is sliced horizontally/vertically from the inserted 
            vertex
        '''
        try:
            xyi, index = self.insertVertex(point, xy, horizontal)
        except ValueError:
            if horizontal:
                raise ValueError('fracture.slicePoint : The polygon cannot be sliced horizontally from this point')
            else:
                raise ValueError('fracture.slicePoint : The polygon cannot be sliced vertically from this point')
        except:
            raise ValueError('fracture.slicePoint : Something unaccounted for threw an error')
        s1, s2 = self.slicePolygon(index, xyi, horizontal)
        return s1, s2

    def insertVertex(self, point, xy, horizontal = True):
        '''
        insertVertex(point, xy, horizontal = True)
        
        Returns a polygon with a vertex inserted along the axis of the point
        
        Parameters
        ----------
        pointIndex : integer
            An integer specifying the vertex to slice            
            
        xy : Nx2 numpy.ndarray
            An array of points representing a polygon
            
        horizontal : boolean
            Slice horizontally (true) or vertically (false)
            Slicing vertically takes more time since xy is changed to yx before
                slicing horizontally and then yx is changed back to xy
                Vertical slicing can be sped up by independent implementation
        
        Returns
        -------
        xyi : Nx2 numpy.ndarray
            The polygon with a vertex inserted
            
        index : integer
            The index of the inserted vertex
            
        Description
        -----------
        1)  A horizontal/vertical line is drawn from the point.  
        2)  A new vertex is inserted into a polygon at the first intersection 
            of an edge of the polygon with the horizontal/vertical line.
        '''
        if not horizontal:
            xy[:,[0,1]] = xy[:,[1,0]]
            point = point[::-1]
        rightEdge = self.isEdgePoly((point[0]+self.eps,point[1]), xy)
        rightInside, tmp, rightCrossIndex = self.isInsidePolyByPoint((point[0]+self.eps,point[1]),xy,True)
        #Determine if a point px+eps is inside or on the edge of the polygon
        leftEdge = self.isEdgePoly((point[0]-self.eps,point[1]), xy)
        leftInside, leftCrossIndex, tmp = self.isInsidePolyByPoint((point[0]-self.eps,point[1]),xy,True)
        if not rightEdge and np.any(rightCrossIndex):
            #Identify the nearest cross edge
            index = None
            dMax = np.inf
            d = dMax
            for i in range(rightCrossIndex.size):
                if rightCrossIndex[i]:
                    if xy[i+1,1] == point[1] or xy[i,1] == point[1]:
                        pass
                    else:
                        dxdy = (xy[i+1,0]-xy[i,0])/float(xy[i+1,1]-xy[i,1])
                        cy = point[1] - xy[i,1]
                        d = (point[0] - xy[i,0] - dxdy*cy)**2
                    if d < dMax:
                        index = i
                        dMax = d                  
        elif not leftEdge and np.any(leftCrossIndex):
            #Identify the nearest cross edge
            index = None
            dMax = np.inf
            d = dMax
            for i in range(leftCrossIndex.size):
                if leftCrossIndex[i]:
                    if xy[i+1,1] == point[1] or xy[i,1] == point[1]:
                            pass
                    else:
                        dxdy = (xy[i+1,0]-xy[i,0])/float(xy[i+1,1]-xy[i,1])
                        cy = point[1] - xy[i,1]
                        d = (point[0] - xy[i,0] - dxdy*cy)**2
                    if d < dMax:
                        index = i
                        dMax = d
        else:
            if not horizontal:
                xy[:,[0,1]] = xy[:,[1,0]]
            raise ValueError('This polygon cannot be sliced at the specified vertex')
        if index == None:
            raise ValueError('This polygon cannot be sliced at the specified vertex')
        #Split the polygon into two
        if xy[index+1,0] == xy[index,0]:
            newPoint = np.array([[xy[index,0],point[1]]])
        elif xy[index+1,1] == xy[index,1]:
            if np.abs(xy[index+1,0] - point[0]) < np.abs(xy[index,0] - point[0]):
                newPoint = xy[[index+1]]
            else:
                newPoint = xy[[index]]
        else:
            dxdy = (xy[index+1,0]-xy[index,0])/float(xy[index+1,1]-xy[index,1])
            cy = point[1] - xy[index,1]
            xint = xy[index,0] + dxdy*cy
            newPoint = np.array([[xint,point[1]]])
            
        if np.all(xy[index] == newPoint):
            xyi = xy.copy()
        elif np.all(xy[index+1] == newPoint):
            xyi = xy.copy()
            index += 1
        else:
            xyi = np.insert(xy,index+1,newPoint,axis=0)
            index += 1
        
        if not horizontal:
            xy[:,[0,1]] = xy[:,[1,0]]
            xyi[:,[0,1]] = xyi[:,[1,0]]
            
        return xyi, index

    def checkPrimitive(self, vertices):
        '''
        checkPrimitives(vertices)
        
        Returns true if the polygon may be a Jeol v3.0 format primitive

        Parameters
        ----------
        vertices : Nx1 numpy.ndarray of integers
            [x0 y0 x1 y1 ... xn yn] or
            [x0 y0 x1 y1 ... xn yn x0 y0]

        Returns
        -------
        isPrimitive : boolean
            Describes if the polygon is a primitive
        
        failLog : String
            A message describing why the polygon is not a primitive
            
        Description
        -----------
        This function will confirm if the polygon is compatible with the
        Jeol v3.0 format primitive, but it does not enforce the following
        specification:
            No negative values
            Integers must range from 0 to 2^20
        These specifications were ignored to allow fracturing of polygons that
        extend beyond the field of an ebeam writer
        
        The v3_Pat.checkPrimitive() should be use to qualify all polygons
        that are ready for conversion.
        '''
        isPrimitive = False
        failLog = 'No error was found'
        
        if np.all(vertices[0:2] == vertices[-2:]):
            vertices = vertices[:-2]
        
        if not vertices.size in [6,8]:
            failLog = 'The vertices parameter must contain 4, 6, or 8 elements'

        if vertices.size == 8:
            #The elements of vertices is [X1 Y1 X2 Y2 X3 Y3 X4 Y4]
        
            #Determine if the base of the trapezoid is along X or Y
            tmp = np.append(vertices,vertices[0:2])
            isX = sum(np.diff(tmp[1::2]) == 0) == 2
            isY = sum(np.diff(tmp[0::2]) == 0) == 2
            tmp = vertices.reshape(4,2)
            
            #The trapezoid is not supported
            if not isX and not isY:
                failLog = 'The trapezoid does not have both base parallel to either the X or Y axis'
                
            #The trapezoid is a rectangle
            if isX and isY:
                isPrimitive = True
                
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

                if theta1 > np.pi/3 or theta2 > np.pi/3:
                    failLog = 'X Trapezoid Theta1 or Theta2 cannot be larger than 60 degrees'
                else:
                    isPrimitive = True

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

                if theta1 > np.pi/3 or theta2 > np.pi/3:
                    failLog = 'Y Trapezoid Theta1 or Theta2 cannot be larger than 60 degrees'
                else:
                    isPrimitive = True
    
        elif vertices.size == 6:
            #The element of vertices is [X1 Y1 X2 Y2 X3 Y3]            
            
            #Determineof the base of the triangle is along X or Y
            tmp = np.append(vertices,vertices[0:2])
            isX = sum(np.diff(tmp[1::2]) == 0) == 1
            isY = sum(np.diff(tmp[0::2]) == 0) == 1
            tmp = vertices.reshape(3,2)

            if not isX and not isY:
                failLog = 'One edge of the triangle must be parallel to either the X or Y axis'

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
                    
                    theta1 = np.arctan(abs(int(trap[6])-int(trap[0]))/float(abs(int(trap[1])-int(trap[7]))))
                    theta2 = np.arctan(abs(int(trap[2])-int(trap[4]))/float(abs(int(trap[3])-int(trap[5]))))

                    if theta1 > np.pi/3 or theta2 > np.pi/3:
                        failLog = 'X Triangle Theta1 or Theta2 cannot be larger than 60 degrees'
                    else:
                        isPrimitive = True
                    
                #Y right triangle
                else:
                    try:
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
    
                        if theta1 > np.pi/3 or theta2 > np.pi/3:
                            failLog = 'Y Triangle Theta1 or Theta2 cannot be larger than 60 degrees'
                        else:
                            isPrimitive = True
                    except:
                        failLog = 'Y Triangle is a Line'
                    
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

                if theta1 > np.pi/3 or theta2 > np.pi/3:
                    failLog = 'X Triangle Theta1 or Theta2 cannot be larger than 60 degrees'
                else:
                    isPrimitive = True

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

                if theta1 > np.pi/3 or theta2 > np.pi/3:
                    failLog = 'Y Triangle Theta1 or Theta2 cannot be larger than 60 degrees'
                else:
                    isPrimitive = True
        else:
            failLog = 'An unaccounted error occurred'
    
        return isPrimitive, failLog

def test(debug = False):
    if debug:
        import matplotlib.pyplot as plot
    A = fracture()
    #Contains many slices along horizontal lines and vertices
    xy = [0,0,2,5,2,7,0,10,5,10,13,12,17,8,20,10,25,5,26,5,40,11,34,8,36,5,33,0,22,0,17,5,9,5,6,0,0,0]
    
    #xy = [i*100 for i in [33,8,40,11,34,8,33,8]]
    
    #Requires Recursive slicing
    #xy = [40,1249,905,1249,905+19*2,1249-249*2,905+18*2,1249-249*2,40,1249]

    #Self intersecting polygon  
    #xy = [0,0,0,20000,20000,20000,20000,0,5000,0,5000,5000,15000,5000,15000,15000,5000,15000,5000,0,0,0]
    
    z = A.fracture([xy])
    if debug:
        plot.plot(xy[::2],xy[1::2],'b-s',linewidth=2)
        for i in range(len(z)):
            plot.plot(z[i][::2],z[i][1::2],'--',linewidth=5)
        plot.axes().set_aspect('equal')
        plot.show()

def testGDS():
    import matplotlib.pyplot as plot
    import time
    from GDSII_Library import GDSII_Library
    A = fracture()
    B = GDSII_Library()
    
    B.readFile('selfintersect.gds')
    a = []
    for i in B.structure[0].boundary:
        a.append(np.array(i.xy))
    ox = a[0][::2].min()
    oy = a[0][1::2].min()
    a[0][::2] -= ox
    a[0][1::2] -= oy
    
    start = time.time()
    z = A.fieldFracture([a[0]],[2000000,2000000])
    z = A.fracture(a)
    end = time.time()
    print end-start
    
    plot.plot(a[0][::2],a[0][1::2],'b-s',linewidth=2)
    for i in range(len(z)):
        plot.plot(z[i][::2],z[i][1::2],'--',linewidth=5)
    plot.show()    
        
if __name__ == '__main__':
    test(True)