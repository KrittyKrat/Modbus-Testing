from modules import terminal_utility
from modules import read_file_utility
from modules import test_registers
from modules import print_file_utility

def main():
    args = terminal_utility.arguments()
    routerName =  args.name.upper()
    jsonFile = args.file
    sshVar = args.ssh
    modVar = args.mod

    print("Router being tested: " + routerName)
    registers = read_file_utility.readConfigFile(routerName, jsonFile)
    test_registers.testAll(registers, sshVar, modVar)
    print_file_utility.writeToCSV(registers, routerName)

if __name__ == "__main__":
    main()