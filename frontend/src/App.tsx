import { useEffect, useMemo, useState } from 'react'

type EventRecord = {
  timestamp: string
  user_id: string
  role: string
  provider: string
  model: string
  complexity_score: number
  pii_types: string[]
  redaction_count: number
  estimated_cost: number
  estimated_carbon: number
  latency_ms: number
  status: string
}

type Policy = {
  role_tiers: string[]
  pii_policy: string
  fallback_policy: string
}

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export default function App() {
  const [events, setEvents] = useState<EventRecord[]>([])
  const [policy, setPolicy] = useState<Policy | null>(null)

  useEffect(() => {
    void Promise.all([
      fetch(`${API_BASE}/v1/events`).then((res) => res.json()).then(setEvents),
      fetch(`${API_BASE}/v1/policies`).then((res) => res.json()).then(setPolicy),
    ])
  }, [])

  const summary = useMemo(() => {
    const pii = events.reduce((acc, event) => acc + event.redaction_count, 0)
    const cost = events.reduce((acc, event) => acc + event.estimated_cost, 0)
    const carbon = events.reduce((acc, event) => acc + event.estimated_carbon, 0)
    return { pii, cost, carbon }
  }, [events])

  return (
    <main style={{ fontFamily: 'Arial, sans-serif', margin: '2rem' }}>
      <h1>AI Access Gateway Dashboard</h1>
      {policy && (
        <section>
          <h2>Policies</h2>
          <p><strong>Roles:</strong> {policy.role_tiers.join(', ')}</p>
          <p><strong>PII:</strong> {policy.pii_policy}</p>
          <p><strong>Fallback:</strong> {policy.fallback_policy}</p>
        </section>
      )}

      <section>
        <h2>Summary</h2>
        <ul>
          <li>Total redactions: {summary.pii}</li>
          <li>Estimated cost: ${summary.cost.toFixed(4)}</li>
          <li>Estimated carbon: {summary.carbon.toFixed(4)} kgCO2e</li>
        </ul>
      </section>

      <section>
        <h2>Recent Events</h2>
        <table border={1} cellPadding={6} cellSpacing={0}>
          <thead>
            <tr>
              <th>Time</th>
              <th>User</th>
              <th>Role</th>
              <th>Provider</th>
              <th>Model</th>
              <th>PII Types</th>
              <th>Redactions</th>
              <th>Cost</th>
              <th>Carbon</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {events.map((event) => (
              <tr key={`${event.timestamp}-${event.user_id}`}>
                <td>{new Date(event.timestamp).toLocaleString()}</td>
                <td>{event.user_id}</td>
                <td>{event.role}</td>
                <td>{event.provider}</td>
                <td>{event.model}</td>
                <td>{event.pii_types.join(', ') || '-'}</td>
                <td>{event.redaction_count}</td>
                <td>{event.estimated_cost.toFixed(4)}</td>
                <td>{event.estimated_carbon.toFixed(4)}</td>
                <td>{event.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </main>
  )
}
