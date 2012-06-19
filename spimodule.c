/*
 * spimodule.c - Python bindings for Linux SPI access through spidev
 * Copyright (C) 2009 Volker Thoms <unconnected@gmx.de>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; version 2 of the License.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
 */

#include <Python.h>
#include "structmember.h"
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <fcntl.h>
#include <linux/spi/spidev.h>
#include <linux/types.h>
#include <sys/ioctl.h>

#define VERBOSE_MODE // comment out to turn off debugging

#define ARRAY_SIZE(a) (sizeof(a) / sizeof((a)[0]))
#define MAXPATH 16

PyDoc_STRVAR(SPI_module_doc,
	"This module defines an object type that allows SPI transactions\n"
	"on hosts running the Linux kernel. The host kernel must have SPI\n"
	"support and SPI device interface support.\n"
	"All of these can be either built-in to the kernel, or loaded from\n"
	"modules.\n"
	"\n"
	"Because the SPI device interface is opened R/W, users of this\n"
	"module usually must have root permissions.\n");
	
typedef struct {
	PyObject_HEAD

	int fd;	/* open file descriptor: /dev/spi-X.Y */
	uint8_t mode;	/* current SPI mode */
	uint8_t bpw;	/* current SPI bits per word setting */
	uint32_t msh;	/* current SPI max speed setting in Hz */
} SPI;

static PyObject *
SPI_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	SPI *self;
	if ((self = (SPI *)type->tp_alloc(type, 0)) == NULL)
		return NULL;

	self->fd = -1;
	self->mode = 0;
	self->bpw = 0;
	self->msh = 0;

	Py_INCREF(self);
	return (PyObject *)self;
}

PyDoc_STRVAR(SPI_close_doc,
	"close()\n\n"
	"Disconnects the object from the interface.\n");

	
static PyObject *SPI_close(SPI *self)
{
	if ((self->fd != -1) && (close(self->fd) == -1)) {
		PyErr_SetFromErrno(PyExc_IOError);
		return NULL;
	}

	self->fd = -1;
	self->mode = 0;
	self->bpw = 0;
	self->msh = 0;

	Py_INCREF(Py_None);
	return Py_None;
}

PyDoc_STRVAR(SPI_transfer_doc,
	"transfer([values]) -> [values]\n\n"
	"Perform SPI transaction.\n"
	"CS will be released and reactivated between blocks.\n"
	"delay specifies delay in usec between blocks.\n");

	

static PyObject* SPI_transfer(SPI *self, PyObject *args)
{
	uint8_t bits = 8;
	int ret = 0;
	char* list;
	int length_list = 1;
	uint16_t delay = 5;
	uint32_t speed = 1000000;
	int i=0;

	PyArg_ParseTuple(args, "s|i:transfer", &list, &length_list);
#ifdef VERBOSE_MODE
	printf ("Length of String List from Python: %d\n", length_list);
	printf ("Read in String List from Python: %s\n", list);
#endif

	char hexbyte[3] = {0};
	uint8_t tx[length_list];
	for (i=0; i < (length_list); i++){

		//should grab first two characters
		//printf("Should grab %c%c\n",list[2*i], list[(2*i)+1]);

		//Data Transfer from String list to 2 byte string
		hexbyte[0] = list[2*i];
		hexbyte[1] = list[(2*i)+1];

		//Passing the 2 byte string into a Hex unsigned int 8-bit and then printing result
		sscanf(hexbyte, "%X", &tx[i]);
		printf("Got HEX: 0x%2.2X\n\n",tx[i]);
	}

#ifdef VERBOSE_MODE
	//printf("TX array size after conversion: %d\n",ARRAY_SIZE(tx));

	printf("Data for SPI to Transmit!!  TX:  ");
	for (ret=0; ret<ARRAY_SIZE(tx); ret++){
		printf("%.2X ",tx[ret]);
	}
	puts(""); // newline
#endif

	uint8_t rx[ARRAY_SIZE(tx)];

	/*This is the transfer part, and sets up
	the details needed to transfer the data*/
	struct spi_ioc_transfer tr = {
		.tx_buf = (unsigned long)tx,
		.rx_buf = (unsigned long)rx,
		.len = ARRAY_SIZE(tx),
		.delay_usecs = delay,
		.speed_hz = speed,
		.bits_per_word = bits,
	};

	//The actual transfer command and data, does send and receive!! Very important!
	ret = ioctl(self->fd, SPI_IOC_MESSAGE(1), &tr);
	if (ret < 1){

		printf("ERROR: Can't send spi message");
		perror(0);
	}

#ifdef VERBOSE_MODE
	//This part prints the Received data of the SPI transmission of equal size to TX
	//printf("Data that was received from SPI!!  RX:  ");
	
	for (ret = 0; ret < ARRAY_SIZE(tx); ret++) {
		if (!(ret % 6))
			puts("");
		printf("%.2X ", rx[ret]);
		
		
	}
	puts(""); // newline
#endif

	Py_INCREF(list);

	//return list;
	return Py_BuildValue("[i,i,i,i,i,i]", rx[0],rx[1],rx[2],rx[3],rx[4],rx[5]);

}

