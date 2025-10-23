from DTS6012M import DTS6012M
import time

ser = DTS6012M("/dev/serial0")
time.sleep(5)
ser.start_stream()
try:
    while True:
        time.sleep(1)
        print(ser.distance)
except KeyboardInterrupt:
    pass
ser.close()
