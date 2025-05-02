export default function ControlPanel({ isCollecting, startCollection, stopCollection, healthStatus }) {
    return (
      <div className="control-panel">
        <button 
          onClick={startCollection} 
          disabled={isCollecting || !healthStatus.serialConnected || !healthStatus.modelLoaded}
        >
          {isCollecting ? 'Collecting...' : 'Start Monitoring'}
        </button>
        <button onClick={stopCollection} disabled={!isCollecting}>
          Stop Monitoring
        </button>
      </div>
    )
  }