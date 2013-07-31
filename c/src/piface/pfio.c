/**
 * pfio.c
 * functions for accessing the PiFace add-on for the Raspberry Pi
 */
#include "pfio.h"
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

#undef VERBOSE_MODE

static Spi * spi;

static void spi_transfer(uint8_t * txbuffer, uint8_t * rxbuffer);
static void spi_write(uint8_t port, uint8_t value);
static uint8_t spi_read(uint8_t port);


int pfio_init(void)
{
    if ((spi = malloc(sizeof(Spi))) == NULL)
        return -1;

    // initialise the spi with some values
    // create the path string
    char path[MAXPATH];
    if (snprintf(path, MAXPATH, "/dev/spidev%d.%d", SPI_BUS, SPI_DEVICE) >= MAXPATH)
    {
        fprintf(stderr, "ERROR: Bus and/or device number is invalid.");
        return -1;
    }

    // try to open the device
    if ((spi->fd = open(path, O_RDWR, 0)) < 0)
    {
        fprintf(stderr, "ERROR: Can not open device");
        return -1;
    }

    // try to control the device
    uint8_t temp;
    if (ioctl(spi->fd, SPI_IOC_RD_MODE, &temp) < 0)
    {
        fprintf(stderr, "ERROR: Can not get spi mode");
        return -1;
    }
    spi->mode = temp;

    // try to get the bits per word
    if (ioctl(spi->fd, SPI_IOC_RD_BITS_PER_WORD, &temp) < 0)
    {
        fprintf(stderr, "ERROR: Can not get bits per word");
        return -1;
    }
    spi->bitsperword = temp;

    // try to get the max speed
    int maxspeed;
    if (ioctl(spi->fd, SPI_IOC_RD_MAX_SPEED_HZ, &maxspeed) < 0)
    {
        fprintf(stderr, "ERROR: Can not get max speed hz");
        return -1;
    }
    spi->maxspeed = maxspeed;

    // set up the ports
    // fixed SPI addresses so that we don't have that annoying
    // LED flashing when initializing pfio.
    spi_write(IOCON,  8); // enable hardware addressing
    spi_write(GPIOA, 0x00); // turn on port A
    spi_write(IODIRA, 0); // set port A as an output
    spi_write(IODIRB, 0xFF); // set port B as an input
    spi_write(GPPUB, 0xFF); // turn on port B pullups

    // initialise all outputs to 0
    int i;
    for (i = 1; i <= 8; i++)
        pfio_digital_write(i, 0);

    return 0;
}

int pfio_deinit(void)
{
    close(spi->fd);
    free(spi);
    return 0;
}

uint8_t pfio_digital_read(uint8_t pin_number)
{
    uint8_t current_pin_values = pfio_read_input();
    uint8_t pin_bit_mask = pfio_get_pin_bit_mask(pin_number);
    // note: when using bitwise operators and checking if a mask is
    // in there it is always better to check if the result equals
    // to the desidered mask, in this case pin_bit_mask.
    return ( current_pin_values & pin_bit_mask ) == pin_bit_mask;
}

void pfio_digital_write(uint8_t pin_number, uint8_t value)
{
    uint8_t pin_bit_mask = pfio_get_pin_bit_mask(pin_number);
    uint8_t old_pin_values = pfio_read_output();

    uint8_t new_pin_values;
    if (value > 0)
        new_pin_values = old_pin_values | pin_bit_mask;
    else
        new_pin_values = old_pin_values & ~pin_bit_mask;

#ifdef VERBOSE_MODE
    printf("digital_write: pin number %d, value %d\n", pin_number, value);
    printf("pin bit mask: 0x%x\n", pin_bit_mask);
    printf("old pin values: 0x%x\n", old_pin_values);
    printf("new pin values: 0x%x\n", new_pin_values);
    printf("\n");
#endif

    pfio_write_output(new_pin_values);
}

uint8_t pfio_read_input(void)
{
    // XOR by 0xFF so we get the right outputs.
    // before a turned off input would read as 1,
    // confusing developers.
    return spi_read(INPUT_PORT) ^ 0xFF;
}
    
uint8_t pfio_read_output(void)
{
    return spi_read(OUTPUT_PORT);
}

void pfio_write_output(uint8_t value)
{
    spi_write(OUTPUT_PORT, value);
}

uint8_t pfio_get_pin_bit_mask(uint8_t pin_number)
{
    // removed - 1 to reflect pin numbering of
    // the python interface (0, 1, ...) instead
    // of (1, 2, ...)
    return 1 << pin_number;
}

uint8_t pfio_get_pin_number(uint8_t bit_pattern)
{
    uint8_t pin_number = 0; // assume pin 0
    while ((bit_pattern & 1) == 0)
    {
        bit_pattern >>= 1;
        if (++pin_number > 7)
        {
            pin_number = 0;
            break;
        }
    }
    return pin_number;
}


static void spi_transfer(uint8_t * txbuffer, uint8_t * rxbuffer)
{
    // set up some transfer information
    struct spi_ioc_transfer transfer_buffer = 
    {
        .tx_buf = (unsigned long) txbuffer,
        .rx_buf = (unsigned long) rxbuffer,
        .len = TRANSFER_LEN,
        .delay_usecs = TRANSFER_DELAY,
        .speed_hz = TRANSFER_SPEED,
        .bits_per_word = TRANSFER_BPW,
    };

    // actually do the transfer
    if (ioctl(spi->fd, SPI_IOC_MESSAGE(1), &transfer_buffer) < 1)
    {
        fprintf(stderr, "ERROR: Can not send SPI message");
        perror(0);
    }
}

static void spi_write(uint8_t port, uint8_t value)
{
    uint8_t txbuffer[] = {SPI_WRITE_CMD, port, value};
    uint8_t rxbuffer[ARRAY_SIZE(txbuffer)];
    spi_transfer(txbuffer, rxbuffer);
}

static uint8_t spi_read(uint8_t port)
{
    uint8_t txbuffer[] = {SPI_READ_CMD, port, 0xff};
    uint8_t rxbuffer[ARRAY_SIZE(txbuffer)];
    spi_transfer(txbuffer, rxbuffer);
    return rxbuffer[2];
}
