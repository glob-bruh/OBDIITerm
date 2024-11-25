
#################################################
# 
# ON-BOARD DIAGNOSTICS LIBRARY
# 
# (C) GlobBruh
# https://glob-bruh.github.io/
# 
# https://github.com/glob-bruh/OBDIITerm
# 
#################################################

import time
import os
import sys
import binascii
import requests
import json
from textwrap import dedent

def printMulti(txt):
    print(dedent(txt))

def sendCANmsg(msgStringIn):
    try:
        msgDataSplit = msgStringIn.split("#")
        msgd = msgDataSplit[1].split(" ")
        msg = obdCan.Message(
            arbitration_id=int("0x" + msgDataSplit[0], 16),
            data=[
                int(msgd[0], 16), 
                int(msgd[1], 16),
                int(msgd[2], 16),
                int(msgd[3], 16),
                int(msgd[4], 16),
                int(msgd[5], 16),
                int(msgd[6], 16),
                int(msgd[7], 16)],
            is_extended_id=False
        )
    except Exception as e:
        print(f"MESSAGE GENERATION FAILURE! => {e}.")
        return False
    else:
        try:
            bus.send(msg)
            return True
        except Exception as e:
            print(f"BUS FAILURE! Have you ran option 01 from menu? ({e}.)")
            return False

def readCANmsg(arbIDneeded, arbID, advancedOut):
    try:
        recvData = bus.recv()
        if arbIDneeded == True:
            while hex(recvData.arbitration_id)[2:] != arbID:
                recvData = bus.recv()
        if advancedOut == False:
            return (hex(recvData.arbitration_id)[2:] + " " + binascii.hexlify(recvData.data, ' ').decode()).split(" ")
        elif advancedOut == True:
            return recvData
    except Exception as e:
        print(f"BUS FAILURE! Have you ran option 01 from menu? ({e}.)")
        return "?"

def vinYearDecode(num): # supported until 2040
    vinChars = ["A", "B", "C", "D", "E", "F", "G", "H", "J", "K", "L", "M", "N", "P", "R", "S", "T", "V", "W", "X", "Y", "1", "2", "3", "4", "5", "6", "7", "8","9"]
    yearCode = list(num)[9]
    y = 0
    for x in vinChars:
        if x == yearCode:
            break
        else:
            y += 1
    return [(1980 + y), (2010 + y)]

def vinCheckDigitCheck(num):
    vinCharValue = [
        ["A", "B", "C", "D", "E", "F", "G", "H", "J", "K", "L", "M", "N", "P", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "0", "1", "2", "3", "4", "5", "6", "7", "8","9"],
        [ 1,   2,   3,   4,   5,   6,   7,   8,   1,   2,   3,   4,   5,   7,   9 ,  2,   3,   4,   5,   6,   7,   8,   9,   0,   1,   2,   3,   4,   5,   6,   7,   8,  9 ]
    ]
    vinPosWeight = [8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2]
    vinArr = list(num)
    x = 0
    final = 0
    for y in vinArr:
        xa = 0
        for z in vinCharValue[0]:
            if z == vinArr[x]:
                result = vinCharValue[1][xa]
                break
            else:
                xa += 1
        final += (vinPosWeight[x] * result)
        x += 1
    checkDig = vinArr[8]
    if str(final % 11) == checkDig:
        return True
    else:
        return False

