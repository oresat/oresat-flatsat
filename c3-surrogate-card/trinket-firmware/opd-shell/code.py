import board
import busio
from digitalio import DigitalInOut, Direction, Pull
import supervisor
import time

commands = ["help", "scan", "enable", "disable", "reset", "status"]

# OPD Bus Addresses
# see https://docs.google.com/spreadsheets/d/1JS7-zUmwoZT049liGybgThh3jqxo8DjF8rsd_qzp3mU/edit#gid=13315181
# ADCS address is 0x1A

OPD_I2C_ADDRESS_BATTERY_1     = 0x18
OPD_I2C_ADDRESS_GPS           = 0x19
OPD_I2C_ADDRESS_ADCS          = 0x1A
OPD_I2C_ADDRESS_DXWIFI        = 0x1B
OPD_I2C_ADDRESS_STAR_TRACKER  = 0x1C
OPD_I2C_ADDRESS_CFC_OCTAVO    = 0x1D
OPD_I2C_ADDRESS_CFC_SENSOR    = 0x1E
OPD_I2C_ADDRESS_BATTERY_2     = 0x1F
OPD_I2C_ADDRESS_RW1           = 0x20
OPD_I2C_ADDRESS_RW2           = 0x21
OPD_I2C_ADDRESS_RW3           = 0x22
OPD_I2C_ADDRESS_RW4           = 0x23

opd_table = [
    ['battery-1', OPD_I2C_ADDRESS_BATTERY_1],
    ['gps', OPD_I2C_ADDRESS_GPS],
    ['adcs', OPD_I2C_ADDRESS_ADCS],
    ['dxwifi', OPD_I2C_ADDRESS_DXWIFI],
    ['star-tracker', OPD_I2C_ADDRESS_STAR_TRACKER],
    ['battery-2', OPD_I2C_ADDRESS_BATTERY_2],
    ['cfc-octavo', OPD_I2C_ADDRESS_CFC_OCTAVO],
    ['cfc-sensor', OPD_I2C_ADDRESS_CFC_SENSOR],
    ['rw1', OPD_I2C_ADDRESS_RW1],
    ['rw2', OPD_I2C_ADDRESS_RW2],
    ['rw3', OPD_I2C_ADDRESS_RW3],
    ['rw4', OPD_I2C_ADDRESS_RW4]
]

MAX7310_AD_INPUT                   = 0x00
MAX7310_AD_ODR                     = 0x01
MAX7310_AD_POL                     = 0x02
MAX7310_AD_MODE                    = 0x03
MAX7310_AD_TIMEOUT                 = 0x04

OPD_SCL                    = 0
OPD_SDA                    = 1
OPD_FAULT                  = 2
OPD_EN                     = 3
OPD_CB_RESET               = 4
OPD_BOOT0                  = 5
OPD_LINUX_BOOT             = 6
OPD_PIN7                   = 7


######################### HELPERS ##############################

def print_help():

    print("")
    print("-----------------------")
    print("Commands:")
    for cmd in commands:
        print("  ", end="")
        print(cmd)
    for row in opd_table:
        print("  opd [enable|disable] " + row[0])
    print("-----------------------")
    return

# OPD Helper Functions
def opd_enable():
    nOPD_ENABLE.value = 0
    time.sleep(1)
    if nOPD_FAULT.value==1:
        print("OPD Enabled")
    else:
        print("ERROR: Fault when trying to enable OPD")

def opd_disable():
    nOPD_ENABLE.value = 1
    print("OPD Disabled")

def opd_reset():
    nOPD_ENABLE.value = 1
    time.sleep(2)
    nOPD_ENABLE.value = 0
    time.sleep(1)
    if nOPD_FAULT.value==1:
        print("OPD Reset and Enabled")
    else:
        print("ERROR: Fault when trying to reset OPD")

def opd_status():
    if nOPD_FAULT.value == 1:
        print("OPD power OK")
    else:
        print("OPD power FAULT")


def probe_i2c():
    if i2c.try_lock():
        for row in opd_table:
            addr = row[1]
            found = False
            try:
                result = bytearray(2)
                i2c.readfrom_into(addr, result)
                found = True
            except Exception:
                pass

            print("I2C device at address 0x%X (%13s): %s" %(addr, row[0], ("FOUND" if found else "not found")))
            time.sleep(0.005)

        i2c.unlock()
    return


#def i2c_read_reg(addr, reg, result):
#    if i2c.try_lock():
#        try:
#            i2c.writeto_then_readfrom(addr, bytes([reg]), result)
#            return result
#        except Exception:
#            print("Failed to read from i2c address 0x%X" % addr)
#        finally:
#            i2c.unlock()


