import argparse

class cl:
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def terminal(address, number, represent, gotten, expected, passedCommands, failedCommands, totalCommands, override):
    if override:
        print(f"{address:8} | {number:8} | {represent:15} | {gotten:25} | {expected:25} | {cl.OKGREEN}{passedCommands:6}{cl.ENDC} | {cl.FAIL}{failedCommands:6}{cl.ENDC} | {totalCommands:5} |", end='\r')
    else:
        print(f"{address:8} | {number:8} | {represent:15} | {gotten:25} | {expected:25} | {cl.OKGREEN}{passedCommands:6}{cl.ENDC} | {cl.FAIL}{failedCommands:6}{cl.ENDC} | {totalCommands:5} | \r")

def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', type=str, help='Name of the router', required=True)
    parser.add_argument('--file', type=str, help='Name of the config .json file', required=True)
    parser.add_argument('--ssh', type=str, help='Ssh variables (ip, username, password)', nargs=3, required=False)
    args = parser.parse_args()
    return args