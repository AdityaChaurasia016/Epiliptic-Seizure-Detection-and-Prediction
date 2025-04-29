# import serial

# # Initialize serial connection
# try:
#     ser = serial.Serial("COM5", 115200, timeout=1)
#     print("Successfully connected to COM5. Reading EEG data from ESP32...")
#     print("Press Ctrl+C to stop.")
    
#     # Continuously print incoming data
#     while True:
#         line = ser.readline().decode().strip()  # Read and decode data
#         print(line)  # Print raw EEG values (e.g., "2048", "3100", etc.)
        
# except serial.SerialException as e:
#     print(f"Error opening COM5: {e}")
#     print("Fix this first:")
#     print("1. Close Arduino IDE/other serial monitors")
#     print("2. Run this script as Administrator")
#     print("3. Check if COM5 is correct in Device Manager")

# except KeyboardInterrupt:
#     print("\nStopped by user.")y
#     ser.close()  # Cleanup







from flask import Flask, jsonify
import serial
import numpy as np
import threading
import time
import atexit

app = Flask(__name__)

# --- Configuration ---
SERIAL_PORT = "COM5"
BAUD_RATE = 115200
SAMPLE_RATE_HZ = 178
BUFFER_DURATION_SEC = 1
BUFFER_SIZE = SAMPLE_RATE_HZ * BUFFER_DURATION_SEC

# --- Global Variables ---
eeg_buffer = np.zeros(BUFFER_SIZE)
buffer_index = 0
is_collecting = False
ser = None

def init_serial():
    global ser
    try:
        if ser and ser.is_open:
            ser.close()
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Allow ESP32 to initialize
        print(f"Connected to {SERIAL_PORT}")
        return True
    except serial.SerialException as e:
        print(f"Error opening {SERIAL_PORT}: {e}")
        return False

def close_serial():
    if ser and ser.is_open:
        ser.close()
        print("Serial port closed")

def read_serial():
    global buffer_index, is_collecting
    while True:
        if ser and ser.in_waiting > 0 and is_collecting:
            try:
                line = ser.readline().decode('utf-8').strip()
                eeg_buffer[buffer_index] = int(line)
                buffer_index += 1
                if buffer_index >= BUFFER_SIZE:
                    is_collecting = False
                    print("Buffer full! Ready for /get_data")
            except (ValueError, UnicodeDecodeError) as e:
                print(f"Serial read error: {e}")
                continue

# Register cleanup function
atexit.register(close_serial)

# Initialize serial
if not init_serial():
    exit(1)

# --- Flask API Endpoints ---
@app.route('/start', methods=['GET'])
def start_collection():
    global buffer_index, is_collecting
    if is_collecting:
        return jsonify({"status": "error", "message": "Already collecting!"})
    
    buffer_index = 0
    is_collecting = True
    return jsonify({
        "status": "started",
        "message": f"Collecting {BUFFER_DURATION_SEC} seconds of EEG data..."
    })

@app.route('/get_data', methods=['GET'])
def get_data():
    if not is_collecting and buffer_index == BUFFER_SIZE:
        return jsonify({
            "status": "success",
            "eeg_data": eeg_buffer.tolist(),
            "samples": buffer_index
        })
    return jsonify({
        "status": "incomplete",
        "samples": buffer_index,
        "message": f"Data not ready. {buffer_index}/{BUFFER_SIZE} samples collected."
    })

if __name__ == '__main__':
    threading.Thread(target=read_serial, daemon=True).start()
    app.run(debug=True, port=5000, use_reloader=False)