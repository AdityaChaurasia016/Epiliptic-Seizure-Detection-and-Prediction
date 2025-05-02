export default function PredictionPanel({ prediction }) {
    return (
      <div className={`prediction-panel ${prediction.prediction}`}>
        <h2>Seizure Prediction</h2>
        <p className="prediction-result">
          Status: <strong>{prediction.prediction}</strong>
        </p>
        <p>Probability: {(prediction.probability * 100).toFixed(2)}%</p>
        <p>Confidence: {(prediction.confidence * 100).toFixed(2)}%</p>
        
        <div className="confidence-meter">
          <div 
            className="confidence-bar" 
            style={{ 
              width: `${prediction.confidence * 100}%`,
              backgroundColor: prediction.prediction === 'seizure' ? '#ff4d4f' : '#52c41a'
            }}
          />
        </div>
      </div>
    )
  }