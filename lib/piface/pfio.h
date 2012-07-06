/**
 * pfio.h
 * functions for accessing the PiFace add-on for the Raspberry Pi
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <linux/spi/spidev.h>
#include <linux/types.h>
#include <sys/ioctl.h>

// /dev/spidev<BUS>.<DEVICE>
#define SPI_BUS    0
#define SPI_DEVICE 0
#define MAXPATH    16

typedef struct
{
    int fd;          // open file descriptor: /dev/spi-X.Y
    int mode;        // current SPI mode
    int bitsperword; // current SPI bits per word setting
    int maxspeed;    // current SPI max speed setting in Hz
} Spi;


extern char pfio_init(void);
extern char pfio_deinit(void);
/*
//extern void pfio_build_hex_string(void);
extern char pfio_digital_read(char pin_number);
extern char pfio_digital_write(char pin_number, char value);
extern char pfio_read_input(char pin_number);
extern char pfio_read_output(char pin_number);
extern char pfio_write_output(char value);
extern char pfio_get_pin_bit_mask(char pin_number);
extern char pfio_get_pin_number(char bit_mask);
*/
