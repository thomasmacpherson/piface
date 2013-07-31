#include "unity.h"
#include "pfio.h"
#include <stdint.h>

void setUp(void)
{
   uint8_t result = pfio_init();
   TEST_ASSERT_EQUAL_INT(0,result);
}

void tearDown(void)
{
   uint8_t result = pfio_deinit();
   TEST_ASSERT_EQUAL_INT(0,result);
}

void testInit(void)
{
   uint8_t result = pfio_read_output();
   TEST_ASSERT_BITS_LOW_MESSAGE(0xFF, result, "default outputs not all low");
}

void testDigitalWrite0(void)
{
   pfio_digital_write(0, 1);
   uint8_t result = pfio_read_output();
   TEST_ASSERT_BIT_HIGH_MESSAGE(0, result, "pin 0 output not set");
   pfio_digital_write(0, 0);
   result = pfio_read_output();
   TEST_ASSERT_BIT_LOW_MESSAGE(0, result, "pin 0 output not cleared");
}

void testDigitalWriteAll(void)
{
   for(uint8_t pin = 0; pin < 8; ++pin) {
	pfio_digital_write(pin, 1);
	uint8_t result = pfio_read_output();
   	TEST_ASSERT_BIT_HIGH_MESSAGE(pin, result, "output not set");
   	pfio_digital_write(pin, 0);
   	result = pfio_read_output();
        TEST_ASSERT_BIT_LOW_MESSAGE(pin, result, "output not cleared");
   }
}

void testWriteOutputAll(void)
{
   pfio_write_output(0xFF);
   uint8_t result = pfio_read_output();
   TEST_ASSERT_BITS_HIGH_MESSAGE(0xFF, result, "outputs not set");
   pfio_write_output(0);
   result = pfio_read_output();
   TEST_ASSERT_BITS_LOW_MESSAGE(0xFF, result, "outputs not cleared");
}

void testWriteOutputByBit(void)
{
   for(uint8_t pin = 0; pin < 8; ++pin) {
        pfio_write_output(1 << pin);
        uint8_t result = pfio_read_output();
        TEST_ASSERT_BIT_HIGH_MESSAGE(pin, result, "output not set");
        pfio_write_output(0);
   }
}

void testDigitalRead0(void)
{
   pfio_digital_write(0, 1);
   uint8_t result = pfio_digital_read(0);
   TEST_ASSERT_EQUAL_INT(1,result);
   pfio_digital_write(0, 0);
   result = pfio_digital_read(0);
   TEST_ASSERT_EQUAL_INT(0,result);
}

void testDigitalReadByBit(void)
{
   for(uint8_t pin = 0; pin < 8; ++pin) {
        pfio_digital_write(pin, 1);
        uint8_t result = pfio_digital_read(pin);
        TEST_ASSERT_EQUAL_INT(1,result);
        pfio_digital_write(pin, 0);
        result = pfio_digital_read(pin);
        TEST_ASSERT_EQUAL_INT(0,result);
   }
}

void testDigitalReadInput(void)
{
   pfio_write_output(0xFF);
   uint8_t result = pfio_read_input();
   TEST_ASSERT_BITS_HIGH_MESSAGE(0xFF, result, "outputs not set");
   pfio_write_output(0);
   result = pfio_read_input();
   TEST_ASSERT_BITS_LOW_MESSAGE(0xFF, result, "outputs not cleared");
}


/*
extern char pfio_init(void);
- pfio_init twice
? Interface requirements - if init called twice then call should return failure (-1) but should still be able to perform I/O
*/
/*
void testInitTwice(void)
{
   uint8_t result = pfio_init();
   TEST_ASSERT_EQUAL_INT(-1,result);
   testWriteOutputAll();
}
*/

/*
extern char pfio_deinit(void);
- pfio_deinit twice

extern char pfio_digital_read(char pin_number);
- pin_number > 7
- -ve pin_number
- 

extern void pfio_digital_write(char pin_number, char value);
- pin_number > 7
- -ve pin_number
- value > 1
- value < 0

extern char pfio_read_input(void);
extern char pfio_read_output(void);
extern void pfio_write_output(char value);
*/
