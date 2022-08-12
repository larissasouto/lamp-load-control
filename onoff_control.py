from pymodbus.client.sync import ModbusTcpClient
import gpiozero
import time
from operator import itemgetter
import numpy as np

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

# initial states Load 1
prevRTAC_C1 = 0
nextRTAC_C1 = 0
prevManual_S1 = 0
nextManual_S1 = 0
prevFlipFlop_L1 = 0
nextFlipFlop_L1 = 0

# initial states Load 2
prevRTAC_C2 = 0
nextRTAC_C2 = 0
prevManual_S2 = 0
nextManual_S2 = 0
prevFlipFlop_L2 = 0
nextFlipFlop_L2 = 0

# initial states Load 3
prevRTAC_C3 = 0
nextRTAC_C3 = 0
prevManual_S3 = 0
nextManual_S3 = 0
prevFlipFlop_L3 = 0
nextFlipFlop_L3 = 0

# initial states Load 4
prevRTAC_C4 = 0
nextRTAC_C4 = 0
prevManual_S4 = 0
nextManual_S4 = 0
prevFlipFlop_L4 = 0
nextFlipFlop_L4 = 0

# initial states Load 5
prevRTAC_C5 = 0
nextRTAC_C5 = 0
prevManual_S5 = 0
nextManual_S5 = 0
prevFlipFlop_L5 = 0
nextFlipFlop_L5 = 0

# initial states Load 6
prevRTAC_C6 = 0
nextRTAC_C6 = 0
prevManual_S6 = 0
nextManual_S6 = 0
prevFlipFlop_L6 = 0
nextFlipFlop_L6 = 0

# initial states Load 7
prevRTAC_C7 = 0
nextRTAC_C7 = 0
prevManual_S7 = 0
nextManual_S7 = 0
prevFlipFlop_L7 = 0
nextFlipFlop_L7 = 0

# initial Loads states
status = client.read_coils(9, 15, unit=UNIT)
memCMD = [status.bits[0], status.bits[1], status.bits[2], status.bits[3],
          status.bits[4], status.bits[5], status.bits[6]]
# default priority array
Ysort = [0.875, 0.75, 0.625, 0.5, 0.375, 0.25, 0.125]

memYGr = [0.875, 0.75, 0.625, 0.5, 0.375, 0.25, 0.125]

def risingEdgeDetector(prevState, nextState):
    if prevState < nextState:
        return 1
    return 0


def fallingEdgeDetector(prevState, nextState):
    if prevState > nextState:
        return 1
    return 0


def srFlipFlop(s, r, prevFlipFlop, nextFlipFlop):
    # SR flip-flop truth table implementation
    if s == 0 and r == 0:
        nextFlipFlop = prevFlipFlop
    elif s == 0 and r == 1:
        nextFlipFlop = 0
    elif s == 1 and r == 0:
        nextFlipFlop = 1
    else:
        nextFlipFlop = prevFlipFlop

    return nextFlipFlop


def orLogic(RTAC, manual):
    if RTAC == 0 and manual == 1:
        return 1
    if RTAC == 1 and manual == 0:
        return 1
    return 0


""" RTAC control mode """


