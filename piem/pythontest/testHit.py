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
from math import pi



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
        self.width, self.height = w, h
        self.set_size_request ( w, h )
        self.x, self.y = 11110,11111110 #unlikely first coord to prevent false hits.

    ## When expose event fires, this is run
    def do_expose_event( self, widget, event ):
        self.cr = self.window.cairo_create( )
        ## Call our draw function to do stuff.
        self.draw( )

    def _mouseMoved ( self, widget, event ):
        self.x = event.x
        self.y = event.y
	self.queue_draw_area(0, 0, 350, 350)




class MyStuff ( Screen ):
    """This class is also a Drawing Area, coming from Screen."""
    def __init__ ( self, w, h, speed):
        Screen.__init__( self, w, h, speed )
        self.isOn = 0


    def draw( self ):
        cr = self.cr # Shabby shortcut.

        #---------TOP LEVEL - THE "PAGE"
        self.cr.identity_matrix  ( ) # VITAL LINE :: I'm not sure what it's doing.
        cr.save ( ) # Start a bubble     

	self.surface = cairo.ImageSurface.create_from_png("pi.png")
	cr.set_source_surface(self.surface, 0, 0)


	cr.rectangle( 0, 0, 350, 250 )
#        cr.set_source_rgb( 1,0,0 ) 
	cr.set_source_surface(self.surface, 0, 0)
        cr.fill( )
        cr.new_path ( ) # stops the hit shape from being drawn
        cr.restore ( ) 

	if self.isOn:        
		cr.save ( ) 
		cr.set_source_rgb( 1,1,0 ) 
		cr.arc (183.0, 135.0, 8, 0, 2*pi);
		cr.fill( )
		cr.restore ( )
		
		cr.save ( )    
		cr.set_source_rgb( 1,0,0 ) 
		cr.arc (183.0, 135.0, 6, 0, 2*pi);
		cr.fill( )
		cr.restore ( ) 

        ## Demonstrate how to detect a mouse hit on this shape:
        ## Draw the hit shape :: It *should* be drawn exactly over the green rectangle.
        self.drawHitShape ( )
        cr.save ( ) # Start a bubble
        cr.identity_matrix ( ) # Reset the matrix within it.
        hit = cr.in_fill ( self.x, self.y ) # Use Cairo's built-in hit test
        cr.new_path ( ) # stops the hit shape from being drawn
        cr.restore ( ) # Close the bubble like this never happened.

       	self.isOn = hit

        ## Print to the console -- low-tech special effects :)
#        if hit: 
#       	print "HIT!", self.x, self.y




    def drawCairoStuff ( self, bos, col= ( 1,0,0 ) ):
        """This draws the squares we see. Pass it a BagOfStuff (bos) and a colour."""
        cr = self.cr
        ## Thrillingly, we draw a rectangle.
        ## It's drawn such that 0,0 is in it's center.
        cr.rectangle( -25, -25, 50, 50 )
        cr.set_source_rgb( col[0],col[1],col[2] ) 
        cr.fill( )
        ## Now draw an axis
        #self.guageScale ( )
        ## Now a visual indicator of the point of rotation
        cr.set_source_rgb( 1,1,1 )
        cr.rectangle ( bos.rx - 2, bos.ry - 2, 4, 4 )
        cr.fill ( )

    ## Same as the rectangle we see. No fill.
    def drawHitShape ( self ):
        """Draws a shape that we'll use to test hits."""
        #self.cr.rectangle( 0, 0, 350, 250 ) # Same as the shape of the squares
        self.cr.arc (183.0, 134.0, 6, 0, 2*pi);



def run( Widget, w, h, speed ):
    window = gtk.Window( )
    window.connect( "delete-event", gtk.main_quit )
    widget = Widget( w, h, speed )
    widget.show( )
    window.add( widget )
    window.present( )
    gtk.main( )

run( MyStuff, 400, 400, speed = 20 )

