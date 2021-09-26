import spidev
import time
import numpy as np
import sys
import RPi.GPIO as GPIO

REG_PIN_CTRL = 0x02
REG_FIFO_CTRL1 = 0x07
REG_FIFO_CTRL2 = 0x08
REG_FIFO_CTRL3 = 0x09
REG_FIFO_CTRL4 = 0x0A
REG_COUNTER_BDR_REG1 = 0x0B
REG_COUNTER_BDR_REG2 = 0x0C
REG_INT1_CTRL = 0x0D
REG_INT2_CTRL = 0x0E
REG_WHO_AM_I = 0x0F
REG_CTRL1_XL = 0x10
REG_CTRL3_C = 0x12
REG_CTRL4_C = 0x13
REG_CTRL5_C = 0x14
REG_CTRL6_C = 0x15
REG_CTRL7_C = 0x16
REG_CTRL8_XL = 0x17
REG_CTRL10_C = 0x19
REG_ALL_INT_SRC = 0x1A
REG_WAKE_UP_SRC = 0x1B
REG_STATUS_REG = 0x1E
REG_OUT_TEMP_L = 0x20
REG_OUT_TEMP_H = 0x21
REG_OUTX_L_A = 0x28
REG_OUTX_H_A = 0x29
REG_OUTY_L_A = 0x2A
REG_OUTY_H_A = 0x2B
REG_OUTZ_L_A = 0x2C
REG_OUTZ_H_A = 0x2D
REG_FIFO_STATUS1 = 0x3A
REG_FIFO_STATUS2 = 0x3B
REG_TIMESTAMP0 = 0x40
REG_TIMESTAMP1 = 0x41
REG_TIMESTAMP2 = 0x42
REG_TIMESTAMP3 = 0x43
REG_SLOPE_EN = 0x56
REG_INTERRUPTS_EN = 0x58
REG_WAKE_UP_THS = 0x5B
REG_WAKE_UP_DUR = 0x5C
REG_MD1_CFG = 0x5E
REG_MD2_CFG = 0x5F
REG_INTERNAL_FREQ_FINE = 0x63
REG_X_OFS_USR = 0x73
REG_Y_OFS_USR = 0x74
REG_Z_OFS_USR = 0x75
REG_FIFO_DATA_OUT_TAG = 0x78
REG_FIFO_DATA_OUT_X_L = 0x79
REG_FIFO_DATA_OUT_X_H = 0x7A
REG_FIFO_DATA_OUT_Y_L = 0x7B
REG_FIFO_DATA_OUT_Y_H = 0x7C
REG_FIFO_DATA_OUT_Z_L = 0x7D
REG_FIFO_DATA_OUT_Z_H = 0x7E


def spi_read(spi, register):
	address = register | 0b10000000
	result = spi.xfer2([address, 0])
	value = result[1]
	return value

def spi_read_double(spi, register):
	address = register | 0b10000000
	result = spi.xfer2([address, 0, 0])
	value = (result[2] << 8 | result[1])
	if(value >= 0x8000):
		value = value - 0x10000
	return value

def spi_write(spi, register, value):
	address = register
	result = spi.xfer2([address, value])

def spi_write_double(spi, register, value):
	address = register
	result = spi.xfer2([address, value & 0b11111111, address + 1, value >> 8])

def twos_complement(value, bits):
	if(value & (1 << (bits - 1))) != 0:
		value = value - (1 << bits)
	return value

def convert_temperature(raw_value):
	return "{:.2f}".format(twos_complement(raw_value, 16) / 256.0 + 25)

def convert_acceleration(raw_value):
	g = 16
	return "{:.4f}".format(twos_complement(raw_value, 16) * (0.0305 * g) / 1000) # factors: 2 g = 0.061, 4 g = 0.122, 8 g = 0.244, 16 g = 0.488


spi = spidev.SpiDev()
bus = 0
device = 0
spi.open(bus, device)
spi.lsbfirst = False
spi.bits_per_word = 8
spi.max_speed_hz = 10_000_000
spi.mode = 0b11


spi_write(spi, REG_CTRL3_C, 0b1) # reset
time.sleep(0.02) # turn-on time is 10 ms

spi_write(spi, REG_CTRL1_XL, 0b10100100) # enable accelerometer, scale = 16 g (also set in function convert_acceleration)
time.sleep(0.01)

print("Status: " + bin(spi_read(spi, REG_STATUS_REG)))
print("Temperature: " + convert_temperature(spi_read_double(spi, REG_OUT_TEMP_L)))

useFifo = True
fifoSamplesCount = 10000

if useFifo:

	spi_write(spi, REG_FIFO_CTRL3, 0b1010) # data rate = 26667 Hz
	spi_write(spi, REG_FIFO_CTRL4, 0b110) # do not include timestamp and temperature in FIFO, FIFO mode = continuous mode

	readingsRaw = []

	for i in range(fifoSamplesCount): # we do conversion later
		readingsRaw.append(spi.xfer2([REG_FIFO_DATA_OUT_TAG | 0b10000000, 0, 0, 0, 0, 0, 0, 0]))

	for reading in readingsRaw:
		fifoTag = reading[1]
		accelerationByAxis = [None, None, None]
		for i in range(3):
			acceleration = (reading[3 + 2 * i] << 8) | reading[2 + 2 * i]
			accelerationByAxis[i] = convert_acceleration(acceleration)
		print(bin(fifoTag) + "\t" + "\t".join(accelerationByAxis))

else:

	while(True):
		print(convert_acceleration(spi_read_double(spi, REG_OUTX_L_A)) + "\t" + convert_acceleration(spi_read_double(spi, REG_OUTY_L_A)) + "\t" + convert_acceleration(spi_read_double(spi, REG_OUTZ_L_A)))
		time.sleep(0.5)
