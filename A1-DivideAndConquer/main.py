# Convex hull
#
# Usage: python main.py [-d] [-np] file_of_points
#
#   -d sets the 'discardPoints' flag
#   -np removes pauses
#
# You can press ESC in the window to exit.
#
# You'll need Python 3 and must install these packages:
#
#   PyOpenGL, GLFW


import sys, os, math

try: # PyOpenGL
  from OpenGL.GL import *
except:
  print( 'Error: PyOpenGL has not been installed.' )
  sys.exit(0)

try: # GLFW
  import glfw
except:
  print( 'Error: GLFW has not been installed.' )
  sys.exit(0)



# Globals

window = None

windowWidth  = 1000 # window dimensions
windowHeight = 1000

minX = None # range of points
maxX = None
minY = None
maxY = None

r  = 0.01 # point radius as fraction of window size

numAngles = 32
thetas = [ i/float(numAngles)*2*3.14159 for i in range(numAngles) ] # used for circle drawing

allPoints = [] # list of points

lastKey = None  # last key pressed

discardPoints = False
addPauses = True

# Point
#
# A Point stores its coordinates and pointers to the two points beside
# it (CW and CCW) on its hull.  The CW and CCW pointers are None if
# the point is not on any hull.
#
# For debugging, you can set the 'highlight' flag of a point.  This
# will cause the point to be highlighted when it's drawn.

class Point(object):

    def __init__( self, coords ):

      self.x = float( coords[0] ) # coordinates
      self.y = float( coords[1] )

      self.ccwPoint = None # point CCW of this on hull
      self.cwPoint  = None # point CW of this on hull

      self.highlight = False # to cause drawing to highlight this point


    def __repr__(self):
      return 'pt(%g,%g)' % (self.x, self.y)


    def drawPoint(self):

      # Highlight with yellow fill
      
      if self.highlight:
          glColor3f( 0.9, 0.9, 0.4 )
          glBegin( GL_POLYGON )
          for theta in thetas:
              glVertex2f( self.x+r*math.cos(theta), self.y+r*math.sin(theta) )
          glEnd()

      # Outline the point
      
      glColor3f( 0, 0, 0 )
      glBegin( GL_LINE_LOOP )
      for theta in thetas:
          glVertex2f( self.x+r*math.cos(theta), self.y+r*math.sin(theta) )
      glEnd()

      # Draw edges to next CCW and CW points.

      if self.ccwPoint:
        glColor3f( 0, 0, 1 )
        drawArrow( self.x, self.y, self.ccwPoint.x, self.ccwPoint.y )

      if self.ccwPoint:
        glColor3f( 1, 0, 0 )
        drawArrow( self.x, self.y, self.cwPoint.x, self.cwPoint.y )



# Draw an arrow between two points, offset a bit to the right

def drawArrow( x0,y0, x1,y1 ):

    d = math.sqrt( (x1-x0)*(x1-x0) + (y1-y0)*(y1-y0) )

    vx = (x1-x0) / d      # unit direction (x0,y0) -> (x1,y1)
    vy = (y1-y0) / d

    vpx = -vy             # unit direction perpendicular to (vx,vy)
    vpy = vx

    xa = x0 + 1.5*r*vx - 0.4*r*vpx # arrow tail
    ya = y0 + 1.5*r*vy - 0.4*r*vpy

    xb = x1 - 1.5*r*vx - 0.4*r*vpx # arrow head
    yb = y1 - 1.5*r*vy - 0.4*r*vpy

    xc = xb - 2*r*vx + 0.5*r*vpx # arrow outside left
    yc = yb - 2*r*vy + 0.5*r*vpy

    xd = xb - 2*r*vx - 0.5*r*vpx # arrow outside right
    yd = yb - 2*r*vy - 0.5*r*vpy

    glBegin( GL_LINES )
    glVertex2f( xa, ya )
    glVertex2f( xb, yb )
    glEnd()

    glBegin( GL_POLYGON )
    glVertex2f( xb, yb )
    glVertex2f( xc, yc )
    glVertex2f( xd, yd )
    glEnd()
      
      

# Determine whether three points make a left or right turn

