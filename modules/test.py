import paramiko
import subprocess
from modules import terminal
import os
import time

#        self.address = address
#        self.number = number
#        self.represent = represent
#        self.verify = verify
#        self.gotten = ""
#        self.expected = ""
#        self.success = ""

def connectSSH(sshVar):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        if sshVar == None:
            ssh_client.connect(hostname='192.168.1.1',username='root',password='Admin123', timeout=5)
        else:
            ssh_client.connect(hostname=sshVar[0],username=sshVar[1],password=sshVar[2], timeout=5)
    except:
        print("Wrong ssh variables")
        quit()

    return ssh_client

def executeCommand(sc, command):
    try:
        stdin,stdout,stderr = sc.exec_command(command, timeout=1)
        return stdout
    except:
        print("\nConnection lost")
        quit()

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
    terminal.terminal(register.address, register.number, register.represent, register.gotten, register.expected, passedCommands, failedCommands, totalCommands, False)
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

def verifyExpected(register, passedCommands, failedCommands, ssh):

    try:
        register.expected = executeCommand(ssh, register.verify).readline().strip()
    except:
        pass

    if register.gotten == register.expected:
        passedCommands += 1
        register.success = True
    else:
        failedCommands += 1
        register.success = False

    return passedCommands, failedCommands

def getValue(register, temp):
    if register.address == "1":
        return getBytes(temp)
    elif register.address == "3":
        return getSignalStrength(temp)
    elif register.address == "5":
        return getTemperature(temp)
    elif register.address == "139" or register.address == "394":
        return getIP(temp)
    else:
        return getBytes(temp)

def getTemperature(temp):
    return temp[1]

def getSignalStrength(temp):
    bits = bin(temp[1]).replace("0b", "")
    bits = bits.replace('1', 'x')
    bits = bits.replace('0', '1')
    bits = bits.replace('x', '0')

    newBits = ""
    added = False
    for i in reversed(range(0, len(bits))):
        if added:
            newBits = bits[i] + newBits
        elif bits[i] == '0':
            added = True
            newBits = '1' + newBits
        else:
            newBits = '0' + newBits
            
    return -int(newBits, 2)

def getBytes(temp):
    return temp[0] * 65536 + temp[1]

def getIP(temp):
    temp[0] = bin(temp[0]).replace("0b", "")
    temp[1] = bin(temp[1]).replace("0b", "")

    while(len(temp[0]) < 16 and len(temp[1]) < 16):
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