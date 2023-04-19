import paramiko
from pymodbus.client.sync import ModbusTcpClient
import pymodbus
from modules import terminal_utility

def connectModbus(modVar):
    try:
        if modVar == None:
            client = ModbusTcpClient('192.168.1.1', 502)
            id = 1
        else:
            client = ModbusTcpClient(modVar[0], modVar[1])
            id = modVar[2]
    except:
        print("Wrong modbus client variables")
        quit()
    
    client.timeout = 2
    client.connect()
    return client, id

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
        print("\nConnection to ssh lost, retrying...", end='\r')
        quit()

def verifyExpected(register, passedCommands, failedCommands, ssh):

    try:
        register.expected = executeCommand(ssh, register.verify).readline().strip()
    except:
        pass

    if register.verify == "SecretSMSMethod":
        register.expected = "@0011123456789Hello"

    if register.gotten == register.expected:
        passedCommands += 1
        register.success = "Passed"
    else:
        failedCommands += 1
        register.success = "Failed"

    if len(register.expected) == 0:
        register.expected = "----"

    return passedCommands, failedCommands

def testAll(registers, sshVar, modVar):

    client, id = connectModbus(modVar)
    ssh = connectSSH(sshVar)
    totalCommands = len(registers)
    passedCommands = 0
    failedCommands = 0

    terminal_utility.terminal("Address", "Number", "Representation", "Gotten", "Expected", "Passed", "Failed", "Total", False)

    for r in registers:
        if not client.is_socket_open():
            print("Modbus connection lost")
            quit()

        if r.verify == "SecretSMSMethod":
            thing = [0x3030, 0x3131, 0x3132, 0x3334, 0x3536, 0x3738, 0x3900, 0 ,0, 0 ,0x4865 ,0x6C6C ,0x6F]
            try:
                client.write_registers(int(r.address), thing, unit=id)
            except:
                passedCommands, failedCommands = verifyExpected(r, passedCommands, failedCommands, ssh)
                r.gotten = "----"
                terminal_utility.terminal(r.address, r.number, r.represent, r.gotten, r.expected, passedCommands, failedCommands, totalCommands, False)
                print("Failed to write to register\r")
                continue
        try:
            temp = client.read_holding_registers(int(r.address), int(r.number), unit=id)
            r.gotten = parseValue(r, temp)
        except pymodbus.exceptions.ModbusException as e:
            print("Modbus error")
            r.gotten = "----"
            pass
        except:
            r.gotten = "----"
            pass
        
        passedCommands, failedCommands = verifyExpected(r, passedCommands, failedCommands, ssh)
        terminal_utility.terminal(r.address, r.number, r.represent, r.gotten, r.expected, passedCommands, failedCommands, totalCommands, False)

    #terminal.terminal(r.address, r.number, r.represent, r.gotten, r.expected, passedCommands, failedCommands, totalCommands, False)
    ssh.close()
    client.close()

def parseValue(r, temp):
    if r.represent == "int":
        result = str(getIntValue(temp.registers, r))
    elif r.represent == "text":
        mapping =  dict.fromkeys(range(32))
        result = temp.encode().decode('utf-8').strip().translate(mapping)
        if len(result) == 0:
            result = "----"
    return result

def getIntValue(rez, register):
    if register.address == "3":
        return getSignalStrength(rez)
    elif register.address == "139" or register.address == "394":
        return getIP(rez)
    elif len(rez) == 1:
        return getIO(rez)
    else:
        return getBytes(rez)

def getIO(temp):
    return temp[0]

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
    
    while(len(temp[0]) < 16 or len(temp[1]) < 16):
        if len(temp[0]) < 16:
            temp[0] = "0" + temp[0]
        if len(temp[1]) < 16:
            temp[1] = "0" + temp[1]

    first = slice(0, 8)
    second = slice(8, 16)
    answ = str(int(temp[0][first], 2)) + "." + str(int(temp[0][second], 2)) + "." + str(int(temp[1][first], 2)) + "." + str(int(temp[1][second], 2))
    return answ