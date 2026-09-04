import { useEffect, useState, type ReactNode } from "react";
import {
  Activity,
  AlertCircle,
  BarChart3,
  BrainCircuit,
  Calculator,
  CheckCircle2,
  Clock3,
  Network,
  RefreshCw,
  ShieldCheck,
  Siren,
  Target,
  TriangleAlert,
} from "lucide-react";

import { api } from "./api";

type CaseSummary = {
  id: string;
  title: string;
  decision: string;
  status: string;
  assumptions?: Record<string, unknown>;
  result?: AnalysisResult;
};

type AuditEvent = {
  id: string;
  agent: string;
  event_type: string;
  summary: string;
  created_at?: string;
};

type FinancialResult = {
  npv: number;
  roi: number;
  payback_years: number | null;
};

type ScenarioResult = {
  iterations: number;
  seed: number;
  mean_npv: number;
  p05_npv: number;
  median_npv: number;
  p95_npv: number;
  probability_negative_npv: number;
};

type CriticalNode = {
  id: string;
  label: string;
  degree: number;
  single_source: boolean;
};

type DependencyResult = {
  critical_nodes: CriticalNode[];
  downstream_impact_count?: Record<string, number>;
};

type BlackSwanResult = {
  title: string;
  classification: string;
  trigger: string;
  transmission_path: string;
  early_warnings: string[];
  mitigations: string[];
};

type EvidenceVerification = {
  status: string;
  checks: string[];
};

type CommitteeResult = {
  decision: string;
  conditions: string[];
  human_approval_required: boolean;
  disclaimer: string;
};

type AnalysisResult = {
  financial?: FinancialResult;
  scenario?: ScenarioResult;
  dependencies?: DependencyResult;
  black_swan?: BlackSwanResult;
  contrarian_concerns?: string[];
  evidence_verification?: EvidenceVerification;
  committee?: CommitteeResult;
};

const ANALYSIS_PAYLOAD = {
  assumptions: {
    initial_investment: 50_000_000,
    annual_cash_flows: [
      9_000_000,
      11_000_000,
      13_000_000,
      15_000_000,
      17_000_000,
    ],
    discount_rate: 0.11,
    annual_revenue: 40_000_000,
    annual_cost: 29_000_000,
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
      id: "charging",
      label: "Charging Infrastructure",
      single_source: false,
    },
    {
      id: "fleet",
      label: "Fleet Operations",
      single_source: false,
    },
    {
      id: "customers",
      label: "Customer Service Levels",
      single_source: false,
    },
  ],
  edges: [
    {
      source: "battery",
      target: "fleet",
    },
    {
      source: "charging",
      target: "fleet",
    },
    {
      source: "fleet",
      target: "customers",
    },
  ],
};

