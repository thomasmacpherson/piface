/**
 * pfio.c
 * functions for accessing the PiFace add-on for the Raspberry Pi
 */
#include "pfio.h"

static Spi * spi;

#define SPI_BUS 0
#define SPI_DEVICE 0
#define MAXPATH 16

char pfio_init(void)
{
    if ((spi = malloc(sizeof(Spi))) == NULL)
        return -1;

    // initialise the spi with some values
    // create the path string
    char path[MAXPATH];
    if (snprintf(path, MAXPATH, "/dev/spidev%d.%d", SPI_BUS, SPI_DEVICE) >= MAXPATH)
    {
        fprintf(stderr, "Bus and/or device number is invalid.");
        return -1;
    }

    // try to open the device
    if ((spi->fd = open(path, O_RDWR, 0)) < 0)
    {
        fprintf(stderr, "can not open device");
        return -1;
    }

    // try to control the device
    char temp;
    if (ioctl(spi->fd, SPI_IOC_RD_MODE, &temp) < 0)
    {
        fprintf(stderr, "can not get spi mode");
        return -1;
    }
    spi->mode = temp;

    // try to get the bits per word
    if (ioctl(spi->fd, SPI_IOC_RD_BITS_PER_WORD, &temp) < 0)
    {
        fprintf(stderr, "can not get bits per word");
        return -1;
    }
    spi->bitsperword = temp;

    // try to get the max speed
    int maxspeed;
    if (ioctl(spi->fd, SPI_IOC_RD_MAX_SPEED_HZ, &maxspeed) < 0)
    {
        fprintf(stderr, "can not get max speed hz");
        return -1;
    }
    spi->maxspeed = maxspeed;
}

char pfio_deinit(void)
{
    close(spi->fd);
    free(spi);
    return 0;
}

int main(void)
{
    if (pfio_init() < 0)
        exit(-1);

    printf("SPI max speed: %d", spi->maxspeed);

    pfio_deinit();
}