#def i2c_write_reg(addr, reg, data):
#    if i2c.try_lock():
#        try:
#            buf = bytearray(1)
#            buf[0] = reg
#            buf.extend(data)
#            i2c.writeto(addr, buf)
#        except Exception:
#            print("Failed to write to address 0x%X: reg=0x%X" % (addr, reg))
#        finally:
#            i2c.unlock()


#def opd_en_pin_mode(i2c_addr):
#  result = bytearray(1)

#    i2c_read_reg(i2c_addr, MAX7310_AD_MODE, result)
#    result[0] &= ~(1 << OPD_EN)  # Set the EN pin to output mode
#    i2c_write_reg(i2c_addr, MAX7310_AD_MODE, result)


def opt_print_status(i2c_addr):
    result = bytearray(1)
    print("====================")
    i2c_read_reg(i2c_addr, MAX7310_AD_INPUT, result)
    print("MAX7310_AD_INPUT = 0x%X" % result[0])

    i2c_read_reg(i2c_addr, MAX7310_AD_ODR, result)
    print("MAX7310_AD_ODR   = 0x%X" % result[0])

    i2c_read_reg(i2c_addr, MAX7310_AD_POL, result)
    print("MAX7310_AD_POL   = 0x%X" % result[0])

    i2c_read_reg(i2c_addr, MAX7310_AD_MODE, result)
    print("MAX7310_AD_MODE  = 0x%X" % result[0])

    return


#def set_max7310_pin(i2c_addr, pin_num):
#    result = bytearray(1)
#    i2c_read_reg(i2c_addr, MAX7310_AD_ODR, result)
#    result[0] |= (1 << pin_num)
#    i2c_write_reg(i2c_addr, MAX7310_AD_ODR, result)
#    return


#def clear_max7310_pin(i2c_addr, pin_num):
#    result = bytearray(1)
#    i2c_read_reg(i2c_addr, MAX7310_AD_ODR, result)
#    result[0] &= ~(1 << pin_num)
#    i2c_write_reg(i2c_addr, MAX7310_AD_ODR, result)
#    return


def opd_enable_disable_node(i2c_addr, enable_flag):
    opd_en_pin_mode(i2c_addr)
    if enable_flag:
        set_max7310_pin(i2c_addr, OPD_EN)
    else:
        clear_max7310_pin(i2c_addr, OPD_EN)
    return

######################### MAIN ##############################

# Setup
#gc.collect()
#print(f"Memory free: {gc.mem_free()} bytes")

# Built in red LED, turn on
led = DigitalInOut(board.D13)
led.direction = Direction.OUTPUT
led.value = 1

# Set OPD Enable as output, Off by default
nOPD_ENABLE = DigitalInOut(board.D3)
nOPD_ENABLE.direction = Direction.OUTPUT
nOPD_ENABLE.value = 1

# OPD Fault Input with Pull-up
nOPD_FAULT = DigitalInOut(board.D4)
nOPD_FAULT.direction = Direction.INPUT
nOPD_FAULT.pull = Pull.UP

# Turn on I2C w/freq = 100kHz
#i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)

# OPD_ISET set as floating input
OPD_ISET = DigitalInOut(board.D1)
OPD_ISET.direction = Direction.INPUT


# Start OPD Shell
print()
print("OPD Shell")
print("!! DISCONNECT (OR HOLD IN RESET) ANY C3 ON THE BUS BEFORE TURNING ON THE C3S OPD !!")
print("Type 'help' for commands")
print("> ", end="")

i = 0
while True:
    led.value = not led.value

    if supervisor.runtime.serial_bytes_available:
        value = input().strip()
        if value == "":
            continue

        handled_command = False

        if value == "help":
            print_help()
            handled_command = True
        # OPD Commands
        elif value == "scan":
            print(f"scan has not been implemented yet")
            handled_command = True
        elif value == "enable":
            opd_enable()
            handled_command = True
        elif value == "disable":
            opd_disable()
            handled_command = True
        elif value == "reset":
            opd_reset()
            handled_command = True
        elif value == "status":
            opd_status()
            handled_command = True

        # MAX7310 Commands
        elif value == "address":
            handled_command = True
        elif value == "direction":
            handled_command = True
        elif value == "write":
            handled_command = True
        elif value =="read":
            handled_command = True

        # Node Commands
        elif value == "node":
            handled_command = True
        elif value == "on":
            handled_command = True
        elif value == "off":
            handled_command = True
        elif value == "check":
            handled_command = True
        elif value == "retry":
            handled_command = True

        elif value == "bus":
            i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
            handled_command = True
        elif value == "probe":
            probe_i2c()
            handled_command = True

        if not handled_command:
            print("Unknown command")

        print("> ", end="")

    time.sleep(1.20)