LEFT_TURN  = 1
RIGHT_TURN = 2
COLLINEAR  = 3

def turn( a, b, c ):

    det = (a.x-c.x) * (b.y-c.y) - (b.x-c.x) * (a.y-c.y)

    if det > 0:
        return LEFT_TURN
    elif det < 0:
        return RIGHT_TURN
    else:
        return COLLINEAR


# Build a convex hull from a set of point
#
# Use the method described in class


def buildHull( points ):

    # Check cases

    if len(points) == 3:

        # Base case of 3 points: make a hull
        # Initialize the three points from the inputted set
        a = points[0]
        b = points[1]
        c = points[2]
        # If a left turn from a around b to c, then set the cw and ccw pointers accordingly
        if turn(a,b,c) == LEFT_TURN:
            a.cwPoint = c
            a.ccwPoint = b
            b.cwPoint = a 
            b.ccwPoint = c
            c.cwPoint = b
            c.ccwPoint = a
        # If a right turn from a around b to c, then set the cw and ccw pointers accordingly
        elif turn(a,b,c) == RIGHT_TURN:
            a.cwPoint = b
            a.ccwPoint = c
            b.cwPoint = c
            b.ccwPoint = a
            c.cwPoint = a
            c.ccwPoint = b
        pass

    elif len(points) == 2:

        # Base case of 2 points: make a hull
        # Initialize the two points from the inputted set
        a = points[0]
        b = points[1]
        # Set the cw and ccw pointers accordingly, given there are only two points
        a.ccwPoint = b
        a.cwPoint = b
        b.cwPoint = a
        b.ccwPoint = a
      
        pass

    else:
        # Floor division the length of the inputted set by 2, to split the set into two sets of points
        mid = len(points) // 2
        # Since the inputted set of points is sorted, recursively build a hull from the left half and the right half of the inputted set of points
        L = points[:mid]   
        R = points[mid:]  
        # Recursively build the right and left hulls
        buildHull(L)
        buildHull(R)
      
      
        pass

 
        # You can do the following to help in debugging.  The code
        # below highlights all the points, then shows them, then
        # pauses until you press 'p'.  While paused, you can click on
        # a point and its coordinates will be printed in the console
        # window.  If you are using an IDE in which you can inspect
        # your variables, this will help you to identify which point
        # on the screen is which point in your data structure.
        #
        # This is good to do, for example, after you have recursively
        # built two hulls (above), to see that the two hulls look right.
        #
        # This same highlighting can also be done immediately after you have merged to hulls
        # ... again, to see that the merged hull looks right.

        for p in points:
            p.highlight = True
        display(wait=addPauses)

        #Walk Downward

        #find the rightmost point on the left hull and the leftmost on the right hull
        lowerLeft = L[len(L) - 1]
        lowerRight = R[0]
        #move the lowerLeft and lowerRight points downward on their hulls to bridge the bottom of the joint hull
        while turn(lowerLeft, lowerRight, lowerRight.ccwPoint) == RIGHT_TURN or turn(lowerLeft.cwPoint, lowerLeft, lowerRight) == RIGHT_TURN:
            #walk the current point on the left hull downward
            if turn(lowerLeft.cwPoint, lowerLeft, lowerRight) == RIGHT_TURN:
                #if the current point is the rightmost point on the left hull, only walk down
                if lowerLeft == L[len(L)-1]:
                    lowerLeft = lowerLeft.cwPoint

                #if below the rightmost point on the left hull, set the pointers of the current point to null, then walk down
                else:
                    temp = lowerLeft
                    lowerLeft = lowerLeft.cwPoint
                    temp.cwPoint = None
                    temp.ccwPoint = None

            #walk the current point on the right hull downward
            else:
                #if the current point is the leftmost point on the right hull, only walk down
                if lowerRight == R[0]:  
                    lowerRight = lowerRight.ccwPoint

                #if below the leftmost point on the right hull, set the pointers of the current point to null, then walk down
                else:
                    temp = lowerRight 
                    lowerRight = lowerRight.ccwPoint
                    temp.ccwPoint = None
                    temp.cwPoint = None

        #Walk Upward

        #find the rightmost point on the left hull and the leftmost on the right hull
        upperLeft = L[len(L) - 1]
        upperRight = R[0]
        while turn(upperLeft.ccwPoint, upperLeft, upperRight) == LEFT_TURN or turn(upperLeft, upperRight, upperRight.cwPoint) == LEFT_TURN:
            #walk the current point on the left hull upward
            if turn(upperLeft.ccwPoint, upperLeft, upperRight) == LEFT_TURN:
                #if the current point is the rightmost point on the left hull, only walk up
                if upperLeft == L[len(L)- 1]:
                     upperLeft = upperLeft.ccwPoint

                #if below the rightmost point on the left hull, set the pointers of the current point to null, then walk up
                else:
                    temp = upperLeft
                    upperLeft = upperLeft.ccwPoint
                    temp.cwPoint = None
                    temp.ccwPoint = None

            #walk the current point on the right hull upward
            else:
                 #if the current point is the leftmost point on the right hull, only walk up
                if upperRight == R[0]:
                     upperRight = upperRight.cwPoint

                 #if below the leftmost point on the right hull, set the pointers of the current point to null, then walk up
                else:
                    temp = upperRight
                    upperRight = upperRight.cwPoint
                    temp.cwPoint = None
                    temp.ccwPoint = None

        #join the bottom and top of hulls

        #checks any of the top-most joining points or bottom-most joining points are equal to either the leftmost on the right hull or the rightmost on the right hull
        if upperLeft == L[len(L) - 1] or lowerLeft == L[len(L)- 1] or upperRight == R[0] or lowerRight == R[0]:
            #join the bottom and top of the hulls via setting the corresponding cw and ccw pointers
            upperLeft.cwPoint = upperRight
            lowerLeft.ccwPoint = lowerRight
            upperRight.ccwPoint = upperLeft
            lowerRight.cwPoint = lowerLeft
            #checks if any do not equal the leftmost point on the right hull
            if upperRight != R[0] and lowerRight != R[0]:
                R[0].ccwPoint = None
                R[0].cwPoint = None
            #checks if any do not equal the rightmost point on the left hull
            elif upperLeft != L[len(L) - 1] and lowerLeft != L[len(L)- 1]:
                L[len(L)- 1].ccwPoint = None
                L[len(L)- 1].cwPoint = None
            #if both checks failed, then no pointers regarding the leftmost and rightmost points need to be adjusted
        
        #if none of the top/bottom most joining points are equal to the leftmost or rightmost points, then set their ccw and cw pointers to None
        else: 
            #join the bottom and top of the hulls via setting the corresponding cw and ccw pointers
            upperLeft.cwPoint = upperRight
            lowerLeft.ccwPoint = lowerRight
            upperRight.ccwPoint = upperLeft
            lowerRight.cwPoint = lowerLeft
            #set ccw and cw of both points below to None
            R[0].ccwPoint = None
            R[0].cwPoint = None
            L[len(L)- 1].ccwPoint = None
            L[len(L)- 1].cwPoint = None
        


        pass
        # Pause to see the result, then remove the highlighting from
        # the points that you previously highlighted:

        display(wait=addPauses)
        for p in points:
            p.highlight = False

    # At the very end of buildHull(), you should display the result
    # after every merge, as shown below.  This call to display() does
    # not pause.
    
    display()

  

