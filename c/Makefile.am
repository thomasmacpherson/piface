AUTOMAKE_OPTIONS = subdir-objects
ACLOCAL_AMFLAGS = ${ACLOCAL_FLAGS}

lib_LTLIBRARIES = libpiface-1.0.la
libpiface_1_0_la_SOURCES = src/piface/pfio.c

library_includedir=$(includedir)/libpiface-1.0
library_include_HEADERS = src/piface/pfio.h

pkgconfigdir = $(libdir)/pkgconfig
pkgconfig_DATA = piface-1.0.pc
