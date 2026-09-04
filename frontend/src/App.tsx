import { useEffect, useState } from "react";
import {
  Activity,
  ShieldCheck,
  BrainCircuit,
  TriangleAlert,
  Network,
  Calculator,
  CheckCircle2,
} from "lucide-react";

import { api } from "./api";

export default function App() {
  const [cases, setCases] = useState<any[]>([]);
  const [active, setActive] = useState<any>(null);
  const [audit, setAudit] = useState<any[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const refresh = async () => {
    try {
      const data = await api("/api/cases");
      setCases(data);
    } catch (err: any) {
      setError(err.message);
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  const createCase = async () => {
    try {
      setBusy(true);

      const result = await api("/api/cases", {
        method: "POST",
        body: JSON.stringify({
          title: "India Electric Fleet Expansion",
          decision:
            "Stress-test whether an Indian logistics company should expand its electric delivery fleet.",
        }),
      });

      setActive(result);
      refresh();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  const loadAudit = async (caseId: string) => {
    try {
      const logs = await api(`/api/cases/${caseId}/audit`);
      setAudit(logs);
    } catch (err) {
      console.error(err);
    }
  };

  const openCase = async (c: any) => {
    try {
      const data = await api(`/api/cases/${c.id}`);
      setActive(data);
      await loadAudit(c.id);
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="shell">
      <header>
        <div>
          <span className="eyebrow">
            ADVERSARIAL DECISION INTELLIGENCE
          </span>

          <h1>Black Swan AI War Room</h1>
        </div>

        <div className="secure">
          <ShieldCheck size={18} />
          Human approval gated
        </div>
      </header>

      <main>
        <section className="left">
          <div className="card hero">
            <h2>Launch a decision investigation</h2>

            <p>
              Test assumptions, analyse dependencies and
              simulate Black Swan risk scenarios.
            </p>

            <button disabled={busy} onClick={createCase}>
              {busy ? "Creating..." : "Create Case"}
            </button>

            {error && (
              <div className="error">
                {error}
              </div>
            )}
          </div>

          <div className="card">
            <div className="sectionTitle">
              <Activity />
              Cases
            </div>

            <div className="caseList">
              {cases.map((c) => (
                <button
                  key={c.id}
                  className={`case ${
                    active?.id === c.id ? "selected" : ""
                  }`}
                  onClick={() => openCase(c)}
                >
                  <span>{c.title}</span>
                  <small>{c.status}</small>
                </button>
              ))}
            </div>
          </div>
        </section>

        <section className="right">
          {!active ? (
            <div className="empty">
              <BrainCircuit size={60} />
              <h2>Create or Select a Case</h2>
              <p>
                Your Black Swan investigation results
                appear here.
              </p>
            </div>
          ) : (
            <>
              <div className="card">
                <span className="eyebrow">
                  ACTIVE CASE
                </span>

                <h2>{active.title}</h2>

                <p>{active.decision}</p>
              </div>

              <div className="metrics">
                <Metric
                  icon={<Calculator />}
                  label="Financial"
                  value="Ready"
                />

                <Metric
                  icon={<TriangleAlert />}
                  label="Risk"
                  value="Ready"
                />

                <Metric
                  icon={<Network />}
                  label="Dependencies"
                  value="Ready"
                />

                <Metric
                  icon={<CheckCircle2 />}
                  label="Committee"
                  value="Pending"
                />
              </div>

              <div className="card">
                <div className="sectionTitle">
                  <Activity />
                  Audit Trail
                </div>

                {audit.length === 0 ? (
                  <p>No audit events yet.</p>
                ) : (
                  audit.map((a: any) => (
                    <div key={a.id}>
                      <strong>{a.agent}</strong>
                      <br />
                      {a.summary}
                    </div>
                  ))
                )}
              </div>
            </>
          )}
        </section>
      </main>
    </div>
  );
}

function Metric({
  icon,
  label,
  value,
}: {
  icon: any;
  label: string;
  value: string;
}) {
  return (
    <div className="metric">
      <div className="metricIcon">{icon}</div>

      <small>{label}</small>

      <strong>{value}</strong>
    </div>
  );
}