export default function App() {
  const [cases, setCases] = useState<CaseSummary[]>([]);
  const [active, setActive] = useState<CaseSummary | null>(null);
  const [audit, setAudit] = useState<AuditEvent[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const refresh = async () => {
    try {
      const data = await api("/api/cases");
      setCases(Array.isArray(data) ? data : []);
    } catch (err: unknown) {
      setError(getErrorMessage(err));
    }
  };

useEffect(() => {
  let cancelled = false;

  const loadCases = async () => {
    try {
      const data = await api("/api/cases");

      if (!cancelled) {
        setCases(Array.isArray(data) ? data : []);
      }
    } catch (err: unknown) {
      if (!cancelled) {
        setError(getErrorMessage(err));
      }
    }
  };

  void loadCases();

  return () => {
    cancelled = true;
  };
}, []);

  const createCase = async () => {
    setBusy(true);
    setError("");

    try {
      const created = await api("/api/cases", {
        method: "POST",
        body: JSON.stringify({
          title: "India Electric Fleet Expansion",
          decision:
            "Stress-test whether an Indian logistics company should expand its electric delivery fleet.",
        }),
      });

      setActive(created);
      setAudit([]);
      await refresh();
      await loadAudit(created.id);
    } catch (err: unknown) {
      setError(getErrorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  const loadAudit = async (caseId: string) => {
    try {
      const logs = await api(`/api/cases/${caseId}/audit`);
      setAudit(Array.isArray(logs) ? logs : []);
    } catch (err: unknown) {
      setError(getErrorMessage(err));
    }
  };

  const openCase = async (selectedCase: CaseSummary) => {
    setBusy(true);
    setError("");

    try {
      const caseDetails = await api(`/api/cases/${selectedCase.id}`);
      setActive(caseDetails);
      await loadAudit(selectedCase.id);
    } catch (err: unknown) {
      setError(getErrorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  const runAnalysis = async () => {
    if (!active) {
      return;
    }

    setBusy(true);
    setError("");

    try {
      await api(`/api/cases/${active.id}/analyze`, {
        method: "POST",
        body: JSON.stringify(ANALYSIS_PAYLOAD),
      });

      const updatedCase = await api(`/api/cases/${active.id}`);

      setActive(updatedCase);
      await loadAudit(active.id);
      await refresh();
    } catch (err: unknown) {
      setError(getErrorMessage(err));
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
              Test financial assumptions, analyse cascading dependencies,
              simulate downside scenarios, and challenge the emerging
              recommendation.
            </p>

            <button disabled={busy} onClick={createCase}>
              {busy ? "Working..." : "Create Case"}
            </button>

            {error && (
              <div className="error" role="alert">
                <AlertCircle size={18} />
                <span>{error}</span>
              </div>
            )}
          </div>

          <div className="card">
            <div className="sectionTitle">
              <Activity />
              Cases
            </div>

            <div className="caseList">
              {cases.length === 0 ? (
                <p>No decision cases created yet.</p>
              ) : (
                cases.map((caseItem) => (
                  <button
                    key={caseItem.id}
                    type="button"
                    className={`case ${
                      active?.id === caseItem.id ? "selected" : ""
                    }`}
                    onClick={() => void openCase(caseItem)}
                  >
                    <span>{caseItem.title}</span>
                    <small>{caseItem.status}</small>
                  </button>
                ))
              )}
            </div>
          </div>

          <div className="card">
            <div className="sectionTitle">
              <Target />
              Scenario assumptions
            </div>

            <AssumptionRow
              label="Initial investment"
              value={formatCurrency(
                ANALYSIS_PAYLOAD.assumptions.initial_investment,
              )}
            />

            <AssumptionRow
              label="Discount rate"
              value={formatPercentage(
                ANALYSIS_PAYLOAD.assumptions.discount_rate,
              )}
            />

            <AssumptionRow
              label="Forecast horizon"
              value={`${ANALYSIS_PAYLOAD.assumptions.years} years`}
            />

            <AssumptionRow
              label="Revenue shock"
              value={`${formatPercentage(
                ANALYSIS_PAYLOAD.assumptions.revenue_shock_low,
              )} to ${formatPercentage(
                ANALYSIS_PAYLOAD.assumptions.revenue_shock_high,
              )}`}
            />

            <AssumptionRow
              label="Cost shock"
              value={`${formatPercentage(
                ANALYSIS_PAYLOAD.assumptions.cost_shock_low,
              )} to ${formatPercentage(
                ANALYSIS_PAYLOAD.assumptions.cost_shock_high,
              )}`}
            />

            <p className="disclaimer">
              These values are scenario assumptions, not verified forecasts.
            </p>
          </div>
        </section>

        <section className="right">
          {!active ? (
            <div className="empty">
              <BrainCircuit size={60} />
              <h2>Create or select a case</h2>
              <p>
                The financial analysis, stress scenarios, dependency risks,
                and agent audit trail will appear here.
              </p>
            </div>
          ) : (
            <>
              <div className="card caseHead">
                <div>
                  <span className="eyebrow">ACTIVE CASE</span>
                  <h2>{active.title}</h2>
                  <p>{active.decision}</p>
                </div>

                <button disabled={busy} onClick={runAnalysis}>
                  {busy ? (
                    <>
                      <RefreshCw size={17} />
                      Analysing...
                    </>
                  ) : (
                    <>
                      <BrainCircuit size={17} />
                      Run Analysis
                    </>
                  )}
                </button>
              </div>

              <div className="metrics">
                <Metric
                  icon={<Calculator />}
                  label="Base NPV"
                  value={
                    result?.financial
                      ? formatCurrency(result.financial.npv)
                      : "Pending"
                  }
                  status={
                    result?.financial
                      ? result.financial.npv >= 0
                        ? "positive"
                        : "negative"
                      : "neutral"
                  }
                />

                <Metric
                  icon={<BarChart3 />}
                  label="ROI"
                  value={
                    result?.financial
                      ? formatPercentage(result.financial.roi)
                      : "Pending"
                  }
                  status={
                    result?.financial
                      ? result.financial.roi >= 0
                        ? "positive"
                        : "negative"
                      : "neutral"
                  }
                />

                <Metric
                  icon={<Clock3 />}
                  label="Payback"
                  value={
                    result?.financial?.payback_years == null
                      ? result?.financial
                        ? "Not reached"
                        : "Pending"
                      : `${result.financial.payback_years.toFixed(2)} years`
                  }
                />

                <Metric
                  icon={<CheckCircle2 />}
                  label="Committee"
                  value={result?.committee?.decision ?? "Pending"}
                  status={decisionStatus(result?.committee?.decision)}
                />
              </div>

              {result?.financial && (
                <section className="card">
                  <div className="sectionTitle">
                    <Calculator />
                    Financial Analysis
                  </div>

                  <div className="detailGrid">
                    <Detail
                      label="Net present value"
                      value={formatCurrency(result.financial.npv)}
                    />

                    <Detail
                      label="Return on investment"
                      value={formatPercentage(result.financial.roi)}
                    />

                    <Detail
                      label="Payback period"
                      value={
                        result.financial.payback_years == null
                          ? "Not reached in supplied horizon"
                          : `${result.financial.payback_years.toFixed(
                              2,
                            )} years`
                      }
                    />
                  </div>
                </section>
              )}

              {result?.scenario && (
                <section className="card">
                  <div className="sectionTitle">
                    <BarChart3 />
                    Monte Carlo Scenario Analysis
                  </div>

                  <div className="detailGrid">
                    <Detail
                      label="Mean NPV"
                      value={formatCurrency(result.scenario.mean_npv)}
                    />

                    <Detail
                      label="5th percentile NPV"
                      value={formatCurrency(result.scenario.p05_npv)}
                    />

                    <Detail
                      label="Median NPV"
                      value={formatCurrency(result.scenario.median_npv)}
                    />

                    <Detail
                      label="95th percentile NPV"
                      value={formatCurrency(result.scenario.p95_npv)}
                    />

                    <Detail
                      label="Negative NPV probability"
                      value={formatPercentage(
                        result.scenario.probability_negative_npv,
                      )}
                    />

                    <Detail
                      label="Simulation runs"
                      value={result.scenario.iterations.toLocaleString(
                        "en-IN",
                      )}
                    />

                    <Detail
                      label="Reproducibility seed"
                      value={String(result.scenario.seed)}
                    />
                  </div>

                  <RiskBar
                    probability={
                      result.scenario.probability_negative_npv
                    }
                  />

                  <p className="disclaimer">
                    Simulation results depend on the supplied ranges and do not
                    represent guaranteed outcomes.
                  </p>
                </section>
              )}

              {result?.dependencies &&
                (() => {
                  const dependencies = result.dependencies;

                  if (!dependencies) {
                    return null;
                  }

                  return (
                    <section className="card">
                      <div className="sectionTitle">
                        <Network />
                        Dependency Risk Analysis
                      </div>

                      {dependencies.critical_nodes.length === 0 ? (
                        <p>No critical dependency nodes were detected.</p>
                      ) : (
                        <div className="dependencyList">
                          {dependencies.critical_nodes.map((node) => (
                            <article className="dependencyItem" key={node.id}>
                              <div>
                                <strong>{node.label}</strong>
                                <small>{node.id}</small>
                              </div>

                              <div>
                                <span className="tag">
                                  Degree {node.degree}
                                </span>

                                {node.single_source && (
                                  <span className="tag">
                                    Single source
                                  </span>
                                )}
                              </div>

                              {dependencies.downstream_impact_count?.[node.id] != null && (
                                <p>
                                  Downstream nodes affected:{" "}
                                  {dependencies.downstream_impact_count[node.id]}
                                </p>
                              )}
                            </article>
                          ))}
                        </div>
                      )}
                    </section>
                  );
                })()}

              {result?.black_swan && (
                <section className="card alert">
                  <div className="sectionTitle">
                    <Siren />
                    Black Swan Threat
                  </div>

                  <div className="tag">
                    {result.black_swan.classification}
                  </div>

                  <h2>{result.black_swan.title}</h2>

                  <Detail
                    label="Trigger"
                    value={result.black_swan.trigger}
                  />

                  <Detail
                    label="Transmission path"
                    value={result.black_swan.transmission_path}
                  />

                  <div className="twoColumn">
                    <div>
                      <h3>Early warning indicators</h3>

                      <ul>
                        {result.black_swan.early_warnings.map(
                          (warning) => (
                            <li key={warning}>{warning}</li>
                          ),
                        )}
                      </ul>
                    </div>

                    <div>
                      <h3>Mitigations</h3>

                      <ul>
                        {result.black_swan.mitigations.map(
                          (mitigation) => (
                            <li key={mitigation}>{mitigation}</li>
                          ),
                        )}
                      </ul>
                    </div>
                  </div>
                </section>
              )}

              {result?.contrarian_concerns && (
                <section className="card">
                  <div className="sectionTitle">
                    <TriangleAlert />
                    Contrarian Challenge
                  </div>

                  {result.contrarian_concerns.length === 0 ? (
                    <p>
                      No automatic blocking concern was found. Human validation
                      of the assumptions is still required.
                    </p>
                  ) : (
                    <ul>
                      {result.contrarian_concerns.map((concern) => (
                        <li key={concern}>{concern}</li>
                      ))}
                    </ul>
                  )}
                </section>
              )}

              {result?.evidence_verification && (
                <section className="card">
                  <div className="sectionTitle">
                    <ShieldCheck />
                    Evidence Verification
                  </div>

                  <div
                    className={`verificationStatus ${
                      result.evidence_verification.status === "PASS"
                        ? "passed"
                        : "failed"
                    }`}
                  >
                    {result.evidence_verification.status}
                  </div>

                  <ul>
                    {result.evidence_verification.checks.map((check) => (
                      <li key={check}>{check}</li>
                    ))}
                  </ul>
                </section>
              )}

              {result?.committee && (
                <section className="card decision">
                  <span className="eyebrow">
                    CONDITIONAL DECISION MEMO
                  </span>

                  <h2>Committee Recommendation</h2>

                  <div
                    className={`decisionBadge ${decisionStatus(
                      result.committee.decision,
                    )}`}
                  >
                    {result.committee.decision}
                  </div>

                  <h3>Conditions</h3>

                  <ul>
                    {result.committee.conditions.map((condition) => (
                      <li key={condition}>{condition}</li>
                    ))}
                  </ul>

                  <div className="approvalNotice">
                    <ShieldCheck size={18} />

                    <span>
                      Human approval required:{" "}
                      <strong>
                        {result.committee.human_approval_required
                          ? "Yes"
                          : "No"}
                      </strong>
                    </span>
                  </div>

                  <p className="disclaimer">
                    {result.committee.disclaimer}
                  </p>
                </section>
              )}

              <section className="card">
                <div className="sectionTitle">
                  <Activity />
                  Agent Audit Trail
                </div>

                {audit.length === 0 ? (
                  <p>No audit events are available yet.</p>
                ) : (
                  <div className="timeline">
                    {audit.map((event, index) => (
                      <article className="event" key={event.id}>
                        <div className="dot">{index + 1}</div>

                        <div>
                          <div className="eventHeading">
                            <strong>{event.agent}</strong>
                            <span>{event.event_type}</span>
                          </div>

                          <p>{event.summary}</p>

                          {event.created_at && (
                            <small>
                              {formatDateTime(event.created_at)}
                            </small>
                          )}
                        </div>
                      </article>
                    ))}
                  </div>
                )}
              </section>
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
  status = "neutral",
}: {
  icon: ReactNode;
  label: string;
  value: string;
  status?: "positive" | "negative" | "warning" | "neutral";
}) {
  return (
    <div className={`metric ${status}`}>
      <div className="metricIcon">{icon}</div>
      <small>{label}</small>
      <strong>{value}</strong>
    </div>
  );
}

function Detail({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="detail">
      <small>{label}</small>
      <strong>{value}</strong>
    </div>
  );
}

function AssumptionRow({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="assumptionRow">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function RiskBar({ probability }: { probability: number }) {
  const safeProbability = Math.min(Math.max(probability, 0), 1);
  const percentage = safeProbability * 100;

  let riskLabel = "Low";
  let riskClass = "low";

  if (percentage >= 50) {
    riskLabel = "High";
    riskClass = "high";
  } else if (percentage >= 25) {
    riskLabel = "Medium";
    riskClass = "medium";
  }

  return (
    <div className="riskBarBlock">
      <div className="riskBarHeader">
        <span>Downside risk</span>
        <strong>
          {riskLabel} · {percentage.toFixed(1)}%
        </strong>
      </div>

      <div className="riskBarTrack">
        <div
          className={`riskBarFill ${riskClass}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

function formatCurrency(value: number) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(value);
}

function formatPercentage(value: number) {
  return new Intl.NumberFormat("en-IN", {
    style: "percent",
    maximumFractionDigits: 2,
  }).format(value);
}

function formatDateTime(value: string) {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("en-IN", {
    dateStyle: "medium",
    timeStyle: "medium",
  }).format(date);
}

function decisionStatus(
  decision?: string,
): "positive" | "negative" | "warning" | "neutral" {
  if (!decision) {
    return "neutral";
  }

  if (decision === "PROCEED") {
    return "positive";
  }

  if (decision === "REJECT") {
    return "negative";
  }

  if (
    decision === "DEFER" ||
    decision === "PROCEED_WITH_CONDITIONS"
  ) {
    return "warning";
  }

  return "neutral";
}

function getErrorMessage(error: unknown) {
  if (error instanceof Error) {
    return error.message;
  }

  return "An unexpected error occurred.";
}