PyDoc_STRVAR(SPI_open_doc,
	"open(bus, device)\n\n"
	"Connects the object to the specified SPI device.\n"
	"open(X,Y) will open /dev/spidev-X.Y\n");
	
	
static PyObject *SPI_open(SPI *self, PyObject *args, PyObject *kwds)
{
	int bus, device;
	char path[MAXPATH];
	uint8_t tmp8;
	uint32_t tmp32;
	static char *kwlist[] = {"bus", "device", NULL};
	if (!PyArg_ParseTupleAndKeywords(args, kwds, "ii:open", kwlist, &bus, &device))
		return NULL;
	if (snprintf(path, MAXPATH, "/dev/spidev%d.%d", bus, device) >= MAXPATH) {
		PyErr_SetString(PyExc_OverflowError,
			"Bus and/or device number is invalid.");
		return NULL;
	}
	if ((self->fd = open(path, O_RDWR, 0)) < 0) {
		printf("can't open device");
		abort();
	}
	if (ioctl(self->fd, SPI_IOC_RD_MODE, &tmp8) == -1) {
		printf("can't get spi mode");
		abort();
	}
	self->mode = tmp8;
	if (ioctl(self->fd, SPI_IOC_RD_BITS_PER_WORD, &tmp8) == -1) {
		printf("can't get bits per word");
		abort();
	}
	self->bpw = tmp8;
	if (ioctl(self->fd, SPI_IOC_RD_MAX_SPEED_HZ, &tmp32) == -1) {
		printf("can't get max speed hz");
		abort();
	}
	self->msh = tmp32;

	Py_INCREF(Py_None);
	return Py_None;
}

static int SPI_init(SPI *self, PyObject *args, PyObject *kwds)
{
	int bus = -1;
	int client = -1;
	static char *kwlist[] = {"bus", "client", NULL};

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "|ii:__init__",
			kwlist, &bus, &client))
		return -1;

	if (bus >= 0) {
		SPI_open(self, args, kwds);
		if (PyErr_Occurred())
			return -1;
	}

	return 0;
}


static PyMethodDef SPI_module_methods[] = {
   { NULL },
};

PyDoc_STRVAR(SPI_type_doc,
	"SPI([bus],[client]) -> SPI\n\n"
	"Return a new SPI object that is (optionally) connected to the\n"
	"specified SPI device interface.\n");

static PyMethodDef SPI_methods[] = {
   {"open", (PyCFunction)SPI_open, METH_VARARGS | METH_KEYWORDS, 
		SPI_open_doc},
   {"close", (PyCFunction)SPI_close, METH_NOARGS,
		SPI_close_doc},
   {"transfer", (PyCFunction)SPI_transfer, METH_VARARGS, 
		SPI_transfer_doc},
	{NULL},
};

static PyTypeObject SPI_type = {
	PyObject_HEAD_INIT(NULL)
	0,				/* ob_size */
	"SPI",			/* tp_name */
	sizeof(SPI),	/* tp_basicsize */
	0,				/* tp_itemsize */
	0,	            /* tp_dealloc */
	0,				/* tp_print */
	0,				/* tp_getattr */
	0,				/* tp_setattr */
	0,				/* tp_compare */
	0,				/* tp_repr */
	0,				/* tp_as_number */
	0,				/* tp_as_sequence */
	0,				/* tp_as_mapping */
	0,				/* tp_hash */
	0,				/* tp_call */
	0,				/* tp_str */
	0,				/* tp_getattro */
	0,				/* tp_setattro */
	0,				/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT,		/* tp_flags */
	SPI_type_doc,			/* tp_doc */
	0,				/* tp_traverse */
	0,				/* tp_clear */
	0,				/* tp_richcompare */
	0,				/* tp_weaklistoffset */
	0,				/* tp_iter */
	0,				/* tp_iternext */
	SPI_methods,	/* tp_methods */
	0,				/* tp_members */
	0,		    	/* tp_getset */
	0,				/* tp_base */
	0,				/* tp_dict */
	0,				/* tp_descr_get */
	0,				/* tp_descr_set */
	0,				/* tp_dictoffset */
	(initproc)SPI_init,		/* tp_init */
	0,				/* tp_alloc */
	SPI_new,			/* tp_new */
};

#ifndef PyMODINIT_FUNC	/* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif

PyMODINIT_FUNC initspi(void)
{
	PyObject* m;

	if (PyType_Ready(&SPI_type) < 0)
		return;

	m = Py_InitModule3("spi", SPI_module_methods, SPI_module_doc);
	Py_INCREF(&SPI_type);
	PyModule_AddObject(m, "SPI", (PyObject *)&SPI_type);
}
