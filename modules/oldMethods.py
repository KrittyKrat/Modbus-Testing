# Ignore this

def testAll(registers, sshVar):

    ssh = connectSSH(sshVar)
    totalCommands = len(registers)
    passedCommands = 0
    failedCommands = 0

    terminal.terminal("Address", "Number", "Representation", "Gotten", "Expected", "Passed", "Failed", "Total", False)

    for r in registers:

        if r.represent == "int":
            cmd = 'modbus read -w -p 502 192.168.1.1 %MW' + r.address + ' ' + r.number
        elif r.represent == "text":
            cmd = 'modbus read -D -w -p 502 192.168.1.1 %MW' + r.address + ' ' + r.number

        t = subprocess.run([cmd], capture_output=True, shell=True, text=True)
        passedCommands, failedCommands = testRegsiter(t, r, passedCommands, failedCommands, totalCommands, ssh)
        terminal.terminal(r.address, r.number, r.represent, r.gotten, r.expected, passedCommands, failedCommands, totalCommands, False)

def testRegsiter(answ, register, passedCommands, failedCommands, totalCommands, ssh):

    temp = getTempValue(register, answ)
    
    try:
        if register.represent == "int":
            register.gotten = str(getValue(register, temp))
        elif register.represent == "text":
            register.gotten = getText(register, temp)
    except:
        register.gotten = "ERROR"

    passedCommands, failedCommands = verifyExpected(register, passedCommands, failedCommands, ssh)
    return passedCommands, failedCommands

def getTempValue(register, answ):
    temp = []
    for l in answ.stdout.split():
        if register.represent == "int":
            try:
                test = int(l)
                temp.append(test)
            except Exception as e:
                continue
        elif register.represent == "text":
            try:
                test = l
                temp.append(test)
            except Exception as e:
                continue
    return temp

def getIP(temp):
    temp[0] = bin(temp[0]).replace("0b", "")
    temp[1] = bin(temp[1]).replace("0b", "")
    
    while(len(temp[0]) < 16 or len(temp[1]) < 16):
        if len(temp[0]) < 16:
            temp[0] = "0" + temp[0]
        if len(temp[1]) < 16:
            temp[1] = "0" + temp[1]

    first = slice(0, 8)
    second = slice(8, 16)
    answ = str(int(temp[0][first], 2)) + "." + str(int(temp[0][second], 2)) + "." + str(int(temp[1][first], 2)) + "." + str(int(temp[1][second], 2))
    return answ

def getText(register, temp):
    gotValue = False
    try:
        test = temp[7].split("[23][01][03][20]")[1].replace('[00]','').replace('[', '').replace(']', '')
        gotValue = True
    except:
        pass
    try:
        test = temp[7].split("[13][01][03][10]")[1].replace('[00]','').replace('[', '').replace(']', '')
        gotValue = True
    except:
        pass
    try:
        test = temp[7].split("[1b][01][03][18]")[1].replace('[00]','').replace('[', '').replace(']', '')
        gotValue = True
    except:
        pass

    if not gotValue:
        test = temp[7].replace('[00]','').replace('[', '').replace(']', '')

    test = bytes.fromhex(test).decode()
    return test

def getValue(register, temp):
    if register.address == "3":
        return getSignalStrength(temp)
    elif register.address == "5":
        return getTemperature(temp)
    elif register.address == "139" or register.address == "394":
        return getIP(temp)
    else:
        return getBytes(temp)
    
def getTemperature(temp):
    return temp[1]