import board
import busio
from digitalio import DigitalInOut, Direction, Pull
import supervisor
import time
from opd import * 

commands = ["help", "scan", "enable", "disable", "reset", "status"]

address = 0 # default current address
i2c = None

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
    global i2c
    nOPD_ENABLE.value = 0
    time.sleep(1)
    if nOPD_FAULT.value==1:
        print("OPD Enabled")
        i2c = busio.I2C(board.SCL, board.SDA, frequency=100000) # Singleton
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

def max_address():
    # Sets device address for subsequent commands
    global address
    if len(value)>len("address"):
        # TODO: check for space
        addr_str = value[7:].strip()
        # TODO: check not empty
        if addr_str[:2] == "0x":        # hexadecimal value
            address = int(addr_str,16)
        elif addr_str[:2] == "0b":      # binary value
            address = int(addr_str,2)     
        else:                           # decimal value
            address = int(addr_str)
    
    # check device found at new address
    # otherwise set to 0 (no address set)
    i2c.try_lock()
    found = i2c.probe(address)
    i2c.unlock()

    if found:
        print("Current address is set to %s" % hex(address))
    elif address == 0:
        print("Address not set")
    else:
        print("No MAX7310 found at %s" % hex(address))
        address = 0


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
            opd_scan(i2c)
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
        elif value[:7] == "address":
            max_address()
            handled_command = True
        elif value == "direction":
            
            handled_command = True
        elif value == "write":
            handled_command = True
        elif value =="read":
            max_read(i2c, address)
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
            print("I2C bus turned on")
            handled_command = True
        elif value == "probe":
            probe_i2c(i2c)
            handled_command = True

        if not handled_command:
            print("Unknown command")

        print("> ", end="")

    time.sleep(1)
