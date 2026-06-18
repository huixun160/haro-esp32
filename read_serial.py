import serial
import time

try:
    s = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
    # Read for 10 seconds
    start = time.time()
    out = b""
    while time.time() - start < 10:
        out += s.read(1024)
    print(out.decode('utf-8', 'ignore'))
except Exception as e:
    print("Error:", e)