def rtac_mode(values, load):
    # initial states Load 1
    global prevRTAC_C1, nextRTAC_C1, prevManual_S1, nextManual_S1

    # initial states Load 2
    global prevRTAC_C2, nextRTAC_C2, prevManual_S2, nextManual_S2

    # initial states Load 3
    global prevRTAC_C3, nextRTAC_C3, prevManual_S3, nextManual_S3

    # initial states Load 4
    global prevRTAC_C4, nextRTAC_C4, prevManual_S4, nextManual_S4

    # initial states Load 5
    global prevRTAC_C5, nextRTAC_C5, prevManual_S5, nextManual_S5

    # initial states Load 6
    global prevRTAC_C6, nextRTAC_C6, prevManual_S6, nextManual_S6

    # initial states Load 7
    global prevRTAC_C7, nextRTAC_C7, prevManual_S7, nextManual_S7

    # manual commands
    manual = client.read_coils(16, 22, unit=UNIT)

    if load == 1:
        prevRTAC_C1 = nextRTAC_C1
        nextRTAC_C1 = values.bits[0]  # coil 2 - S1 cmd

        prevManual_S1 = nextManual_S1
        nextManual_S1 = manual.bits[0]  # coil 16 - S1 manual cmd

        risingEdgeRTAC = risingEdgeDetector(prevRTAC_C1, nextRTAC_C1)
        risingEdgeManual = risingEdgeDetector(prevManual_S1, nextManual_S1)

        fallingEdgeRTAC = fallingEdgeDetector(prevRTAC_C1, nextRTAC_C1)
        fallingEdgeManual = fallingEdgeDetector(prevManual_S1, nextManual_S1)

        # OR Logic
        s = orLogic(risingEdgeRTAC, risingEdgeManual)
        r = orLogic(fallingEdgeRTAC, fallingEdgeManual)

        global prevFlipFlop_L1, nextFlipFlop_L1
        prevFlipFlop_L1 = nextFlipFlop_L1

        loadState = srFlipFlop(s, r, prevFlipFlop_L1, nextFlipFlop_L1)
        nextFlipFlop_L1 = loadState

        if loadState == 0:
            relay1.on()  # load OFF
        else:
            relay1.off()  # load ON

        client.write_coil(9, loadState, unit=UNIT)
        return loadState

    if load == 2:
        prevRTAC_C2 = nextRTAC_C2
        nextRTAC_C2 = values.bits[1]  # coil 3 - S2 cmd

        prevManual_S2 = nextManual_S2
        nextManual_S2 = manual.bits[1]  # coil 17 - S2 manual cmd

        risingEdgeRTAC = risingEdgeDetector(prevRTAC_C2, nextRTAC_C2)
        risingEdgeManual = risingEdgeDetector(prevManual_S2, nextManual_S2)

        fallingEdgeRTAC = fallingEdgeDetector(prevRTAC_C2, nextRTAC_C2)
        fallingEdgeManual = fallingEdgeDetector(prevManual_S2, nextManual_S2)

        # OR Logic
        s = orLogic(risingEdgeRTAC, risingEdgeManual)
        r = orLogic(fallingEdgeRTAC, fallingEdgeManual)

        global prevFlipFlop_L2, nextFlipFlop_L2
        prevFlipFlop_L2 = nextFlipFlop_L2

        loadState = srFlipFlop(s, r, prevFlipFlop_L2, nextFlipFlop_L2)
        nextFlipFlop_L2 = loadState

        if loadState == 0:
            relay2.on()  # load OFF
        else:
            relay2.off()  # load ON

        client.write_coil(10, loadState, unit=UNIT)
        return loadState

    if load == 3:
        prevRTAC_C3 = nextRTAC_C3
        nextRTAC_C3 = values.bits[2]  # coil 4 - S3 cmd

        prevManual_S3 = nextManual_S3
        nextManual_S3 = manual.bits[2]  # coil 18 - S3 manual cmd

        risingEdgeRTAC = risingEdgeDetector(prevRTAC_C3, nextRTAC_C3)
        risingEdgeManual = risingEdgeDetector(prevManual_S3, nextManual_S3)

        fallingEdgeRTAC = fallingEdgeDetector(prevRTAC_C3, nextRTAC_C3)
        fallingEdgeManual = fallingEdgeDetector(prevManual_S3, nextManual_S3)

        # OR Logic
        s = orLogic(risingEdgeRTAC, risingEdgeManual)
        r = orLogic(fallingEdgeRTAC, fallingEdgeManual)

        global prevFlipFlop_L3, nextFlipFlop_L3
        prevFlipFlop_L3 = nextFlipFlop_L3

        loadState = srFlipFlop(s, r, prevFlipFlop_L3, nextFlipFlop_L3)
        nextFlipFlop_L3 = loadState

        if loadState == 0:
            relay3.on()  # load OFF
        else:
            relay3.off()  # load ON

        client.write_coil(11, loadState, unit=UNIT)
        return loadState

    if load == 4:
        prevRTAC_C4 = nextRTAC_C4
        nextRTAC_C4 = values.bits[3]  # coil 5 - S4 cmd

        prevManual_S4 = nextManual_S4
        nextManual_S4 = manual.bits[3]  # coil 19 - S4 manual cmd

        risingEdgeRTAC = risingEdgeDetector(prevRTAC_C4, nextRTAC_C4)
        risingEdgeManual = risingEdgeDetector(prevManual_S4, nextManual_S4)

        fallingEdgeRTAC = fallingEdgeDetector(prevRTAC_C4, nextRTAC_C4)
        fallingEdgeManual = fallingEdgeDetector(prevManual_S4, nextManual_S4)

        # OR Logic
        s = orLogic(risingEdgeRTAC, risingEdgeManual)
        r = orLogic(fallingEdgeRTAC, fallingEdgeManual)

        global prevFlipFlop_L4, nextFlipFlop_L4
        prevFlipFlop_L4 = nextFlipFlop_L4

        loadState = srFlipFlop(s, r, prevFlipFlop_L4, nextFlipFlop_L4)
        nextFlipFlop_L4 = loadState

        if loadState == 0:
            relay4.on()  # load OFF
        else:
            relay4.off()  # load ON

        client.write_coil(12, loadState, unit=UNIT)
        return loadState

    if load == 5:
        prevRTAC_C5 = nextRTAC_C5
        nextRTAC_C5 = values.bits[4]  # coil 6 - S5 cmd

        prevManual_S5 = nextManual_S5
        nextManual_S5 = manual.bits[4]  # coil 20 - S5 manual cmd

        risingEdgeRTAC = risingEdgeDetector(prevRTAC_C5, nextRTAC_C5)
        risingEdgeManual = risingEdgeDetector(prevManual_S5, nextManual_S5)

        fallingEdgeRTAC = fallingEdgeDetector(prevRTAC_C5, nextRTAC_C5)
        fallingEdgeManual = fallingEdgeDetector(prevManual_S5, nextManual_S5)

        # OR Logic
        s = orLogic(risingEdgeRTAC, risingEdgeManual)
        r = orLogic(fallingEdgeRTAC, fallingEdgeManual)

        global prevFlipFlop_L5, nextFlipFlop_L5
        prevFlipFlop_L5 = nextFlipFlop_L5

        loadState = srFlipFlop(s, r, prevFlipFlop_L5, nextFlipFlop_L5)
        nextFlipFlop_L5 = loadState

        if loadState == 0:
            relay5.on()  # load OFF
        else:
            relay5.off()  # load ON

        client.write_coil(13, loadState, unit=UNIT)
        return loadState

    if load == 6:
        prevRTAC_C6 = nextRTAC_C6
        nextRTAC_C6 = values.bits[5]  # coil 7 - S6 cmd

        prevManual_S6 = nextManual_S6
        nextManual_S6 = manual.bits[5]  # coil 21 - S6 manual cmd

        risingEdgeRTAC = risingEdgeDetector(prevRTAC_C6, nextRTAC_C6)
        risingEdgeManual = risingEdgeDetector(prevManual_S6, nextManual_S6)

        fallingEdgeRTAC = fallingEdgeDetector(prevRTAC_C6, nextRTAC_C6)
        fallingEdgeManual = fallingEdgeDetector(prevManual_S6, nextManual_S6)

        # OR Logic
        s = orLogic(risingEdgeRTAC, risingEdgeManual)
        r = orLogic(fallingEdgeRTAC, fallingEdgeManual)

        global prevFlipFlop_L6, nextFlipFlop_L6
        prevFlipFlop_L6 = nextFlipFlop_L6

        loadState = srFlipFlop(s, r, prevFlipFlop_L6, nextFlipFlop_L6)
        nextFlipFlop_L6 = loadState

        if loadState == 0:
            relay6.on()  # load OFF
        else:
            relay6.off()  # load ON

        client.write_coil(14, loadState, unit=UNIT)
        return loadState

    if load == 7:
        prevRTAC_C7 = nextRTAC_C7
        nextRTAC_C7 = values.bits[6]  # coil 8 - S7 cmd

        prevManual_S7 = nextManual_S7
        nextManual_S7 = manual.bits[6]  # coil 22 - S7 manual cmd

        risingEdgeRTAC = risingEdgeDetector(prevRTAC_C7, nextRTAC_C7)
        risingEdgeManual = risingEdgeDetector(prevManual_S7, nextManual_S7)

        fallingEdgeRTAC = fallingEdgeDetector(prevRTAC_C7, nextRTAC_C7)
        fallingEdgeManual = fallingEdgeDetector(prevManual_S7, nextManual_S7)

        # OR Logic
        s = orLogic(risingEdgeRTAC, risingEdgeManual)
        r = orLogic(fallingEdgeRTAC, fallingEdgeManual)

        global prevFlipFlop_L7, nextFlipFlop_L7
        prevFlipFlop_L7 = nextFlipFlop_L7

        loadState = srFlipFlop(s, r, prevFlipFlop_L7, nextFlipFlop_L7)
        nextFlipFlop_L7 = loadState

        if loadState == 0:
            relay7.on()  # load OFF
        else:
            relay7.off()  # load ON

        client.write_coil(15, loadState, unit=UNIT)
        return loadState


