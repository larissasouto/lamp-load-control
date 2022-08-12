from pymodbus.client.sync import ModbusTcpClient
import gpiozero
import time

# server connection
server_ip_address = '127.0.0.1'
server_port = 10502

client = ModbusTcpClient(server_ip_address, server_port)

print("[+]Info : Connection : " + str(client.connect()))

UNIT = 2

""" 
Rpi pin definition
PIN | GPIO
29     5
31     6
33     13
36     16
35     19
38     20
40     21
"""

relay1 = gpiozero.OutputDevice(5, initial_value=True)
relay2 = gpiozero.OutputDevice(6, initial_value=True)
relay3 = gpiozero.OutputDevice(13, initial_value=True)
relay4 = gpiozero.OutputDevice(16, initial_value=True)
relay5 = gpiozero.OutputDevice(19, initial_value=True)
relay6 = gpiozero.OutputDevice(20, initial_value=True)
relay7 = gpiozero.OutputDevice(21, initial_value=True)

# LOGIC FUNCTIONS
""" Pset control mode """

def pset_mode(value):
    print("PSET CONTROL MODE")
    pset_power = value.registers[0]

    if pset_power < 828:
        relay1.on() # inverted logic
        relay2.on()
        relay3.on()
        relay4.on()
        relay5.on()
        relay6.on()
        relay7.on()

        client.write_coils(9, [0] * 7, unit=UNIT)  

    if (pset_power >= 828) and (pset_power < 1656):
        relay1.off()
        relay2.on()
        relay3.on()
        relay4.on()
        relay5.on()
        relay6.on()
        relay7.on()

        client.write_coil(9, 1, unit=UNIT) 
        client.write_coils(10, [0] * 6, unit=UNIT)  

    if (pset_power >= 1656) and (pset_power < 2484):
        relay1.off()
        relay2.off()
        relay3.on()
        relay4.on()
        relay5.on()
        relay6.on()
        relay7.on()

        client.write_coils(9, [1] * 2, unit=UNIT)  
        client.write_coils(11, [0] * 5, unit=UNIT)  

    if (pset_power >= 2484) and (pset_power < 3312):
        relay1.off()
        relay2.off()
        relay3.off()
        relay4.on()
        relay5.on()
        relay6.on()
        relay7.on()

        client.write_coils(9, [1] * 3, unit=UNIT)  
        client.write_coils(12, [0] * 4, unit=UNIT) 

    if (pset_power >= 3312) and (pset_power < 4140):
        relay1.off()
        relay2.off()
        relay3.off()
        relay4.off()
        relay5.on()
        relay6.on()
        relay7.on()

        client.write_coils(9, [1] * 4, unit=UNIT) 
        client.write_coils(13, [0] * 3, unit=UNIT)  

    if (pset_power >= 4140) and (pset_power < 4968):
        relay1.off()
        relay2.off()
        relay3.off()
        relay4.off()
        relay5.off()
        relay6.on()
        relay7.on()

        client.write_coils(9, [1] * 5, unit=UNIT)  
        client.write_coils(14, [0] * 2, unit=UNIT)  

    if (pset_power >= 4968) and (pset_power < 5796):
        relay1.off()
        relay2.off()
        relay3.off()
        relay4.off()
        relay5.off()
        relay6.off()
        relay7.on()

        client.write_coils(9, [1] * 6, unit=UNIT)  
        client.write_coil(15, 0, unit=UNIT)  

    if pset_power >= 5796:
        relay1.off()
        relay2.off()
        relay3.off()
        relay4.off()
        relay5.off()
        relay6.off()
        relay7.off()

        client.write_coils(9, [1] * 7, unit=UNIT)  

    print(f'S1 {relay1.value}\nS2 {relay2.value}\nS3 {relay3.value}\nS4 {relay4.value}\nS5 {relay5.value}\nS6 {relay6.value}\nS7 {relay7.value}\n')


def getValues():
    power_value = client.read_holding_registers(0, 1, unit=UNIT)
    pset_mode(power_value)
    time.sleep(5)  # wait 5 seconds


while True:
    getValues()