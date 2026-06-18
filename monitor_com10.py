import serial
import time
import sys

port = 'COM10'
baud = 115200
print(f"Opening {port} at {baud} baud...")

try:
    s = serial.Serial(port, baud, timeout=0.1)
    # Toggle DTR/RTS to reset the board so we see the boot/reboot logs
    s.dtr = False
    s.rts = False
    time.sleep(0.1)
    s.rts = True
    time.sleep(0.1)
    
    print("Monitoring started. Press Ctrl+C to stop.")
    while True:
        try:
            line = s.readline()
            if line:
                # Decode line and print it
                decoded = line.decode('utf-8', errors='ignore')
                print(decoded, end='', flush=True)
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user.")
            break
        except Exception as e:
            print(f"\nRead error: {e}")
            break
    s.close()
except Exception as e:
    print(f"Failed to open port {port}: {e}")