# LOGIC FUNCTIONS
def manual_command(values):
    # Load 1 - manual CMD
    load_1_State = values.bits[0]
    if load_1_State:  # True
        relay1.off()  # load ON
    else:
        relay1.on()  # load OFF

    client.write_coil(9, load_1_State, unit=UNIT)

    # Load 2 - manual CMD
    load_2_State = values.bits[1]
    if load_2_State:  # True
        relay2.off()  # load ON
    else:
        relay2.on()  # load OFF

    client.write_coil(10, load_2_State, unit=UNIT)

    # Load 3 - manual CMD
    load_3_State = values.bits[2]
    if load_3_State:  # True
        relay3.off()  # load ON
    else:
        relay3.on()  # load OFF

    client.write_coil(11, load_3_State, unit=UNIT)

    # Load 4 - manual CMD
    load_4_State = values.bits[3]
    if load_4_State:  # True
        relay4.off()  # load ON
    else:
        relay4.on()  # load OFF

    client.write_coil(12, load_4_State, unit=UNIT)

    # Load 5 - manual CMD
    load_5_State = values.bits[4]
    if load_5_State:  # True
        relay5.off()  # load ON
    else:
        relay5.on()  # load OFF

    client.write_coil(13, load_5_State, unit=UNIT)

    # Load 6 - manual CMD
    load_6_State = values.bits[5]
    if load_6_State:  # True
        relay6.off()  # load ON
    else:
        relay6.on()  # load OFF

    client.write_coil(14, load_6_State, unit=UNIT)

    # Load 7 - manual CMD
    load_7_State = values.bits[6]
    if load_7_State:  # True
        relay7.off()  # load ON
    else:
        relay7.on()  # load OFF

    client.write_coil(15, load_7_State, unit=UNIT)


