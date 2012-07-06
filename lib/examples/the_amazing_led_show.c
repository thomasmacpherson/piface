#include <unistd.h>
#include "../piface/pfio.h"

int main(void)
{
    if (pfio_init() < 0)
        exit(-1);

    char patterns[] = {0x1, 0xc, 0xd, 0x3, 0x1, 0x2, 0x4, 0x5, 0x6, 0x7};

    int i;
    for (i = 0; i < ARRAY_SIZE(patterns); i++)
    {
        pfio_write_output(patterns[i]);
        sleep(1);
    }

    pfio_deinit();
    return 0;
}