def vinNHTSAGetInfo(num):
    x = requests.get(f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{num}?format=json").text
    return json.loads(x)

def vinNHTSAFind(variable, inDict):
    for x in inDict["Results"]:
        if x["Variable"] == variable:
            return x["Value"]

def vinPrintVehicleStat(num):
    printMulti("""
    ---===---
    1 = Offline Lookup = Calculations performed locally (less info). 
    2 = Online Lookup  = Lookup VIN through NHTSA API (more info).
    ---===---
    """)
    x = int(input("Enter Choice: "))
    if x == 1:
        vehicleYear = vinYearDecode(num)
        checkStat = vinCheckDigitCheck(num)
        vinSerial = "".join(list(num)[11:17])
        printMulti(f"""
        ------------------------
        Vehicle Stats (offline):
        ------------------------
        VIN:                {num}.
        Check digit passed? {checkStat}.
        Year:               {vehicleYear[0]} or {vehicleYear[1]}.
        Serial number:      {vinSerial}.
        """)
    elif x == 2:
        apiJson = vinNHTSAGetInfo(num)
        printMulti(f"""
        -----------------------
        Vehicle Stats (online):
        -----------------------
        {apiJson["Message"]}
        -----------------------
        VIN:                {num}.
        Manufacture:        {vinNHTSAFind("Manufacturer Name", apiJson)}.
        Model:              {vinNHTSAFind("Make", apiJson)} {vinNHTSAFind("Model", apiJson)}.
        Check digit passed? {vinNHTSAFind("Error Text", apiJson)}.
        Year:               {vinNHTSAFind("Model Year", apiJson)}.
        Plant:              {vinNHTSAFind("Plant Company Name", apiJson)} > {vinNHTSAFind("Plant City", apiJson)} > {vinNHTSAFind("Plant State", apiJson)} > {vinNHTSAFind("Plant Country", apiJson)}.
        Engine Model:       {vinNHTSAFind("Engine Model", apiJson)}.
        Primary Fuel Type:  {vinNHTSAFind("Fuel Type - Primary", apiJson)}.
        Turbo:              {vinNHTSAFind("Turbo", apiJson)}.
        Body Class:         {vinNHTSAFind("Body Class", apiJson)}.
        Doors:              {vinNHTSAFind("Doors", apiJson)}.
        """)

def runMain():
    printMulti("""
    =====================================================================
    ================= GlobBruh OBD-II Interfacing Tool ==================
    ============= https://github.com/glob-bruh/OBDIITerm ================
    =====================================================================

    ------------- !!! USE THIS TOOL AT YOUR OWN RISK !!! ----------------
    """)

    while True:
        printMulti("""
        === MAIN MENU ===
        --- Initialization Tools ---
        [01]: Initialize CAN (run every script start)
        [02]: Initialize OS (only run this per boot)
        --- General Tools ---
        [10]: SEND - Sends message
        [11]: READ - Repeats received/sent messages
        [12]: TERM - Terminal mode
        [13]: VIN Lookup Tool
        --- Information Extractors ---
        [201] Get RPM (srv 01, pid 0C) - OneShot
        [202] Get RPM (srv 01, pid 0C) - Repeat
        [211] Get Fuel Tank Level (srv 01, pid 2F) - Repeat
        --- Development Tools ---
        [30]: Code Spammer
        [31]: Read to file
        --- Other ---
        [eXit]: Safely Exit
        """)
        initChoose = input("Select choice: ")

        match initChoose:
            case "01":
                print("Import CAN modules...")
                import can as obdCan
                from can.interface import Bus
                print("CAN config...")
                obdCan.rc["interface"] = "socketcan"
                obdCan.rc["channel"] = "vcan0"
                obdCan.rc["bitrate"] = 500000
                bus = Bus()
                print("Done!")
                continue
            case "02":
                print("OS config...")
                while True:
                    interfaceToUse = input("Interface to use (eg: ttyUSB0, 'find' to see USB devices): ")
                    if interfaceToUse == "find":
                        os.system("lsusb -v | grep 'Bus\|iManufacturer\|iProduct\|iSerial' | less")
                    else:
                        break
                os.system("sudo slcand -o -s6 -t hw -S 3000000 /dev/" + interfaceToUse + " vcan0")
                os.system("ip link set up vcan0")
                print("Done!")
                continue
            case "10" | "12":
                if initChoose == "10":
                    print("SEND MODE:")
                else:
                    print("TERMINAL MODE:")    
                print("Enter 'leave' to leave this mode.")
                while True:
                    msgDataStr = input("Type message DATA: ")
                    if msgDataStr == "scale":
                        print("SCALE SCALE SCALE: 123#45 67 89 01 23 45 67 89")
                    elif msgDataStr == "leave":
                        break
                    else:
                        sendStat = sendCANmsg(msgDataStr)
                        if initChoose == "12" and sendStat == True:
                            print("Returned DATA: " + str(readCANmsg(False, 0, False)))
                continue
            case "11":
                print("READ MODE:")
                print("[!] You will need to press CTRL+C to exit this mode [!]")
                try:
                    while True:
                        print(readCANmsg(False, 0, False))
                except KeyboardInterrupt:
                    pass
                continue
            case "13":
                printMulti("""
                ***********
                VIN LOOKUP:
                ***********
                Enter 'example' to use example VIN (93 Nissan 240SX, from AutoZone).
                """)
                vin = input("ENTER VIN: ").upper()
                if vin == "EXAMPLE":
                    print("Using example VIN!")
                    vin = "JN3MS37A9PW202929"
                vinPrintVehicleStat(vin)
                continue
            case "30":
                print("[!] You will need to press CTRL+C to exit this mode [!]")
                timeinput = input("Time to wait between each SEND (ms): ")
                print("SCALE SCALE SCALE: 123#45 67 89 01 23 45 67 89")
                msgDataStr = input("Type message DATA: ")
                while True:
                    time.sleep(int(timeinput) / 1000)
                    sendCANmsg(msgDataStr)
                    print(f"Sent -> {msgDataStr}")
                continue
            case "31":
                print("READ TO FILE:")
                filename = input("Enter filename: ")
                workingFile = open(filename, "a")
                print("File Opened - Autosaving...")
                print("Press CTRL+C to finish.")
                try:
                    while True:
                        returned = readCANmsg(False, 0, False)
                        print(returned)
                        curTime = time.localtime(time.time())
                        workingFile.write(f"{curTime.tm_hour}:{curTime.tm_min}:{curTime.tm_sec} => {returned}\n")
                except KeyboardInterrupt:
                    workingFile.close()
                    print("File Close - Save Successful!")
                    pass
                continue
            case "201":
                sendCANmsg("7DF#02 01 0C 00 00 00 00 00")
                returned = readCANmsg(True, "7e8", False)
                rpmValue = ((256 * int(returned[4], 16)) + int(returned[5], 16)) / 4
                print("The vehicles current RPM is: " + str(rpmValue))
                continue
            case "202":
                try:
                    print("Press CTRL+C to exit.")
                    while True:
                        sendCANmsg("7DF#02 01 0C 00 00 00 00 00")
                        returned = readCANmsg(True, "7e8", False)
                        rpmValue = ((256 * int(returned[4], 16)) + int(returned[5], 16)) / 4
                        print("                                             ", end='\r')
                        print("The vehicles current RPM is: " + str(rpmValue), end='\r')
                        time.sleep(0.35)
                except KeyboardInterrupt:
                    pass
                continue
            case "211":
                try:
                    print("Press CTRL+C to exit.")
                    while True:
                        sendCANmsg("7DF#02 01 2F 00 00 00 00 00")
                        returned = readCANmsg(True, "7e8", False)
                        rpmValue = (100 * 255) / int(returned[4], 16)
                        print("                                                 ", end='\r')
                        print("The vehicles Fuel Tank Level is: " + str(rpmValue), end='\r')
                        time.sleep(0.35)
                except KeyboardInterrupt:
                    pass
                continue
            case "exit" | "X":
                print("Shutdown bus...")
                bus.shutdown()
                print("Done exiting!")
                exit()
                continue
            case _:
                print("This is not a valid selection.")

if __name__ == "__main__":
    runMain()