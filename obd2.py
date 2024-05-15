#import can as obdCan
#from can.interface import Bus
import time
import os
import binascii

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

print("""
=====================================================================
================= GlobBruh OBD-II Interfacing Tool ==================
============= https://github.com/glob-bruh/OBDIITerm ================
=====================================================================

------------- !!! USE THIS TOOL AT YOUR OWN RISK !!! ----------------
""")

while True:
    print("""
=== MAIN MENU ===
--- Initialization Tools ---
[01]: Initialize CAN (run every script start)
[02]: Initialize OS (only run this per boot)
--- General Tools ---
[10]: SEND - Sends message
[11]: READ - Repeats recieved/sent messages
[12]: TERM - Terminal mode
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

    if initChoose == "10" or initChoose == "12":
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
    elif initChoose == "11":
        print("READ MODE:")
        print("[!] You will need to press CTRL+C to exit this mode [!]")
        try:
            while True:
                print(readCANmsg(False, 0, False))
        except KeyboardInterrupt:
            pass
    elif initChoose == "02":
        print("OS config...")
        interfaceToUse = input("Interface to use (eg: ttyUSB0): ")
        os.system("sudo slcand -o -s6 -t hw -S 3000000 /dev/" + interfaceToUse + " vcan0")
        os.system("ip link set up vcan0")
        print("Done!")
    elif initChoose == "01":
        print("CAN config...")
        obdCan.rc["interface"] = "socketcan"
        obdCan.rc["channel"] = "vcan0"
        obdCan.rc["bitrate"] = 500000
        bus = Bus()
        print("Done!")
    elif initChoose == "30":
        print("[!] You will need to press CTRL+C to exit this mode [!]")
        timeinput = input("Time to wait between each SEND (ms): ")
        print("SCALE SCALE SCALE: 123#45 67 89 01 23 45 67 89")
        msgDataStr = input("Type message DATA: ")
        while True:
            time.sleep(int(timeinput) / 1000)
            sendCANmsg(msgDataStr)
            print(f"Sent -> {msgDataStr}")
    elif initChoose == "31":
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
    elif initChoose == "201":
        sendCANmsg("7DF#02 01 0C 00 00 00 00 00")
        returned = readCANmsg(True, "7e8", False)
        rpmValue = ((256 * int(returned[4], 16)) + int(returned[5], 16)) / 4
        print("The vehicles current RPM is: " + str(rpmValue))
    elif initChoose == "202":
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
    elif initChoose == "211":
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
    elif initChoose == "exit" or initChoose == "X":
        print("Shutdown bus...")
        bus.shutdown()
        print("Done exiting!")
        exit()
    else:
        print("This is not a valid selection.")