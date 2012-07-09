CC=gcc
CFLAGS=-Wall

input_reader: input_reader.c ../piface/pfio.o
	$(CC) $(CFLAGS) -o input_reader input_reader.c ../piface/pfio.o

the_amazing_led_show: the_amazing_led_show.c ../piface/pfio.o
	$(CC) $(CFLAGS) -o the_amazing_led_show the_amazing_led_show.c ../piface/pfio.o

board_reset: board_reset.c ../piface/pfio.o
	$(CC) $(CFLAGS) -o board_reset board_reset.c ../piface/pfio.o

clean:
	rm *.o
