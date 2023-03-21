# Modbus register testing
#### Intro
This is a a simple python program designed to test the modbus register values and if they are correct in any router that supports modbus functionality.
#### Prerequisites
Before you begin, these are the libraries you will need to install:
```
pip install paramiko
pip install argparse
pip install pymodbus
```
Then you must connect your desired device to your computer using an ethernet cable. Navigate to it's WebUI and enable modubs in Services>Modbus>Modbus TCP Slave.
#### Program
You can run the program using:
```
python3 main.py [--name] "router name" [--file] "config file location" [--ssh] "ssh variables [--mod] "modbus variables"
```
The router name and file are mandatory arguments and must be pasted correctly. Ssh variables are optional if you decide to customize your ssh connection and want to set your own variables for the hostname, user and password. Here are a few examples of how to use the program:
```
python3 main.py --name RUTX11 --file Config/config.json --mod 192.168.1.1 502 1
python3 main.py --name RUT955 --file /home/stud/testCom.json --ssh 192.168.3.1 root admin
```
While running the program you will be able to see live results like the modbus register being tested, it's representation, result, excpected value, total number of commands to be tested, how many commands passed and failed the test.
#### Files
The command file must be a .json and it is formated like this:
```
{
  "devices": [
    {
      "router":"RUTX11",
      "registers": [
        {
          "address":"1",
          "representation": "int",
          "number":"2",
          "verify":"awk '{ print int($1) + 1 }' /proc/uptime"
        },
        {
          "address":"7",
          "representation": "text",
          "number":"16",
          "verify":"uci get system.system.hostname"
        },
      ]
    },
    {
      "router":"RUTX10",
      "registers": [
        {
          "address":"55",
          "representation": "text",
          "number":"16",
          "verify":"mnf_info -m"
        },
        {
          "address":"71",
          "representation": "text",
          "number":"16",
          "verify":"uci get system.system.routername"
        }
      ]
    }
  ]
}
```
Results are stored in the Results folder in .csv format. A new file is created for every time you launch a test.