def calculate_priority(values):
    global memCMD, memYGr
    ord = [1, 2, 3, 4, 5, 6, 7]
    endCMD = [values.bits[0], values.bits[1], values.bits[2], values.bits[3],
              values.bits[4], values.bits[5], values.bits[6]]
    
    print(values.bits)

    aux = np.array([ord, memCMD, memYGr, endCMD, memYGr])
    aux = np.transpose(aux)

    aux = sorted(aux, key=itemgetter(2), reverse=True)
    aux = sorted(aux, key=itemgetter(1))
    aux = sorted(aux, key=itemgetter(3), reverse=True)

    aux = np.transpose(aux)

    for i in range(0, 6):
        aux[4:i] = Ysort

    aux = np.transpose(aux)

    aux = sorted(aux, key=itemgetter(0))
    aux = np.transpose(aux)

    YGr = aux[4]
    print(YGr)
    
    client.write_register(1, int(YGr[0]*1000), unit=UNIT)
    client.write_register(2, int(YGr[1]*1000), unit=UNIT)
    client.write_register(3, int(YGr[2]*1000), unit=UNIT)
    client.write_register(4, int(YGr[3]*1000), unit=UNIT)
    client.write_register(5, int(YGr[4]*1000), unit=UNIT)
    client.write_register(6, int(YGr[5]*1000), unit=UNIT)
    client.write_register(7, int(YGr[6]*1000), unit=UNIT)

    memCMD = endCMD
    memYGr = YGr

    time.sleep(10)
    return YGr


