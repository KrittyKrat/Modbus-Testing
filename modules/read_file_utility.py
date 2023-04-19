import json
from modules.register_class import Register

def openJson(jsonFile):
    try:
        file = open(jsonFile)
        data = json.load(file)
    except:
        print("Failed to open the command file")
        quit()

    return file, data

def readConfigFile(routerName, jsonFile):

    file, data = openJson(jsonFile)
    registers = []
    connected = False

    try:
        for d in data['devices']:
            if d['router'] == routerName:
                for c in d['registers']:
                    registers.append(Register(c['address'], c['number'], c['representation'], c['verify']))
                connected = True
    except:
        print("Bad json format")
        quit()
        
    if not connected:
        print("No specified device found")
        quit()

    file.close()
    return registers