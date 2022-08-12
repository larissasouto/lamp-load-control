from pymodbus.client.sync import ModbusTcpClient
import subprocess
import os
import signal
import time
import sys

# server connection
server_ip_address = '127.0.0.1'
server_port = 10502

client = ModbusTcpClient(server_ip_address, server_port)

print("Info : Connection : " + str(client.connect()))

UNIT = 3

control_type_mem = client.read_coils(1, 1, unit=UNIT)
print("coil 1 value: ", control_type_mem.bits[0])

# first call
if control_type_mem.bits[0]:
    p_onoff = subprocess.Popen("python3 pset_control.py", shell=True, preexec_fn=os.setsid)
        
else:
    p_pset = subprocess.Popen("python3 onoff_control.py", shell=True, preexec_fn=os.setsid)

def main():
    global control_type_mem, p_dr, p_rtac
    
    control_type = client.read_coils(1, 1, unit=UNIT)

    if control_type.bits[0] != control_type_mem.bits[0]:
        if control_type.bits[0]:
            os.killpg(os.getpgid(p_onoff.pid), signal.SIGTERM)
            p_pset = subprocess.Popen("python3 pset_control.py", shell=True, preexec_fn=os.setsid)
                
        else:
            os.killpg(os.getpgid(p_pset.pid), signal.SIGTERM)
            p_onoff = subprocess.Popen("python3 onoff_control.py", shell=True, preexec_fn=os.setsid)
        
        control_type_mem = control_types
        

def signal_handler(sig, frame):
    print("You pressed Ctrl+C!")
    if "p_pset" in globals():
        os.killpg(os.getpgid(p_pset.pid), signal.SIGINT)
    if "p_onoff" in globals():
        os.killpg(os.getpgid(p_onoff.pid), signal.SIGINT)
        
    sys.exit(0)
        

while True:
    main()
    signal.signal(signal.SIGINT, signal_handler)
    time.sleep(5)
    
    

