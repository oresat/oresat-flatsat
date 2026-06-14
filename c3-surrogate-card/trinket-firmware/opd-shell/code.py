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
        elif cmd == "debug":
            nArgs = len(arg_list)
            if nArgs==1:    # no argument after cmd
                opd.debug = not opd.debug # toggle value
            elif nArgs ==2:
                if arg_list[1] == 'on':
                    opd.debug = True
                elif arg_list[1] == 'off':
                    opd.debug = False
                else:
                    print("Unknown command.  Use debug | debug on | debug off")
            else:
                print("Run debug command as:  debug | debug on | debug off")
            
            if opd.debug:
                print("Debug messages on")
            else:
                print("Debug messages off")

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
            C3S.max_probe(arg_list[1]) # probe [addr]
        elif cmd == "read":
            # print help info if not right # of arguments

            C3S.max_read(arg_list[1], arg_list[2])  #  read [addr] [reg]
        elif cmd == "write":
            C3S.max_write(arg_list[1], arg_list[2], arg_list[3]) # write [addr] [reg] [value]

        # Node Commands
        elif cmd == "node":
            C3S.node(arg_list[1])
        elif cmd == "on":
            C3S.on()
        elif cmd == "off":
            C3S.off()
        elif cmd == "check":
            C3S.check()
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
        else:
            print("Command not found")  # unnessessary due to check at beginning, but just in case

        # Print Prompt for next input
        print("> ", end="")

    time.sleep(1)
