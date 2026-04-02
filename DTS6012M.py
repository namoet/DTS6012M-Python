import serial
import threading
import time

START_CMD = b"\x01"
STOP_CMD = b"\x02"

def calc_crc16(data: bytes) -> int:
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc

def parse_numbers(data: bytes, num_len, byteorder) -> list:
    nums = []
    for index in range(0, len(data), num_len):
        binary = data[index : index+num_len]
        nums.append(int.from_bytes(binary, byteorder))
    return nums


class DTS6012M:
    def __init__(self, port, baudrate=921600, check_crc=True, data_event=None):
        self.port = port
        self.baudrate = baudrate
        self.ser = serial.Serial(port=port, baudrate=baudrate)
        self.streaming = False
        self.check_crc = check_crc
        self.data_event = data_event
        self.listener_thread = None
        self.sec_distance = None
        self.sec_correction = None
        self.sec_intensity = None
        self.distance = None
        self.correction = None
        self.intensity = None
        self.sunlight_base = None

    def send(self, cmd, data, baotou=b"\xA5", device_number=b"\x03", device_type=b"\x20"):
        send_data = baotou + device_number + device_type + cmd + b"\x00" + len(data).to_bytes(2, "big") + data
        crc = calc_crc16(send_data)
        send_data += crc.to_bytes(2, "little")
        self.ser.write(send_data)
        self.ser.flush()

    def recv(self):
        frame = self.ser.read(7)
        length = int.from_bytes(frame[-2:], "big")
        frame += self.ser.read(length+2)
        if self.check_crc:
            comp = calc_crc16(frame[:-2])
            if comp.to_bytes(2, "big") != frame[-2:]:
                return None
        header = frame[0:1]
        dev_num = frame[1:2]
        dev_type = frame[2:3]
        cmd = frame[3:4]
        _ = frame[4:5]
        data = frame[7:7+length]
        return dev_num, dev_type, cmd, data
    
    def listener(self):
        while True:
            resp = self.recv()
            if not resp:
                continue
            dev_num, dev_type, cmd, data = resp
            if cmd == STOP_CMD:
                if data[0] == 0:
                    self.streaming = False
                    return
            elif cmd == START_CMD:
                self.streaming = True
                if len(data) != 14:
                    continue
                nums = parse_numbers(data, 2, "little")
                if self.data_event:
                    func = self.data_event
                    func(self)
                self.sec_distance, self.sec_correction, self.sec_intensity, self.distance, self.correction, self.intensity, self.sunlight_base = nums
    
    def start_stream(self, timeout=3):
        self.send(START_CMD, b"")
        self.listener_thread = threading.Thread(target=self.listener)
        self.listener_thread.start()
        start = time.time()
        while not self.streaming:
            if time.time()-start > timeout:
                raise TimeoutError("Timed out while waiting for stream start response!")

    def stop_stream(self, timeout=3):
        self.send(STOP_CMD, b"")
        start = time.time()
        while self.streaming:
            if time.time()-start > timeout:
                raise TimeoutError("Timed out while waiting for stream stop response!")
            
    
    def close(self):
        if self.streaming:
            self.stop_stream()
        self.ser.close()
