#!/usr/bin/env python
import sys
import gtk
import cairo

def expose (da, event, pixbuf):
  ctx = da.window.cairo_create()
  # You can put ctx.scale(..) or ctx.rotate(..) here, if you need some
  ctx.set_source_pixbuf(pixbuf,0,0)
  ctx.paint()
  ctx.stroke()

def main():
  filename = sys.argv[1]
  pixbuf = gtk.gdk.pixbuf_new_from_file(filename)
  imgw=pixbuf.get_width()
  imgh=pixbuf.get_height()
  win = gtk.Window()
  win.connect('destroy', gtk.main_quit)
  win.set_default_size(imgw, imgh)
  da = gtk.DrawingArea()
  win.add(da)
  da.connect('expose_event', expose, pixbuf)
  win.show_all()
  gtk.main()

if __name__ == '__main__':
  if len(sys.argv) != 2:
    program = sys.argv[0]
    print program +':', 'usage:', program, '<filename>'
    sys.exit(0)
  else:
    main()

