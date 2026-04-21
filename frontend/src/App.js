import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect, useMemo, useState } from 'react';
const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';
export default function App() {
    const [events, setEvents] = useState([]);
    const [policy, setPolicy] = useState(null);
    useEffect(() => {
        void Promise.all([
            fetch(`${API_BASE}/v1/events`).then((res) => res.json()).then(setEvents),
            fetch(`${API_BASE}/v1/policies`).then((res) => res.json()).then(setPolicy),
        ]);
    }, []);
    const summary = useMemo(() => {
        const pii = events.reduce((acc, event) => acc + event.redaction_count, 0);
        const cost = events.reduce((acc, event) => acc + event.estimated_cost, 0);
        const carbon = events.reduce((acc, event) => acc + event.estimated_carbon, 0);
        return { pii, cost, carbon };
    }, [events]);
    return (_jsxs("main", { style: { fontFamily: 'Arial, sans-serif', margin: '2rem' }, children: [_jsx("h1", { children: "AI Access Gateway Dashboard" }), policy && (_jsxs("section", { children: [_jsx("h2", { children: "Policies" }), _jsxs("p", { children: [_jsx("strong", { children: "Roles:" }), " ", policy.role_tiers.join(', ')] }), _jsxs("p", { children: [_jsx("strong", { children: "PII:" }), " ", policy.pii_policy] }), _jsxs("p", { children: [_jsx("strong", { children: "Fallback:" }), " ", policy.fallback_policy] })] })), _jsxs("section", { children: [_jsx("h2", { children: "Summary" }), _jsxs("ul", { children: [_jsxs("li", { children: ["Total redactions: ", summary.pii] }), _jsxs("li", { children: ["Estimated cost: $", summary.cost.toFixed(4)] }), _jsxs("li", { children: ["Estimated carbon: ", summary.carbon.toFixed(4), " kgCO2e"] })] })] }), _jsxs("section", { children: [_jsx("h2", { children: "Recent Events" }), _jsxs("table", { border: 1, cellPadding: 6, cellSpacing: 0, children: [_jsx("thead", { children: _jsxs("tr", { children: [_jsx("th", { children: "Time" }), _jsx("th", { children: "User" }), _jsx("th", { children: "Role" }), _jsx("th", { children: "Provider" }), _jsx("th", { children: "Model" }), _jsx("th", { children: "PII Types" }), _jsx("th", { children: "Redactions" }), _jsx("th", { children: "Cost" }), _jsx("th", { children: "Carbon" }), _jsx("th", { children: "Status" })] }) }), _jsx("tbody", { children: events.map((event) => (_jsxs("tr", { children: [_jsx("td", { children: new Date(event.timestamp).toLocaleString() }), _jsx("td", { children: event.user_id }), _jsx("td", { children: event.role }), _jsx("td", { children: event.provider }), _jsx("td", { children: event.model }), _jsx("td", { children: event.pii_types.join(', ') || '-' }), _jsx("td", { children: event.redaction_count }), _jsx("td", { children: event.estimated_cost.toFixed(4) }), _jsx("td", { children: event.estimated_carbon.toFixed(4) }), _jsx("td", { children: event.status })] }, `${event.timestamp}-${event.user_id}`))) })] })] })] }));
}
