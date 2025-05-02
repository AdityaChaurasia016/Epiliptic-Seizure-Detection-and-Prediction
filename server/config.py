class Config:
    # Serial Configuration
    SERIAL_PORT = "COM7"
    BAUD_RATE = 115200
    
    # EEG Data Configuration
    SAMPLE_RATE_HZ = 178
    BUFFER_DURATION_SEC = 1
    BUFFER_SIZE = SAMPLE_RATE_HZ * BUFFER_DURATION_SEC
    
    # Model Configuration
    MODEL_PATH = "models/eeg_seizure_lstm_binary.h5"
    MEANS_PATH = "models/eeg_means.npy"
    STDS_PATH = "models/eeg_stds.npy"