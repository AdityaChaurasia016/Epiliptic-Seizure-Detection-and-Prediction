// import { useState, useEffect, useRef } from 'react'
// import axios from 'axios'

// const API_BASE_URL = 'http://localhost:5000'

// export default function useSeizureDetection() {
//   const [eegData, setEegData] = useState([])
//   const [prediction, setPrediction] = useState(null)
//   const [isCollecting, setIsCollecting] = useState(false)
//   const [healthStatus, setHealthStatus] = useState({
//     serialConnected: false,
//     modelLoaded: false
//   })
//   const [error, setError] = useState(null)
//   const collectionInterval = useRef(null)

//   useEffect(() => {
//     checkHealth()
//     return () => {
//       if (collectionInterval.current) {
//         clearInterval(collectionInterval.current)
//       }
//     }
//   }, [])

//   const checkHealth = async () => {
//     try {
//       const response = await axios.get(`${API_BASE_URL}/health`)
//       setHealthStatus({
//         serialConnected: response.data.serial_connected,
//         modelLoaded: response.data.model_loaded
//       })
//     } catch (err) {
//       setError('Failed to connect to the backend service')
//       console.error('Health check failed:', err)
//     }
//   }

//   const startCollection = async () => {
//     try {
//       setError(null)
//       await axios.get(`${API_BASE_URL}/start`)
//       setIsCollecting(true)
//       beginCollectionCycle()
//     } catch (err) {
//       setError('Failed to start data collection')
//       console.error('Start collection failed:', err)
//     }
//   }

//   const beginCollectionCycle = () => {
//     if (collectionInterval.current) {
//       clearInterval(collectionInterval.current)
//     }

//     collectionInterval.current = setInterval(async () => {
//       try {
//         const dataResponse = await axios.get(`${API_BASE_URL}/get_data`)
        
//         if (dataResponse.data.data_available) {
//           const rawData = dataResponse.data.data
//           const formattedData = rawData.map((value, index) => ({
//             index,
//             value
//           }))
          
//           setEegData(formattedData)
          
//           const predictionResponse = await axios.get(`${API_BASE_URL}/predict`)
//           setPrediction(predictionResponse.data)
          
//           setIsCollecting(false)
//           clearInterval(collectionInterval.current)
          
//           setTimeout(startCollection, 500)
//         } else {
//           setEegData(prev => [
//             ...prev.slice(-dataResponse.data.samples),
//             ...Array(dataResponse.data.samples - prev.length).fill(0).map((_, i) => ({
//               index: i + (prev.length > 0 ? prev[prev.length - 1].index + 1 : 0),
//               value: 0
//             }))
//           ])
//         }
//       } catch (err) {
//         setError('Error during data collection cycle')
//         console.error('Collection cycle error:', err)
//         clearInterval(collectionInterval.current)
//         setIsCollecting(false)
//       }
//     }, 100)
//   }

//   const stopCollection = () => {
//     if (collectionInterval.current) {
//       clearInterval(collectionInterval.current)
//       collectionInterval.current = null
//     }
//     setIsCollecting(false)
//   }

//   return {
//     eegData,
//     prediction,
//     isCollecting,
//     healthStatus,
//     error,
//     startCollection,
//     stopCollection
//   }
// }



import { useState, useEffect, useRef } from 'react'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

export default function useSeizureDetection() {
  const [eegData, setEegData] = useState([])
  const [prediction, setPrediction] = useState(null)
  const [isCollecting, setIsCollecting] = useState(false)
  const [healthStatus, setHealthStatus] = useState({
    serialConnected: false,
    modelLoaded: false
  })
  const [error, setError] = useState(null)
  const collectionInterval = useRef(null)

  // Enhanced error handling
  const handleError = (error, context) => {
    let errorMessage = context
    if (error.response) {
      errorMessage += `: ${error.response.status} ${error.response.data?.message || ''}`
    } else if (error.request) {
      errorMessage += ': No response from server'
    } else {
      errorMessage += `: ${error.message}`
    }
    setError(errorMessage)
    console.error(errorMessage, error)
    return errorMessage
  }

  const checkHealth = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/health`, {
        timeout: 5000
      })
      setHealthStatus({
        serialConnected: response.data.serial_connected,
        modelLoaded: response.data.model_loaded
      })
      setError(null)
    } catch (err) {
      handleError(err, 'Health check failed')
    }
  }

  const startCollection = async () => {
    try {
      setError(null)
      const response = await axios.get(`${API_BASE_URL}/start`, {
        timeout: 5000
      })
      setIsCollecting(true)
      beginCollectionCycle()
    } catch (err) {
      handleError(err, 'Start collection failed')
      setIsCollecting(false)
    }
  }

  const beginCollectionCycle = () => {
    if (collectionInterval.current) {
      clearInterval(collectionInterval.current)
    }

    collectionInterval.current = setInterval(async () => {
      try {
        // Get data
        const dataResponse = await axios.get(`${API_BASE_URL}/get_data`, {
          timeout: 5000
        })
        
        if (dataResponse.data.data_available) {
          // Process full buffer
          const rawData = dataResponse.data.data
          const formattedData = rawData.map((value, index) => ({
            index,
            value
          }))
          
          setEegData(formattedData)
          
          // Make prediction
          const predictionResponse = await axios.get(`${API_BASE_URL}/predict`, {
            timeout: 5000
          })
          setPrediction(predictionResponse.data)
          
          // Reset for next collection
          setIsCollecting(false)
          clearInterval(collectionInterval.current)
          
          // Start new collection after brief pause
          setTimeout(startCollection, 1000)
        } else {
          // Update with partial data
          const progress = dataResponse.data.samples
          setEegData(prev => [
            ...prev.slice(-progress),
            ...Array(Math.max(0, progress - prev.length)).fill(0).map((_, i) => ({
              index: i + (prev.length > 0 ? prev[prev.length - 1].index + 1 : 0),
              value: 0
            }))
          ])
        }
      } catch (err) {
        const errorMsg = handleError(err, 'Collection cycle error')
        if (err.response?.status === 400 && err.response.data?.status === 'incomplete') {
          // Expected error when buffer isn't full yet
          console.log('Waiting for more data...')
        } else {
          // Unexpected error - stop collection
          clearInterval(collectionInterval.current)
          setIsCollecting(false)
        }
      }
    }, 300) // Check every 300ms
  }

  const stopCollection = () => {
    if (collectionInterval.current) {
      clearInterval(collectionInterval.current)
      collectionInterval.current = null
    }
    setIsCollecting(false)
  }

  useEffect(() => {
    checkHealth()
    return () => {
      if (collectionInterval.current) {
        clearInterval(collectionInterval.current)
      }
    }
  }, [])

  return {
    eegData,
    prediction,
    isCollecting,
    healthStatus,
    error,
    startCollection,
    stopCollection,
    checkHealth
  }
}