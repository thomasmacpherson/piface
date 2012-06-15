##    cairo demos Copyright  (C)  2007 Donn.C.Ingle
##
##    Contact: donn.ingle@gmail.com - I hope this email lasts.
##
##    This program is free software; you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation; either version 2 of the License, or
##     ( at your option )  any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with this program; if not, write to the Free Software
##    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import pygtk
import gtk, gobject, cairo
from gtk import gdk

class Screen( gtk.DrawingArea ):
    """ This class is a Drawing Area"""
    def __init__( self, w, h, speed ):
        super( Screen, self ).__init__( )
        ## Old fashioned way to connect expose. I don't savvy the gobject stuff.
        self.connect ( "expose_event", self.do_expose_event )
        ## We want to know where the mouse is:
        self.connect ( "motion_notify_event", self._mouseMoved )
        ## More GTK voodoo : unmask events
        self.add_events ( gdk.BUTTON_PRESS_MASK |   gdk.BUTTON_RELEASE_MASK |   gdk.POINTER_MOTION_MASK )        
        ## This is what gives the animation life!
        gobject.timeout_add( speed, self.tick ) # Go call tick every 'speed' whatsits.
        self.width, self.height = w, h
        self.set_size_request ( w, h )
        self.x, self.y = 11110,11111110 #unlikely first coord to prevent false hits.

    def tick ( self ):
        """This invalidates the screen, causing the expose event to fire."""
        self.alloc = self.get_allocation ( )
        rect = gtk.gdk.Rectangle ( self.alloc.x, self.alloc.y, self.alloc.width, self.alloc.height )
        self.window.invalidate_rect ( rect, True )        
        return True # Causes timeout to tick again.

    ## When expose event fires, this is run
    def do_expose_event( self, widget, event ):
        self.cr = self.window.cairo_create( )
        ## Call our draw function to do stuff.
        self.draw( )

    def _mouseMoved ( self, widget, event ):
        self.x = event.x
        self.y = event.y

class BunchOfStuff ( object ):
    """Stores a bunch of data"""
    def __init__ ( self, x=0, y=0, rx=0, ry=0, rot=0, sx=1, sy=1 ):
        self.x = x
        self.y = y
        self.rx = rx
        self.ry = ry
        self.rot = rot
        self.sx = sx
        self.sy  = sy

