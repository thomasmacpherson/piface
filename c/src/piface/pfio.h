/**
 * pfio.h
 * functions for accessing the PiFace add-on for the Raspberry Pi
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <linux/spi/spidev.h>
#include <linux/types.h>
#include <sys/ioctl.h>

// /dev/spidev<BUS>.<DEVICE>
#define SPI_BUS    0
#define SPI_DEVICE 0
#define MAXPATH    16

#define TRANSFER_LEN   3
#define TRANSFER_DELAY 5
#define TRANSFER_SPEED 1000000
#define TRANSFER_BPW   8

#define SPI_WRITE_CMD 0x40
#define SPI_READ_CMD 0x41

// Port configuration
#define IODIRA 0x00 // I/O direction A
#define IODIRB 0x01 // I/O direction B
#define IOCON  0x0A // I/O config
#define GPIOA  0x12 // port A
#define GPIOB  0x13 // port B
#define GPPUA  0x0C // port A pullups
#define GPPUB  0x0D // port B pullups
#define OUTPUT_PORT GPIOA
#define INPUT_PORT  GPIOB

#define ARRAY_SIZE(a) (sizeof(a) / sizeof((a)[0]))


typedef struct
{
    int fd;          // open file descriptor: /dev/spi-X.Y
    int mode;        // current SPI mode
    int bitsperword; // current SPI bits per word setting
    int maxspeed;    // current SPI max speed setting in Hz
} Spi;


extern char pfio_init(void);
extern char pfio_deinit(void);
extern char pfio_digital_read(char pin_number);
extern void pfio_digital_write(char pin_number, char value);
extern char pfio_read_input(void);
extern char pfio_read_output(void);
extern void pfio_write_output(char value);
extern char pfio_get_pin_bit_mask(char pin_number);
extern char pfio_get_pin_number(char bit_mask);

/*
static void spi_transfer(char * txbuffer, char * rxbuffer);
static void spi_write(char port, char value);
static char spi_read(char port);
*/
