import { useState, useEffect } from 'react'
import EEGChart from './components/EEGChart'
import PredictionPanel from './components/PredictionPanel'
import StatusPanel from './components/StatusPanel'
import ControlPanel from './components/ControlPanel'
import useSeizureDetection from './hooks/useSeizureDetection'
import './styles/dashboard.css'

function App() {
  const {
    eegData,
    prediction,
    isCollecting,
    healthStatus,
    error,
    startCollection,
    stopCollection
  } = useSeizureDetection()

  return (
    <div className="dashboard-container">
      <h1>EEG Seizure Detection Dashboard</h1>
      
      <StatusPanel healthStatus={healthStatus} error={error} />
      
      <ControlPanel 
        isCollecting={isCollecting}
        startCollection={startCollection}
        stopCollection={stopCollection}
        healthStatus={healthStatus}
      />
      
      <EEGChart data={eegData} />
      
      {prediction && <PredictionPanel prediction={prediction} />}
    </div>
  )
}

export default App