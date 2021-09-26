import time
import smbus

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

def read_value(register):
	value = bus.read_i2c_block_data(SENSOR_I2C_ADDR, register, 1)
	return value[0]

def read_value_double(register):
	value = bus.read_i2c_block_data(SENSOR_I2C_ADDR, register, 2)
	return (value[1] << 8) | value[0]

def write_value(register, value):
	bus.write_i2c_block_data(SENSOR_I2C_ADDR, register, [value])
	time.sleep(0.1)

def set_configuration_bits(configuration, value, shift, bitsCount):
	clearBits = 0
	i = 0
	while(i < bitsCount):
		clearBits |= (1 << i)
		i += 1

	return (configuration & ~(clearBits << shift)) | (value << shift)

def print_register(register):
	print(hex(register) + ": " + str(read_value(register)))

def twos_complement(value, bits):
	if(value & (1 << (bits - 1))) != 0:
		value = value - (1 << bits)
	return value

def convert_temperature(raw_value):
	return "{:.2f}".format(twos_complement(raw_value, 16) / 256.0 + 25)

def convert_acceleration(raw_value):
	g = 2
	return "{:.4f}".format(twos_complement(raw_value, 16) * (0.0305 * g) / 1000) # factors: 2 g = 0.061, 4 g = 0.122, 8 g = 0.244, 16 g = 0.488


SENSOR_I2C_ADDR = 0x6b

bus = smbus.SMBus(1)

print_register(REG_WHO_AM_I)
print_register(REG_CTRL3_C)
print_register(REG_STATUS_REG)

write_value(REG_CTRL1_XL, 0b10100000) # enable accelerometer, scale = 2 g (also set in function convert_acceleration)
time.sleep(0.1)

while(True):
	print("")
	print("T: " + convert_temperature(read_value_double(REG_OUT_TEMP_L)))
	print("x: " + convert_acceleration(read_value_double(REG_OUTX_L_A)))
	print("y: " + convert_acceleration(read_value_double(REG_OUTY_L_A)))
	print("z: " + convert_acceleration(read_value_double(REG_OUTZ_L_A)))
	time.sleep(1)
