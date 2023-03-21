from modules import terminal
from modules import inUtil
from modules import test
from modules import outUtil

def main():
    args = terminal.arguments()
    routerName =  args.name.upper()
    jsonFile = args.file
    sshVar = args.ssh

    print("Router being tested: " + routerName)
    registers = inUtil.readConfigFile(routerName, jsonFile)
    test.testAll(registers, sshVar)
    outUtil.writeToCSV(registers, routerName)

if __name__ == "__main__":
    main()