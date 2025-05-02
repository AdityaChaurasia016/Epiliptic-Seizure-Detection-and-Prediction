# from flask import Flask, jsonify
# from flask_cors import CORS 
# import threading
# import time
# from services.data_collector import DataCollector
# from services.seizure_predictor import SeizurePredictor
# from config import Config

# app = Flask(__name__)
# CORS(app)
# config = Config()

# # Initialize services
# data_collector = DataCollector()
# seizure_predictor = SeizurePredictor()

# # Start serial connection
# if not data_collector.init_serial():
#     print("Failed to initialize serial connection")
#     exit(1)

# def serial_reader_thread():
#     """Background thread for reading serial data"""
#     while True:
#         data_collector.read_serial()
#         time.sleep(0.001)  # Small delay to prevent CPU overuse

# # Start the serial reader thread
# threading.Thread(target=serial_reader_thread, daemon=True).start()

# @app.route('/start', methods=['GET'])
# def start_collection():
#     success, message = data_collector.start_collection()
#     if success:
#         return jsonify({"status": "started", "message": message})
#     return jsonify({"status": "error", "message": message}), 400

# @app.route('/get_data', methods=['GET'])
# def get_data():
#     success, data = data_collector.get_data()
#     if success:
#         return jsonify({
#             "status": "success",
#             "samples": len(data),
#             "data_available": True,
#             "data": data.tolist()
#         })
#     return jsonify({
#         "status": "incomplete",
#         "samples": data_collector.buffer_index,
#         "data_available": False,
#         "message": f"{data_collector.buffer_index}/{config.BUFFER_SIZE} samples collected"
#     }), 400

# @app.route('/predict', methods=['GET'])
# def predict():
#     success, data = data_collector.get_data()
#     if not success:
#         return jsonify({
#             "status": "error",
#             "message": "Not enough data collected yet"
#         }), 400
    
#     prediction_result = seizure_predictor.predict(data)
#     if "error" in prediction_result:
#         return jsonify(prediction_result), 500
    
#     return jsonify(prediction_result)

# @app.route('/health', methods=['GET'])
# def health_check():
#     return jsonify({
#         "status": "healthy",
#         "serial_connected": data_collector.ser.is_open if data_collector.ser else False,
#         "model_loaded": seizure_predictor.loaded
#     })

# if __name__ == '__main__':
#     # Pre-load the model when starting the server
#     if not seizure_predictor.load_model():
#         print("Failed to load seizure prediction model")
#         exit(1)
    
#     app.run(debug=True, port=5000, use_reloader=False)





from flask import Flask, jsonify
from flask_cors import CORS
import threading
import time
from services.data_collector import DataCollector
from services.seizure_predictor import SeizurePredictor
from config import Config

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

config = Config()
data_collector = DataCollector()
seizure_predictor = SeizurePredictor()

# Initialize serial connection with retries
def initialize_serial(retries=3, delay=2):
    for i in range(retries):
        if data_collector.init_serial():
            return True
        time.sleep(delay)
    return False

if not initialize_serial():
    print("Failed to initialize serial connection after retries")
    exit(1)

def serial_reader_thread():
    while True:
        try:
            data_collector.read_serial()
            time.sleep(0.001)
        except Exception as e:
            print(f"Error in serial reader thread: {str(e)}")
            time.sleep(1)

threading.Thread(target=serial_reader_thread, daemon=True).start()

@app.route('/start', methods=['GET'])
def start_collection():
    try:
        success, message = data_collector.start_collection()
        if success:
            return jsonify({"status": "started", "message": message})
        return jsonify({"status": "error", "message": message}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/get_data', methods=['GET'])
def get_data():
    try:
        success, data = data_collector.get_data()
        if success:
            return jsonify({
                "status": "success",
                "samples": len(data),
                "data_available": True,
                "data": data.tolist()
            })
        return jsonify({
            "status": "incomplete",
            "samples": data_collector.buffer_index,
            "data_available": False,
            "message": f"{data_collector.buffer_index}/{config.BUFFER_SIZE} samples collected"
        }), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/predict', methods=['GET'])
def predict():
    try:
        success, data = data_collector.get_data()
        if not success:
            return jsonify({
                "status": "error",
                "message": "Not enough data collected yet"
            }), 400
        
        prediction_result = seizure_predictor.predict(data)
        if "error" in prediction_result:
            return jsonify(prediction_result), 500
        
        return jsonify(prediction_result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "serial_connected": data_collector.ser.is_open if data_collector.ser else False,
        "model_loaded": seizure_predictor.loaded
    })

if __name__ == '__main__':
    if not seizure_predictor.load_model():
        print("Failed to load seizure prediction model")
        exit(1)
    
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)