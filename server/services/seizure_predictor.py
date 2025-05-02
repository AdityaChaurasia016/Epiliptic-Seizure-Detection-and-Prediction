import numpy as np
from tensorflow.keras.models import load_model
from config import Config

class SeizurePredictor:
    def __init__(self):
        self.config = Config()
        self.model = None
        self.means = None
        self.stds = None
        self.loaded = False
    
    def load_model(self):
        """Load model and scaler parameters"""
        try:
            self.model = load_model(self.config.MODEL_PATH)
            self.means = np.load(self.config.MEANS_PATH)
            self.stds = np.load(self.config.STDS_PATH)
            self.loaded = True
            return True
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            return False
    
    def predict(self, eeg_data):
        """Make prediction on EEG data"""
        if not self.loaded:
            if not self.load_model():
                return {"error": "Model failed to load"}
        
        try:
            # Convert input to numpy array if it isn't already
            eeg_array = np.array(eeg_data, dtype=np.float32)
            
            # Check input length
            if len(eeg_array) != self.config.BUFFER_SIZE:
                return {"error": f"Expected {self.config.BUFFER_SIZE} samples, got {len(eeg_array)}"}
            
            # Normalize and reshape
            normalized_input = (eeg_array - self.means) / self.stds
            reshaped_input = normalized_input.reshape(1, self.config.BUFFER_SIZE, 1)
            
            # Predict
            prediction = self.model.predict(reshaped_input)
            probability = float(prediction[0][0])
            predicted_class = int(probability > 0.5)
            
            return {
                "prediction": "seizure" if predicted_class == 1 else "non-seizure",
                "probability": probability,
                "confidence": probability if predicted_class == 1 else 1 - probability,
                "status": "success"
            }
        except Exception as e:
            return {"error": f"Prediction failed: {str(e)}", "status": "error"}