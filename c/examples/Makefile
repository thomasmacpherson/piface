CC=gcc
CFLAGS=-Wall
INCLUDES=-L/usr/local/lib/ -lpiface-1.0

input_reader: input_reader.c
	$(CC) $(CFLAGS) $(INCLUDES) -o input_reader input_reader.c

the_amazing_led_show: the_amazing_led_show.c
	$(CC) $(CFLAGS) $(INCLUDES) -o the_amazing_led_show the_amazing_led_show.c

board_reset: board_reset.c
	$(CC) $(CFLAGS) $(INCLUDES) -o board_reset board_reset.c

clean:
	rm *.o
