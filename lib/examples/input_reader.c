#include <unistd.h>
#include "../piface/pfio.h"

int main(void)
{
    if (pfio_init() < 0)
        exit(-1);

    while (1)
    {
        printf("Input port: 0x%x\n", pfio_read_input());
        sleep(1);
    }

    pfio_deinit();
    return 0;
}
