import serial
import time
import sys

try:
    s = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
    
    # Reset board via DTR/RTS
    s.setDTR(False)
    s.setRTS(True)
    time.sleep(0.1)
    s.setDTR(False)
    s.setRTS(False)
    
    print("Board reset. Reading for 40 seconds...")
    sys.stdout.flush()
    
    start = time.time()
    while time.time() - start < 40:
        line = s.readline()
        if line:
            print(line.decode('utf-8', 'ignore').strip())
            sys.stdout.flush()
            
except Exception as e:
    print("Error:", e)
