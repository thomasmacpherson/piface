# ==========================================
#   Unity Project - A Test Framework for C
#   Copyright (c) 2007 Mike Karlesky, Mark VanderVoord, Greg Williams
#   [Released under MIT License. Please refer to license.txt for details]
# ========================================== 

C_COMPILER=gcc
TARGET = tests
OUT_FILE=-o $(TARGET)
SRC_FILES=/usr/share/cmock/vendor/unity/src/unity.c test/$(TARGET).c build/$(TARGET)_Runner.c ../src/piface/pfio.c
INC_DIRS=-I/usr/share/cmock/vendor/unity/src/ -I../src/piface/
SYMBOLS=-DTEST -DUNITY_SUPPORT_64 -std=c99

CLEANUP = rm -f build/*.o ; rm -f $(TARGET)

all: clean default

default:
	ruby /usr/share/cmock/vendor/unity/auto/generate_test_runner.rb test/$(TARGET).c build/$(TARGET)_Runner.c
	$(C_COMPILER) $(INC_DIRS) $(SYMBOLS) $(SRC_FILES) $(OUT_FILE)
	clear
	./$(TARGET)

clean:
	$(CLEANUP)
	
