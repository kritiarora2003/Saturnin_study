# Compiler and flags
CC = gcc
CFLAGS = -Wall -Wextra -O2

# Source files
SRCS = saturnin.c custom_encrypt.c
# If you want to include the reference encrypt.c, uncomment the next line
# SRCS += encrypt.c

# Output executable
TARGET = saturnin_test

# Build target
all: $(TARGET)

$(TARGET): $(SRCS)
	$(CC) $(CFLAGS) -o $(TARGET) $(SRCS)

# Clean target
clean:
	rm -f $(TARGET) *.o

# Run target (optional)
run: $(TARGET)
	./$(TARGET)
