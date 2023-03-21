from datetime import datetime
import csv

def writeToCSV(registers, routerName):
    tempName = routerName + "_" + datetime.now().strftime('%Y-%m-%d_%H:%M:%S') + ".csv"
    fileName = "Results/" + tempName
    #fileName = "Results/test.csv"
    
    try:
        file = open(fileName, 'w')
        writer = csv.writer(file)
    except:
        print("Failed to open file")
        quit()
    
    try:
        writer.writerow(["Register", "Representation", "Gotten", "Expected", "Pass"])

        for i in range(0, len(registers)):
            writer.writerow([registers[i].address, registers[i].represent, registers[i].gotten, registers[i].expected, registers[i].success])
    except:
        print("Failed to write to .csv file")
        quit()
    
    file.close()
    return tempName