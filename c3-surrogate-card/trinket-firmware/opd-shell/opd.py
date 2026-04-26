import board
import busio
from digitalio import DigitalInOut, Direction, Pull
import time

# see https://docs.google.com/spreadsheets/d/1JS7-zUmwoZT049liGybgThh3jqxo8DjF8rsd_qzp3mU/edit#gid=13315181
# ADCS address is 0x1A

OPD_I2C_ADDRESS_DIODE         = 0x11
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

MAX7310_AD_INPUT              = 0x00
MAX7310_AD_ODR                = 0x01
MAX7310_AD_POL                = 0x02
MAX7310_AD_MODE               = 0x03
MAX7310_AD_TIMEOUT            = 0x04

OPD_SCL                    = 0
OPD_SDA                    = 1
OPD_FAULT                  = 2
OPD_EN                     = 3
OPD_CB_RESET               = 4
OPD_BOOT0                  = 5
OPD_LINUX_BOOT             = 6
OPD_UART_EN                = 7 

opd_table = [
    ['diode-test',   OPD_I2C_ADDRESS_DIODE],
    ['battery-1',    OPD_I2C_ADDRESS_BATTERY_1],
    ['gps',          OPD_I2C_ADDRESS_GPS],
    ['adcs',         OPD_I2C_ADDRESS_ADCS],
    ['dxwifi',       OPD_I2C_ADDRESS_DXWIFI],
    ['star-tracker', OPD_I2C_ADDRESS_STAR_TRACKER],
    ['battery-2',    OPD_I2C_ADDRESS_BATTERY_2],
    ['cfc-octavo',   OPD_I2C_ADDRESS_CFC_OCTAVO],
    ['cfc-sensor',   OPD_I2C_ADDRESS_CFC_SENSOR],
    ['rw1',          OPD_I2C_ADDRESS_RW1],
    ['rw2',          OPD_I2C_ADDRESS_RW2],
    ['rw3',          OPD_I2C_ADDRESS_RW3],
    ['rw4',          OPD_I2C_ADDRESS_RW4]
]

commands = ["help", "scan", "enable", "disable", "reset", "status",
            "probe", "read", "write",
            "node", "on", "off", "check", "retry", "serialon", "serialoff", "boothigh", "bootlow", "bootrelease"]

######################### HELPERS ##############################

def print_help():

    print("")
    print("-----------------------")
    print("Commands:")
    for cmd in commands:
        print("  ", end="")
        print(cmd)
    # for row in opd_table:
    #     print("  opd [enable|disable] " + row[0])
    print("-----------------------")
    return

def set_bit(value, bit):
    return value | (1<<bit)

def clear_bit(value, bit):
    return value & ~(1<<bit)

def toggle_bit(value, bit):
    return value ^ (1<<bit)  

def get_bit(value, bit):
    return (value >> bit) & 1

def address_string_to_int(addr_str):
    # converts hex, binary, or decimal value in string to int
    if not isinstance(addr_str, str):
        print("Input not a string")
        addr = None

    if addr_str[:2] == "0x":        # hexadecimal value
        addr = int(addr_str,16)
    elif addr_str[:2] == "0b":      # binary value
        addr = int(addr_str,2)
    else:                           # decimal value
        addr = int(addr_str)

    return addr
    