class MyStuff ( Screen ):
    """This class is also a Drawing Area, coming from Screen."""
    def __init__ ( self, w, h, speed):
        Screen.__init__( self, w, h, speed )

        ## Setup three sets of data for the three objects to be drawn
        self.red = BunchOfStuff ( x=50, y=-10, rx=50, ry=25 )
        self.green = BunchOfStuff ( x=-10, y=10 )
        self.blue = BunchOfStuff ( x=-70,y=30, sx=1, sy=1 )

        self.sign = +1 # to flip the blue animation's sign

    def setToCenter ( self ):
        """Shift 0,0 to be in the center of page."""
        matrix = cairo.Matrix ( 1, 0, 0, 1, self.width/2, self.height/2 )
        self.cr.transform ( matrix ) # Make it so...

    def doMatrixVoodoo ( self, bos ):
        """Do all the matrix mumbo to get stuff to the right place on the screen."""
        ThingMatrix =cairo.Matrix ( 1, 0, 0, 1, 0, 0 )
        ## Next, move the drawing to it's x,y
        cairo.Matrix.translate ( ThingMatrix, bos.x, bos.y )
        self.cr.transform ( ThingMatrix ) # Changes the context to reflect that
        ## Now, change the matrix again to:
        if bos.rx != 0 and bos.ry != 0 : # Only do this if there's a special reason
            cairo.Matrix.translate( ThingMatrix, bos.rx, bos.ry ) # move it all to point of rotation
        cairo.Matrix.rotate( ThingMatrix, bos.rot ) # Do the rotation
        if bos.rx != 0 and bos.ry != 0 :        
            cairo.Matrix.translate( ThingMatrix, -bos.rx, -bos.ry ) # move it back again
        cairo.Matrix.scale( ThingMatrix, bos.sx, bos.sy ) # Now scale it all
        self.cr.transform ( ThingMatrix ) # and commit it to the context

    def draw( self ):
        cr = self.cr # Shabby shortcut.

        #---------TOP LEVEL - THE "PAGE"
        self.cr.identity_matrix  ( ) # VITAL LINE :: I'm not sure what it's doing.
        self.setToCenter ( )

        #----------FIRST LEVEL
        cr.save ( ) # Creates a 'bubble' of private coordinates. Save # 1

        ## RED - draw the red object
        self.doMatrixVoodoo ( self.red )        
        self.drawCairoStuff ( self.red  )

        #---------- SECOND LEVEL - RELATIVE TO FIRST
        cr.save ( ) #save 2

        ## GREEN - draw the green one
        self.doMatrixVoodoo ( self.green )
        self.drawCairoStuff ( self.green, col= ( 0,1,0 )  )

        ## Demonstrate how to detect a mouse hit on this shape:
        ## Draw the hit shape :: It *should* be drawn exactly over the green rectangle.
        self.drawHitShape ( )
        cr.save ( ) # Start a bubble
        cr.identity_matrix ( ) # Reset the matrix within it.
        hit = cr.in_fill ( self.x, self.y ) # Use Cairo's built-in hit test
        cr.new_path ( ) # stops the hit shape from being drawn
        cr.restore ( ) # Close the bubble like this never happened.


        cr.restore ( ) #restore 2 :: "pop" the bubble.

        ## We are in level one's influence now

        cr.restore ( ) #restore 1
        ## Back on PAGE's influence now

        #-------- THIRD LEVEL  -- RELATIVE TO PAGE
        cr.save ( ) # Creates a 'bubble' of private coordinates.
        ## Draw the blue object
        self.doMatrixVoodoo ( self.blue ) # within the bubble, this will not effect the PAGE
        self.drawCairoStuff ( self.blue, col= ( 0,0,1 )  )
        cr.restore ( )

        ## Back on the PAGE level again.

        #indicate center
        self.drawCrosshair ( )         
        self.guageScale ( )

        ## Let's animate the red object 
        ## ( which *also* moves the green because it's a 'child' 
        ## of the red by way of being in the same "bubble" )
        self.red.rot += 0.01
        ## Now animate the blue
        self.blue.sx += self.sign *  0.1
        if  self.blue.sx < 0 or self.blue.sx > 4: 
            self.sign *= -1
        self.blue.sy = self.blue.sx

        ## Print to the console -- low-tech special effects :)
        if hit: print "HIT!", self.x, self.y

    def guageScale ( self ):
        """Draw some axis so we can see where stuff is."""
        c = self.cr
        m = 0
        for x in range ( 10,210,10 ):
            m += 1
            w = 10 + ( m % 2 * 10 )
            if x == 100: w = 50
            c.rectangle ( x,-w/2,1,w )
            c.rectangle ( -x, -w/2, 1, w )
            c.rectangle ( -w/2, x, w, 1 )
            c.rectangle ( -w/2, -x , w, 1 )
        c.set_source_rgb ( 0,0,0 )
        c.fill ( )

    def drawCairoStuff ( self, bos, col= ( 1,0,0 ) ):
        """This draws the squares we see. Pass it a BagOfStuff (bos) and a colour."""
        cr = self.cr
        ## Thrillingly, we draw a rectangle.
        ## It's drawn such that 0,0 is in it's center.
        cr.rectangle( -25, -25, 50, 50 )
        cr.set_source_rgb( col[0],col[1],col[2] ) 
        cr.fill( )
        ## Now draw an axis
        self.guageScale ( )
        ## Now a visual indicator of the point of rotation
        cr.set_source_rgb( 1,1,1 )
        cr.rectangle ( bos.rx - 2, bos.ry - 2, 4, 4 )
        cr.fill ( )

    ## Same as the rectangle we see. No fill.
    def drawHitShape ( self ):
        """Draws a shape that we'll use to test hits."""
        self.cr.rectangle( -25, -25, 50, 50 ) # Same as the shape of the squares

    def drawCrosshair ( self ):
        """Another visual aid."""
        ctx = self.cr
        ctx.set_source_rgb ( 0, 0, 0 )
        ctx.move_to ( 0,10 )
        ctx.line_to ( 0, -10 )
        ctx.move_to ( -10, 0 )
        ctx.line_to ( 10, 0 )
        ctx.stroke ( )


def run( Widget, w, h, speed ):
    window = gtk.Window( )
    window.connect( "delete-event", gtk.main_quit )
    widget = Widget( w, h, speed )
    widget.show( )
    window.add( widget )
    window.present( )
    gtk.main( )

run( MyStuff, 400, 400, speed = 20 )

