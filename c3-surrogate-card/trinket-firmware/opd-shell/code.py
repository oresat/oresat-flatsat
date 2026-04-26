
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
        # Check nOPD_FAULT
        if C3S.nOPD_ENABLE.value == 0 and not C3S.check():
            print("OPD CB is tripped.  Reset OPD, then set Node and turn on")

        # Check for text input
        value = input().strip() # get string with leading or trailing whitespace removed
        if value == "":
            continue

        # Get command (1st argument)
        arg_list = value.split()
        cmd = arg_list[0]

        if cmd not in opd.commands:  # check cmd in cmd list
            print("Unknown Command.  Type 'help' for list of commands")
            continue
        
        if len(arg_list)>4:
            print("Error: No more than 4 arguments expected")
            continue

        # Execute command
        if cmd == "help":
            opd.print_help()
            
        # OPD Commands
        elif cmd == "scan":
            C3S.opd_scan()
        elif cmd == "enable":
            C3S.opd_enable()           
        elif cmd == "disable":
            C3S.opd_disable()           
        elif cmd == "reset":
            C3S.opd_reset()           
        elif cmd == "status":
            C3S.opd_status()           

        # MAX7310 Commands
        elif cmd == "probe":
            C3S.max_probe(arg_list[1:2]) # addr
        elif cmd =="read":
            C3S.max_read(arg_list[1:3])  # addr reg
        elif cmd == "write":
            C3S.max_write(arg_list[1:4])  # addr reg value

        # Node Commands
        elif cmd == "node":
            C3S.node(arg_list[1])
        elif cmd == "on":
            C3S.on()
        elif cmd == "off":
            C3S.off()
        elif cmd == "check":
            #Output: High = “OPD CB on”,  low = “OPD CB is tripped”, or error message
            if C3S.check():
                print("OPD CB on")
            else:
                print("OPD CB is tripped")
        elif cmd == "retry":
            C3S.retry()
        elif cmd == "serialon":
            C3S.serialon()
        elif cmd == "serialoff":
            C3S.serialoff()
        elif cmd == "boothigh":
            C3S.boothigh()
        elif cmd == "bootlow":
            C3S.bootlow()
        elif cmd == "bootrelease":
            C3S.bootrelease()     
        elif cmd == "probe":
             C3S.probe_i2c()

        # Print Prompt for next input
        print("> ", end="")

    time.sleep(1)
