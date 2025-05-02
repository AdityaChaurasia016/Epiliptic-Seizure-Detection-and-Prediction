import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function EEGChart({ data }) {
  return (
    <div className="data-visualization">
      <h2>EEG Signal</h2>
      <div style={{ width: '100%', height: 400 }}>
        <ResponsiveContainer>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="index" 
              label={{ value: 'Sample Index', position: 'insideBottomRight', offset: -10 }} 
            />
            <YAxis 
              label={{ value: 'Amplitude', angle: -90, position: 'insideLeft' }} 
            />
            <Tooltip />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="value" 
              stroke="#8884d8" 
              dot={false} 
              activeDot={{ r: 6 }} 
              name="EEG Signal"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}