windowLeft   = None
windowRight  = None
windowTop    = None
windowBottom = None


# Set up the display and draw the current image

def display( wait=False ):

    global lastKey, windowLeft, windowRight, windowBottom, windowTop
    
    # Handle any events that have occurred

    glfw.poll_events()

    # Set up window

    glClearColor( 1,1,1,0 )
    glClear( GL_COLOR_BUFFER_BIT )
    glPolygonMode( GL_FRONT_AND_BACK, GL_FILL )

    glMatrixMode( GL_PROJECTION )
    glLoadIdentity()

    glMatrixMode( GL_MODELVIEW )
    glLoadIdentity()

    if maxX-minX > maxY-minY: # wider point spread in x direction
        windowLeft = -0.1*(maxX-minX)+minX
        windowRight = 1.1*(maxX-minX)+minX
        windowBottom = windowLeft
        windowTop    = windowRight
    else: # wider point spread in y direction
        windowTop    = -0.1*(maxY-minY)+minY
        windowBottom = 1.1*(maxY-minY)+minY
        windowLeft   = windowBottom
        windowRight  = windowTop

    glOrtho( windowLeft, windowRight, windowBottom, windowTop, 0, 1 )

    # Draw points and hull

    for p in allPoints:
        p.drawPoint()

    # Show window

    glfw.swap_buffers( window )

    # Maybe wait until the user presses 'p' to proceed
    
    if wait:

        sys.stderr.write( 'Press "p" to proceed ' )
        sys.stderr.flush()

        lastKey = None
        while lastKey != 80 and lastKey != glfw.KEY_ESCAPE: # wait for 'p'
            glfw.wait_events()
            display()

        sys.stderr.write( '\r                     \r' )
        sys.stderr.flush()

        if lastKey == glfw.KEY_ESCAPE:
            sys.exit(0)

    

