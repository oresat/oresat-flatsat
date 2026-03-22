
import supervisor
import time
import opd


######################### MAIN ##############################

# Setup
C3S = opd.C3Surrogate()


# Start OPD Shell
print()
print("OPD Shell")
print("!! DISCONNECT (OR HOLD IN RESET) ANY C3 ON THE BUS BEFORE TURNING ON THE C3S OPD !!")
print("Type 'help' for commands")
print("> ", end="")

while True:
    C3S.led.value = not C3S.led.value

    if supervisor.runtime.serial_bytes_available:
        value = input().strip() # get string with leading or trailing whitespace removed
        if value == "":
            continue

        arg_list = value.split()
        cmd = arg_list[0]
        arg = None

        if len(arg_list)==2:
            arg = arg_list[1]
        elif len(arg_list)>2:
            print("Error: only 1 or 2 arguments expected")
            continue

        handled_command = False

        if cmd == "help":
            opd.print_help()
            handled_command = True
        # OPD Commands
        elif cmd == "scan":
            C3S.opd_scan()
            handled_command = True
        elif cmd == "enable":
            C3S.opd_enable()
            handled_command = True
        elif cmd == "disable":
            C3S.opd_disable()
            handled_command = True
        elif cmd == "reset":
            C3S.opd_reset()
            handled_command = True
        elif cmd == "status":
            C3S.opd_status()
            handled_command = True

        # MAX7310 Commands
        elif cmd == "address":
            C3S.max_address(arg)
            handled_command = True
        elif cmd == "direction":
            handled_command = True
        elif cmd == "write":
            handled_command = True
        elif cmd =="read":
            #max_read(i2c, address)
            handled_command = True

        # Node Commands
        elif cmd == "node":
            C3S.node(arg)
            handled_command = True
        elif cmd == "on":
            C3S.on()
            handled_command = True
        elif cmd == "off":
            C3S.off()
            handled_command = True
        elif cmd == "check":
            C3S.check()
            handled_command = True
        elif cmd == "retry":
            C3S.retry()
            handled_command = True
        elif cmd == "serialon":
            C3S.serialon()
            handled_command = True
        elif cmd == "serialoff":
            C3S.serialoff()
            handled_command = True
        # elif cmd == "bus":
        #     i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
        #     print("I2C bus turned on")
        #     handled_command = True
        elif cmd == "probe":
            C3S.probe_i2c()
            handled_command = True

        if not handled_command:
            print("Unknown command")

        print("> ", end="")

    time.sleep(1)
