import board
import digitalio
import analogio
import time
iset = analogio.AnalogIn(board.A0)
opd_enable_n = digitalio.DigitalInOut(board.D3)
opd_enable_n.direction = digitalio.Direction.OUTPUT
fault_n = digitalio.DigitalInOut(board.D4)
fault_n.direction = digitalio.Direction.INPUT

opd_enable_n.value = False
time.sleep(.1)
print("/Fault = ", fault_n.value)
print("ISET = ", iset.value)
i2c = board.I2C()

while not i2c.try_lock():
    pass

cfc_card = 0x1D
cfc_sensor_card = 0x1E

result = bytearray(1)

try:
    i2c.writeto(cfc_card, bytes([3,0b10000]))
    time.sleep(.1)
    i2c.writeto(cfc_card, bytes([1,0b1000]))
    i2c.writeto_then_readfrom(cfc_card, bytes([1]), result)
    i2c.writeto(cfc_sensor_card, bytes([3,0b10000]))
    time.sleep(.1)
    i2c.writeto(cfc_sensor_card, bytes([1,0b1000]))
    i2c.writeto_then_readfrom(cfc_sensor_card, bytes([1]), result)
    while 1:
        continue

finally:
    i2c.writeto(cfc_sensor_card, bytes([1,0b0]))
    i2c.writeto_then_readfrom(cfc_sensor_card, bytes([1]), result)
    print(hex(result[0]))
    i2c.writeto(cfc_card, bytes([1,0b0]))
    i2c.writeto_then_readfrom(cfc_card, bytes([1]), result)
    print(hex(result[0]))
    i2c.unlock()