# Handle keyboard input

def keyCallback( window, key, scancode, action, mods ):

    global lastKey
    
    if action == glfw.PRESS:
        lastKey = key



# Handle window reshape


def windowReshapeCallback( window, newWidth, newHeight ):

    global windowWidth, windowHeight

    windowWidth  = newWidth
    windowHeight = newHeight



# Handle mouse click/release

def mouseButtonCallback( window, btn, action, keyModifiers ):

    if action == glfw.PRESS:

        # Find point under mouse

        x,y = glfw.get_cursor_pos( window ) # mouse position

        wx = (x-0)/float(windowWidth)  * (windowRight-windowLeft) + windowLeft
        wy = (windowHeight-y)/float(windowHeight) * (windowTop-windowBottom) + windowBottom

        minDist = windowRight-windowLeft
        minPoint = None
        for p in allPoints:
            dist = math.sqrt( (p.x-wx)*(p.x-wx) + (p.y-wy)*(p.y-wy) )
            if dist < r and dist < minDist:
                minDist = dist
                minPoint = p

        # print point and toggle its highlight

        if minPoint:
            minPoint.highlight = not minPoint.highlight
            print( minPoint )

        
    
# Initialize GLFW and run the main event loop

def main():

    global window, allPoints, minX, maxX, minY, maxY, r, discardPoints, addPauses
    
    # Check command-line args

    if len(sys.argv) < 2:
        print( 'Usage: %s filename' % sys.argv[0] )
        sys.exit(1)

    args = sys.argv[1:]
    while len(args) > 1:
        if args[0] == '-d':
            discardPoints = True
        elif args[0] == '-np':
            addPauses = False
        args = args[1:]

    # Set up window
  
    if not glfw.init():
        print( 'Error: GLFW failed to initialize' )
        sys.exit(1)

    window = glfw.create_window( windowWidth, windowHeight, "Assignment 1", None, None )

    if not window:
        glfw.terminate()
        print( 'Error: GLFW failed to create a window' )
        sys.exit(1)

    glfw.make_context_current( window )
    glfw.swap_interval( 1 )
    glfw.set_key_callback( window, keyCallback )
    glfw.set_window_size_callback( window, windowReshapeCallback )
    glfw.set_mouse_button_callback( window, mouseButtonCallback )

    # Read the points

    with open( args[0], 'rb' ) as f:
      allPoints = [ Point( line.split(b' ') ) for line in f.readlines() ]

    # Get bounding box of points

    minX = min( p.x for p in allPoints )
    maxX = max( p.x for p in allPoints )
    minY = min( p.y for p in allPoints )
    maxY = max( p.y for p in allPoints )

    # Adjust point radius in proportion to bounding box
    
    if maxX-minX > maxY-minY:
        r *= maxX-minX
    else:
        r *= maxY-minY

    # Sort by increasing x.  For equal x, sort by increasing y.
    
    allPoints.sort( key=lambda p: (p.x,p.y) )

    # Run the code
    
    buildHull( allPoints )

    # Wait to exit

    while not glfw.window_should_close( window ):
        glfw.wait_events()
        if lastKey == glfw.KEY_ESCAPE:
            sys.exit(0)

    glfw.destroy_window( window )
    glfw.terminate()
    


if __name__ == '__main__':
    main()
