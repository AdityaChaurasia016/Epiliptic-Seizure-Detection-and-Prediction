export default function StatusPanel({ healthStatus, error }) {
    return (
      <div className="status-panel">
        <h2>System Status</h2>
        <p>Serial Connected: {healthStatus.serialConnected ? '✅' : '❌'}</p>
        <p>Model Loaded: {healthStatus.modelLoaded ? '✅' : '❌'}</p>
        {error && <div className="error-message">{error}</div>}
      </div>
    )
  }