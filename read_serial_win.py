import serial
import time
import sys

print("Opening COM23 at 115200 baud...")
try:
    s = serial.Serial('COM23', 115200, timeout=1)
    # Toggle DTR/RTS to reset the board and catch the boot log from the beginning
    s.dtr = False
    s.rts = False
    time.sleep(0.1)
    s.rts = True
    time.sleep(0.1)
    
    start = time.time()
    while time.time() - start < 15:
        line = s.readline()
        if line:
            print(line.decode('utf-8', 'ignore'), end='')
    s.close()
except Exception as e:
    print("Error:", e)