class C3Surrogate:

    def __init__(self):
        self.address = None  # default current address
        self.i2c     = None  # I2C bus, instantiated after OPD enabled 
        self.output  = None  # To track the state of the output register
        self.config  = None  # To track the state of config register

        # Built in red LED, turn on
        self.led = DigitalInOut(board.D13)
        self.led.direction = Direction.OUTPUT
        self.led.value = 1

        # Set OPD Enable as output, Off by default
        self.nOPD_ENABLE = DigitalInOut(board.D3)
        self.nOPD_ENABLE.direction = Direction.OUTPUT
        self.nOPD_ENABLE.value = 1

        # OPD Fault Input with Pull-up
        self.nOPD_FAULT = DigitalInOut(board.D4)
        self.nOPD_FAULT.direction = Direction.INPUT
        self.nOPD_FAULT.pull = Pull.UP

        # OPD_ISET set as floating input
        self.OPD_ISET = DigitalInOut(board.D1)
        self.OPD_ISET.direction = Direction.INPUT

    # Helper commands to read and write to registers
    def i2c_read_reg(self, addr, reg):
        if self.i2c.try_lock():
            try:
                result = bytearray(1)
                write_buf = bytes([reg])
                self.i2c.writeto_then_readfrom(addr, write_buf, result)
                print(f"Address 0x{addr:02x} : {reg:02x} = {result:02x}")
                return result
            except Exception:
                print(f"Failed to read from i2c address 0x{self.address:02x}")
            finally:
                self.i2c.unlock()


    def i2c_write_reg(self, addr, reg, data):
        if not self.address:
            print("Device address not set")

        if self.i2c.try_lock():
            try:
                # buf = bytearray(1)
                # buf[0] = reg
                # buf.extend(data)  TODO: get extend to work
                buf = bytearray(2)
                buf[0] = reg
                buf[1] = data
                self.i2c.writeto(self.address, buf)
                print(f"Wrote 0x{buf[1]:02x} to device at 0x{self.address:02x}, register 0x{reg:02x}")
            except Exception:
                print("Failed to write to address 0x{self.address:02x}: reg=0x{reg:02x}")
            finally:
                self.i2c.unlock()

    # OPD Commands
    def opd_scan(self):
    # Loop over all possible I2C addresses and print devices found

        if self.i2c.try_lock():
            device_list = self.i2c.scan()

            self.i2c.unlock()
            if not device_list:  # check list is empty
                print("No Devices Found")
            else:
                for addr in device_list:
                    print("Found I2C device at address 0x%X" %(addr))
        
        return

    def opd_enable(self):
        self.nOPD_ENABLE.value = 0
        time.sleep(1)
        if self.nOPD_FAULT.value==1:
            if self.i2c==None:
                self.i2c = busio.I2C(board.SCL, board.SDA, frequency=100000) # Singleton
            print("OPD Enabled")
        else:
            print("ERROR: Fault when trying to enable OPD")

    def opd_disable(self):
        self.nOPD_ENABLE.value = 1
        print("OPD Disabled")

    def opd_reset(self):
        print("Resetting OPD")
        self.nOPD_ENABLE.value = 1
        time.sleep(2)
        self.nOPD_ENABLE.value = 0
        time.sleep(1)
        if self.nOPD_FAULT.value==1:
            print("OPD Reset and Enabled")
        else:
            print("ERROR: Fault when trying to reset OPD")

    def opd_status(self):
        if self.nOPD_FAULT.value == 1:
            print("OPD power OK")
        else:
            print("OPD power FAULT")

    
    def probe_i2c(self):
        # loops over all devices in opd_table and shows which are found on bus
        if self.i2c.try_lock():
            for row in opd_table:
                addr = row[1]
                found = self.i2c.probe(addr)

                print("I2C device at address 0x%X (%13s): %s" %(addr, row[0], ("FOUND" if found else "not found")))
                time.sleep(0.005)

            self.i2c.unlock()
        return
    

    
    # MAX7310 Commands
    def max_address(self, addr_str):
        # Sets device address for subsequent commands

        if addr_str is not None:
            if addr_str[:2] == "0x":        # hexadecimal value
                self.address = int(addr_str,16)
            elif addr_str[:2] == "0b":      # binary value
                self.address = int(addr_str,2)
            else:                           # decimal value
                self.address = int(addr_str)

              
        # check device found at new address
        # otherwise set to None (no address set)
        if self.i2c and self.address:
            self.i2c.try_lock()
            found = self.i2c.probe(self.address)
            self.i2c.unlock()

        if self.address is None:
            print("Address not set") 
            return
        if found:
            print("Current address is set to %s" % hex(self.address))
        else:
            print("No MAX7310 found at %s, set to None" % hex(self.address))
            self.address = None

    def max_probe(self, addr):
        if not self.i2c.try_lock():
            print("I2C bus not available")
            return
        
        try:
            found = self.i2c.probe(self.address)
        except Exception:
            print(f"Error occurred probing address 0x{addr:02x}")
        finally:
            self.i2c.unlock()

        if found:
            print(f"MAX7310 Device found at address 0x{addr:02x}")
        else:
            print(f"No MAX7310 Device found at address 0x{addr:02x}")
    
    def max_read(self, addr, register):
 
        # check register
        if register   in ['0', 'i', "input"]:
            reg_addr = MAX7310_AD_INPUT
        elif register in ['1', 'o', "output"]:
            reg_addr = MAX7310_AD_ODR
        elif register in ['2', 'p', "polarity"]:
            reg_addr = MAX7310_AD_POL
        elif register in ['3', 'c', "configuration"]:
            reg_addr = MAX7310_AD_MODE
        elif register in ['4', 't', "timeout"]:
            reg_addr = MAX7310_AD_TIMEOUT
        else:
            print(f"Not a valid register: {register}")
            return

        if not self.i2c.try_lock():
            print("I2C bus not available")
            return
                   
        try:
            result = self.i2c_read_reg(addr, reg_addr)
            print("Address %x: %x = %b" % (addr, reg_addr, result))
        except Exception:
            print(f"Failed to read from from address: {addr:02x}:{reg_addr:02x}")
        finally:  # unlock the i2c bus when ctrl-c'ing out of the loop
            self.i2c.unlock()

        return result

    def max_write(self, addr, reg, value):
        pass
        if not self.address:
            print("Device address not set")
            return

        if self.i2c.try_lock():
            try:
                buf = bytearray(1)
                buf[0] = MAX7310_AD_ODR 
                buf.extend(value)
                self.i2c.writeto(self.address, buf)
            except Exception:
                print("Failed to write to address 0x%X: reg=0x%X" % (self.address, MAX7310_AD_ODR))
            finally:
                self.i2c.unlock()


    # def opd_en_pin_mode(i2c_addr):
    #   result = bytearray(1)

    #   i2c_read_reg(i2c_addr, MAX7310_AD_MODE, result)
    #   result[0] &= ~(1 << OPD_EN)  # Set the EN pin to output mode
    #   i2c_write_reg(i2c_addr, MAX7310_AD_MODE, result)


    # def opt_print_status(i2c_addr):
    #     result = bytearray(1)
    #     print("====================")
    #     i2c_read_reg(i2c_addr, MAX7310_AD_INPUT, result)
    #     print("MAX7310_AD_INPUT = 0x%X" % result[0])

    #     i2c_read_reg(i2c_addr, MAX7310_AD_ODR, result)
    #     print("MAX7310_AD_ODR   = 0x%X" % result[0])

    #     i2c_read_reg(i2c_addr, MAX7310_AD_POL, result)
    #     print("MAX7310_AD_POL   = 0x%X" % result[0])

    #     i2c_read_reg(i2c_addr, MAX7310_AD_MODE, result)
    #     print("MAX7310_AD_MODE  = 0x%X" % result[0])

    #     return


    # def set_max7310_pin(i2c_addr, pin_num):
    # result = bytearray(1)
    # i2c_read_reg(i2c_addr, MAX7310_AD_ODR, result)
    # result[0] |= (1 << pin_num)
    # i2c_write_reg(i2c_addr, MAX7310_AD_ODR, result)
    # return


    # def clear_max7310_pin(i2c_addr, pin_num):
    # result = bytearray(1)
    # i2c_read_reg(i2c_addr, MAX7310_AD_ODR, result)
    # result[0] &= ~(1 << pin_num)
    # i2c_write_reg(i2c_addr, MAX7310_AD_ODR, result)
    # return


    # def opd_enable_disable_node(i2c_addr, enable_flag):
    #     opd_en_pin_mode(i2c_addr)
    #     if enable_flag:
    #         set_max7310_pin(i2c_addr, OPD_EN)
    #     else:
    #         clear_max7310_pin(i2c_addr, OPD_EN)
    #     return

    # Node commands
    def node(self, addr):
        self.max_address(addr)

        # Sets the direction to 0b0010 0100
        self.config = 0b00100100
        self.i2c_write_reg(addr, MAX7310_AD_MODE, self.config)

        # Sets the output to 0b0000 0000
        self.output = 0x00
        self.i2c_write_reg(addr, MAX7310_AD_ODR, MAX7310_AD_ODR)

    def on(self):
        # Sets ON/nOFF (bit 3) to high
        self.output = set_bit(self.output, 3)
        self.i2c_write_reg(self.address, MAX7310_AD_ODR, self.output)

        
        # Output: “OK” or error message

    def off(self):
        # Sets ON/nOFF (bit 3) to low
        self.output = clear_bit(self.output, 3)
        self.i2c_write_reg(self.address, MAX7310_AD_ODR, self.output)

        # Output: “OK” or error message

    def check(self):
        # Checks if nFAULT is bit is set and returns result.  No message printed

        if self.address==None:
            return
        
        #Check nFAULT (bit 2)
        value = self.i2c_read_reg(self.address, MAX7310_AD_INPUT)
        value_int = int.from_bytes(value)
        result = (value_int >> 2) & 1 == 1 # check bit 2 set

        return result

    def retry(self):
        #Write 1 to CB-RESET
        self.output = set_bit(self.output, OPD_CB_RESET)
        self.i2c_write_reg(self.address, MAX7310_AD_ODR, self.output)
        time.sleep(.500) #Wait 100 ms
        #Write 0 to CB-RESET
        self.output = clear_bit(self.output, OPD_CB_RESET)
        self.i2c_write_reg(self.address, MAX7310_AD_ODR, self.output)      

    def serialon(self):
        #Sets UART_EN (bit 7) to high, connecting C3-UART lines to the card
        self.output = set_bit(self.output, OPD_UART_EN)
        self.i2c_write_reg(self.address, MAX7310_AD_ODR, self.output)       
        #Output: “OK” or error message

    def serialoff(self):
        # Sets UART_EN (bit 7) to low, disconnected C3-UART lines from the card
        self.output = clear_bit(self.output, OPD_UART_EN)
        self.i2c_write_reg(self.address, MAX7310_AD_ODR, self.output)
        # Output: “OK” or error message

    def boothigh(self):
        # Check direction of pin 5 (input=1, output=0)
        if get_bit(self.config, OPD_BOOT0):  # check if pin 5 set as input           
            self.config = clear_bit(self.config, OPD_BOOT0) # set pin5 to output
            self.i2c_write_reg(self.address, MAX7310_AD_MODE, self.config) 
        
        #Sets BOOT0/BOOT/ISPMODE (bit 5) to high
        self.output = set_bit(self.output, OPD_BOOT0)
        self.i2c_write_reg(self.address, MAX7310_AD_ODR, self.output)
        #Output: “OK” or error message

    def bootlow(self):
        # Check direction of pin 5 (input=1, output=0)
        if get_bit(self.config, OPD_BOOT0):  # check if pin 5 set as input          
            self.config = clear_bit(self.config, OPD_BOOT0)     # set pin5 to output
            self.i2c_write_reg(self.address, MAX7310_AD_MODE, self.config)           

        # Sets BOOT0/BOOT/ISPMODE (bit 5) to low
        self.output = clear_bit(self.output, OPD_BOOT0)
        self.i2c_write_reg(self.address, MAX7310_AD_ODR, self.output) 
        # Output: “OK” or error message

    def bootrelease(self):
        # Check direction of pin 5 (input=1, output=0)
        if get_bit(self.config, OPD_BOOT0):  # check if pin 5 set as input
            return
        
        self.config = set_bit(self.config, OPD_BOOT0) # set pin5 to input
        self.i2c_write_reg(self.address, MAX7310_AD_MODE, self.config)
        