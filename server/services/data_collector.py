# import numpy as np
# import serial
# import time
# from config import Config

# class DataCollector:
#     def __init__(self):
#         self.config = Config()
#         self.eeg_buffer = np.zeros(self.config.BUFFER_SIZE)
#         self.buffer_index = 0
#         self.is_collecting = False
#         self.ser = None
        
#     def init_serial(self):
#         try:
#             if self.ser and self.ser.is_open:
#                 self.ser.close()
#             self.ser = serial.Serial(
#                 self.config.SERIAL_PORT, 
#                 self.config.BAUD_RATE, 
#                 timeout=1
#             )
#             time.sleep(2)  # Allow ESP32 to initialize
#             print(f"Connected to {self.config.SERIAL_PORT}")
#             return True
#         except serial.SerialException as e:
#             print(f"Error opening {self.config.SERIAL_PORT}: {e}")
#             return False
    
#     def close_serial(self):
#         if self.ser and self.ser.is_open:
#             self.ser.close()
#             print("Serial port closed")
    
#     def start_collection(self):
#         if self.is_collecting:
#             return False, "Already collecting!"
        
#         self.buffer_index = 0
#         self.is_collecting = True
#         return True, f"Collecting {self.config.BUFFER_DURATION_SEC} seconds of EEG data..."
    
#     def read_serial(self):
#         if self.ser and self.ser.in_waiting > 0 and self.is_collecting:
#             try:
#                 line = self.ser.readline().decode('utf-8').strip()
#                 self.eeg_buffer[self.buffer_index] = int(line)
#                 self.buffer_index += 1
#                 if self.buffer_index >= self.config.BUFFER_SIZE:
#                     self.is_collecting = False
#                     print("Buffer full! Ready for prediction")
#                 return True
#             except (ValueError, UnicodeDecodeError) as e:
#                 print(f"Serial read error: {e}")
#                 return False
#         return False
    
#     def get_data(self):
#         if not self.is_collecting and self.buffer_index == self.config.BUFFER_SIZE:
#             return True, self.eeg_buffer.copy()
#         return False, None



import numpy as np
import serial
import time
from serial.serialutil import SerialException
from config import Config

class DataCollector:
    def __init__(self):
        self.config = Config()
        self.reset_buffer()
        self.is_collecting = False
        self.ser = None
        
    def reset_buffer(self):
        self.eeg_buffer = np.zeros(self.config.BUFFER_SIZE)
        self.buffer_index = 0
        
    def init_serial(self):
        try:
            if self.ser and self.ser.is_open:
                self.ser.close()
            self.ser = serial.Serial(
                self.config.SERIAL_PORT, 
                self.config.BAUD_RATE, 
                timeout=1
            )
            time.sleep(2)  # Allow ESP32 to initialize
            print(f"Connected to {self.config.SERIAL_PORT}")
            return True
        except SerialException as e:
            print(f"Error opening {self.config.SERIAL_PORT}: {e}")
            return False
    
    def close_serial(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("Serial port closed")
    
    def start_collection(self):
        if self.is_collecting:
            return False, "Already collecting!"
        
        self.reset_buffer()
        self.is_collecting = True
        return True, f"Collecting {self.config.BUFFER_DURATION_SEC} seconds of EEG data..."
    
    def read_serial(self):
        if not (self.ser and self.ser.is_open and self.is_collecting):
            return False
            
        if self.ser.in_waiting > 0:
            try:
                line = self.ser.readline().decode('utf-8').strip()
                if line:  # Only process non-empty lines
                    self.eeg_buffer[self.buffer_index] = int(line)
                    self.buffer_index += 1
                    if self.buffer_index >= self.config.BUFFER_SIZE:
                        self.is_collecting = False
                        print("Buffer full! Ready for prediction")
                    return True
            except (ValueError, UnicodeDecodeError) as e:
                print(f"Serial read error: {e}")
        return False
    
    def get_data(self):
        if not self.is_collecting and self.buffer_index == self.config.BUFFER_SIZE:
            return True, self.eeg_buffer.copy()
        return False, None