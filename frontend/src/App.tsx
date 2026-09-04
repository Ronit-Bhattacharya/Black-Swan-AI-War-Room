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
    const data = await api(`/api/cases/${c.id}`);
    setActive(data);
    await loadAudit(c.id);
  };

  const runAnalysis = async () => {
    if (!active) return;

    try {
      setBusy(true);

      await api(`/api/cases/${active.id}/analyze`, {
        method: "POST",
        body: JSON.stringify({
          assumptions: {
            initial_investment: 50000000,
            annual_cash_flows: [
              9000000,
              11000000,
              13000000,
              15000000,
              17000000,
            ],
            discount_rate: 0.11,
            annual_revenue: 40000000,
            annual_cost: 29000000,
            years: 5,
            revenue_shock_low: -0.25,
            revenue_shock_high: 0.1,
            cost_shock_low: 0,
            cost_shock_high: 0.3,
          },
          nodes: [
            {
              id: "battery",
              label: "Battery Supplier",
              single_source: true,
            },
            {
              id: "fleet",
              label: "Fleet Operations",
              single_source: false,
            },
          ],
          edges: [
            {
              source: "battery",
              target: "fleet",
            },
          ],
        }),
      });

      const updated = await api(`/api/cases/${active.id}`);
      setActive(updated);

      await loadAudit(active.id);

      refresh();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  const result = active?.result;

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
              <div className="error">{error}</div>
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
            </div>
          ) : (
            <>
              <div className="card">
                <span className="eyebrow">
                  ACTIVE CASE
                </span>

                <h2>{active.title}</h2>

                <p>{active.decision}</p>

                <button
                  disabled={busy}
                  onClick={runAnalysis}
                >
                  {busy
                    ? "Analysing..."
                    : "Run Analysis"}
                </button>
              </div>

              <div className="metrics">
                <Metric
                  icon={<Calculator />}
                  label="NPV"
                  value={
                    result?.financial
                      ? String(result.financial.npv)
                      : "Pending"
                  }
                />

                <Metric
                  icon={<TriangleAlert />}
                  label="ROI"
                  value={
                    result?.financial
                      ? String(result.financial.roi)
                      : "Pending"
                  }
                />

                <Metric
                  icon={<Network />}
                  label="Payback"
                  value={
                    result?.financial
                      ? String(
                          result.financial.payback_years
                        )
                      : "Pending"
                  }
                />

                <Metric
                  icon={<CheckCircle2 />}
                  label="Decision"
                  value={
                    result?.committee?.decision ||
                    "Pending"
                  }
                />
              </div>

              {result?.black_swan && (
                <div className="card">
                  <h2>Black Swan Scenario</h2>

                  <p>
                    <strong>Title:</strong>{" "}
                    {result.black_swan.title}
                  </p>

                  <p>
                    <strong>Trigger:</strong>{" "}
                    {result.black_swan.trigger}
                  </p>

                  <p>
                    <strong>Transmission:</strong>{" "}
                    {
                      result.black_swan
                        .transmission_path
                    }
                  </p>
                </div>
              )}

              {result?.committee && (
                <div className="card">
                  <h2>
                    Committee Recommendation
                  </h2>

                  <h3>
                    {
                      result.committee
                        .decision
                    }
                  </h3>

                  <ul>
                    {result.committee.conditions.map(
                      (x: string) => (
                        <li key={x}>{x}</li>
                      )
                    )}
                  </ul>
                </div>
              )}

              <div className="card">
                <div className="sectionTitle">
                  <Activity />
                  Audit Trail
                </div>

                {audit.map((a: any) => (
                  <div
                    key={a.id}
                    style={{
                      marginBottom: "12px",
                    }}
                  >
                    <strong>{a.agent}</strong>

                    <div>{a.summary}</div>
                  </div>
                ))}
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
      <div className="metricIcon">
        {icon}
      </div>

      <small>{label}</small>

      <strong>{value}</strong>
    </div>
  );
}