def power_calculation(value, ranking):
    pset_power = value.registers[0]

    state = client.read_coils(9, 16, unit=UNIT)

    # each load group has 828 Watts
    actual_state = [state.bits[0], state.bits[1], state.bits[2], state.bits[3],
                    state.bits[4], state.bits[5], state.bits[6]]
    power_consumption = actual_state.count(True) * 828
    print(actual_state)

    base_value = 0.125
    aux = 0

    while pset_power < power_consumption:
        _ranking = np.where(ranking == base_value + aux)
        minor_priority = _ranking[0]

        if actual_state[minor_priority[0]]:
            load_manual_coil = minor_priority[0] + 16
            print("switch: ", minor_priority[0] + 1)
            load_state_coil = minor_priority[0] + 9

            relay = "relay" + str(minor_priority[0] + 1)
            if relay == "relay1":
                relay1.on()  # load OFF
            if relay == "relay2":
                relay2.on()  # load OFF
            if relay == "relay3":
                relay3.on()  # load OFF
            if relay == "relay4":
                relay4.on()  # load OFF
            if relay == "relay5":
                relay5.on()  # load OFF
            if relay == "relay6":
                relay6.on()  # load OFF
            if relay == "relay7":
                relay7.on()  # load OFF

            client.write_coil(load_state_coil, 0, unit=UNIT)
            client.write_coil(load_manual_coil, 0, unit=UNIT)
            time.sleep(10)

            # each load group has 828 Watts
            state = client.read_coils(9, 16, unit=UNIT)
            actual_state = [state.bits[0], state.bits[1], state.bits[2], state.bits[3],
                            state.bits[4], state.bits[5], state.bits[6]]
            power_consumption = actual_state.count(True) * 828
            print("power consumption: ", power_consumption)

        else:
            aux += base_value


def getValuesRanking():
    # manual commands
    manual = client.read_coils(16, 22, unit=UNIT)
    
    manual_command(manual)

    ranking = calculate_priority(manual)

    power_value = client.read_holding_registers(0, 1, unit=UNIT)

    power_calculation(power_value, ranking)

    time.sleep(5)  # wait 5 seconds
    
def getValuesRTAC():
    print("RTAC CONTROL MODE")
    values = client.read_coils(2, 9, unit=UNIT)
    #  Load 1
    loadState = rtac_mode(values, 1)
    if loadState == 0:
        print("SWITCH 1: OFF")
    else:
        print("SWITCH 1 = ON")
    #  Load 2
    loadState = rtac_mode(values, 2)
    if loadState == 0:
        print("SWITCH 2: OFF")
    else:
        print("SWITCH 2 = ON")
    #  Load 3
    loadState = rtac_mode(values, 3)
    if loadState == 0:
        print("SWITCH 3: OFF")
    else:
        print("SWITCH 3 = ON")
    #  Load 4
    loadState = rtac_mode(values, 4)
    if loadState == 0:
        print("SWITCH 4: OFF")
    else:
        print("SWITCH 4 = ON")
    #  Load 5
    loadState = rtac_mode(values, 5)
    if loadState == 0:
        print("SWITCH 5: OFF")
    else:
        print("SWITCH 5 = ON")
    #  Load 6
    loadState = rtac_mode(values, 6)
    if loadState == 0:
        print("SWITCH 6: OFF")
    else:
        print("SWITCH 6 = ON")
    #  Load 7
    loadState = rtac_mode(values, 7)
    if loadState == 0:
        print("SWITCH 7: OFF")
    else:
        print("SWITCH 7 : ON")
        
    time.sleep(5)

def checkControlType():
    control_mode = client.read_coils(0, 1, unit=UNIT)
    print("coil 0: ", control_mode.bits[0])
    
    if control_mode.bits[0]:
        getValuesRanking()
    
    else:
        getValuesRTAC()


while True:
    checkControlType()
