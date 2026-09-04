import {
  useEffect,
  useRef,
  useState,
} from "react";

import {
  AnimatePresence,
  motion,
} from "framer-motion";

import {
  Activity,
  AlertCircle,
  BrainCircuit,
  Database,
  FileSearch,
  Layers3,
  Loader2,
  Network,
  PanelLeftClose,
  PanelLeftOpen,
  Play,
  Plus,
  Search,
  ShieldCheck,
  Siren,
  Sparkles,
  X,
  Zap,
  type LucideIcon,
} from "lucide-react";

import { api } from "./api";

import type {
  AuditEvent,
  CaseSummary,
} from "./types";

import {
  CursorGlow,
  ThinkingOverlay,
  Toast,
} from "./components/Effects";

import {
  AgentFlow,
  AuditPanel,
  CommitteePanel,
  EvidencePanel,
  RedTeamPanel,
  ResearchPanel,
} from "./components/Panels";

import {
  Badge,
  GlassCard,
  SectionTitle,
  Skeleton,
  cx,
  safeArray,
} from "./components/ui";


type TabKey =
  | "command"
  | "research"
  | "risk"
  | "decision"
  | "audit";


type TabDefinition = {
  key: TabKey;
  label: string;
  Icon: LucideIcon;
};


type FeatureDefinition = {
  label: string;
  description: string;
  Icon: LucideIcon;
};


const TABS: TabDefinition[] = [
  {
    key: "command",
    label: "Command",
    Icon: BrainCircuit,
  },
  {
    key: "research",
    label: "Research",
    Icon: FileSearch,
  },
  {
    key: "risk",
    label: "Red Team",
    Icon: Siren,
  },
  {
    key: "decision",
    label: "Decision",
    Icon: ShieldCheck,
  },
  {
    key: "audit",
    label: "Audit",
    Icon: Activity,
  },
];


const FEATURES: FeatureDefinition[] = [
  {
    label: "Fail closed",
    description:
      "Weak evidence automatically defers the decision.",
    Icon: ShieldCheck,
  },
  {
    label: "Red team",
    description:
      "Assumptions are tested with adversarial scenarios.",
    Icon: Siren,
  },
  {
    label: "Evidence gate",
    description:
      "Claims remain separate from verified evidence.",
    Icon: Database,
  },
  {
    label: "Live audit",
    description:
      "Every agent execution produces a traceable event.",
    Icon: Activity,
  },
];


const INITIAL_FORM = {
  title: "",
  decision: "",
  context: "",
};


function getErrorMessage(
  error: unknown,
): string {
  if (error instanceof Error) {
    return error.message;
  }

  return "An unexpected error occurred.";
}


export default function App() {
  const [sidebarOpen, setSidebarOpen] =
    useState(true);

  const [cases, setCases] =
    useState<CaseSummary[]>([]);

  const [activeCase, setActiveCase] =
    useState<CaseSummary | null>(null);

  const [auditEvents, setAuditEvents] =
    useState<AuditEvent[]>([]);

  const [activeTab, setActiveTab] =
    useState<TabKey>("command");

  const [creatingCase, setCreatingCase] =
    useState(false);

  const [orchestrating, setOrchestrating] =
    useState(false);

  const [loadingCase, setLoadingCase] =
    useState(false);

  const [error, setError] = useState("");
  const [toast, setToast] = useState("");
  const [search, setSearch] = useState("");

  const [form, setForm] = useState(
    INITIAL_FORM,
  );

  const toastTimer = useRef<
    number | undefined
  >(undefined);


  const showToast = (
    message: string,
  ) => {
    setToast(message);

    window.clearTimeout(
      toastTimer.current,
    );

    toastTimer.current =
      window.setTimeout(
        () => {
          setToast("");
        },
        3500,
      );
  };


  const loadCases = async () => {
    const result = await api.listCases();

    setCases(
      safeArray(result),
    );
  };


  const loadAudit = async (
    caseId: string,
  ) => {
    const result = await api.audit(
      caseId,
    );

    setAuditEvents(
      safeArray(result),
    );
  };


  useEffect(() => {
    let cancelled = false;

    const initialise = async () => {
      try {
        const result =
          await api.listCases();

        if (!cancelled) {
          setCases(
            safeArray(result),
          );
        }
      } catch (caughtError) {
        if (!cancelled) {
          setError(
            getErrorMessage(
              caughtError,
            ),
          );
        }
      }
    };

    void initialise();

    return () => {
      cancelled = true;

      window.clearTimeout(
        toastTimer.current,
      );
    };
  }, []);


  const updateForm = (
    field: keyof typeof INITIAL_FORM,
    value: string,
  ) => {
    setForm(
      (current) => ({
        ...current,
        [field]: value,
      }),
    );
  };


  const createCase = async () => {
    if (
      form.title.trim().length < 3
      || form.decision.trim().length < 10
    ) {
      setError(
        "Enter a case title and a decision question of at least 10 characters.",
      );
      return;
    }

    setCreatingCase(true);
    setError("");

    try {
      const created =
        await api.createCase({
          title: form.title.trim(),
          decision: form.decision.trim(),
          context: form.context.trim(),
        });

      setActiveCase(created);
      setActiveTab("command");
      setForm(INITIAL_FORM);

      await Promise.all([
        loadCases(),
        loadAudit(created.id),
      ]);

      showToast(
        "Case classified and investigation plan created.",
      );
    } catch (caughtError) {
      setError(
        getErrorMessage(
          caughtError,
        ),
      );
    } finally {
      setCreatingCase(false);
    }
  };


  const openCase = async (
    caseId: string,
  ) => {
    setLoadingCase(true);
    setError("");

    try {
      const selectedCase =
        await api.getCase(caseId);

      setActiveCase(selectedCase);
      setActiveTab("command");

      await loadAudit(caseId);
    } catch (caughtError) {
      setError(
        getErrorMessage(
          caughtError,
        ),
      );
    } finally {
      setLoadingCase(false);
    }
  };


  const runWarRoom = async () => {
    console.log(
      "[War Room] Button action started",
    );

    if (!activeCase) {
      console.error(
        "[War Room] No active case selected",
      );

      setError(
        "No active case is selected.",
      );

      return;
    }

    const caseId = activeCase.id;

    console.log(
      "[War Room] Active case ID:",
      caseId,
    );

    setOrchestrating(true);
    setError("");

    try {
      console.log(
        "[War Room] Sending orchestration request",
      );

      const orchestrationResponse =
        await api.orchestrate(caseId);

      console.log(
        "[War Room] Orchestration response:",
        orchestrationResponse,
      );

      const updatedCase =
        await api.getCase(caseId);

      setActiveCase(updatedCase);

      await Promise.all([
        loadCases(),
        loadAudit(caseId),
      ]);

      showToast(
        "War Room orchestration completed.",
      );

      console.log(
        "[War Room] Complete",
      );
    } catch (caughtError) {
      console.error(
        "[War Room] Failed:",
        caughtError,
      );

      setError(
        getErrorMessage(
          caughtError,
        ),
      );
    } finally {
      console.log(
        "[War Room] Removing reasoning overlay",
      );

      setOrchestrating(false);
    }
  };


  const startNewInvestigation = () => {
    setActiveCase(null);
    setActiveTab("command");
    setAuditEvents([]);
    setError("");
  };


  const filteredCases = cases.filter(
    (caseItem) => {
      const searchableText = (
        `${caseItem.title} ${caseItem.status}`
      ).toLowerCase();

      return searchableText.includes(
        search.toLowerCase(),
      );
    },
  );


  const result =
    activeCase?.result ?? {};

  const investigationPlan =
    result.plan;

  const orchestration =
    result.orchestration;


  return (
    <div className="min-h-screen overflow-x-hidden bg-[#04080f] text-slate-100">
      <CursorGlow />

      <div className="cyber-grid pointer-events-none fixed inset-0 z-0 opacity-50 bg-[linear-gradient(rgba(255,255,255,.018)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,.018)_1px,transparent_1px)] bg-[size:32px_32px]" />

      <ThinkingOverlay
        visible={orchestrating}
      />

      <Toast
        message={toast}
        onClose={() => setToast("")}
      />

      <aside
        className={cx(
          "fixed inset-y-0 left-0 z-40 hidden border-r border-white/10 bg-slate-950/85 backdrop-blur-xl transition-all duration-500 lg:block",
          sidebarOpen
            ? "w-72"
            : "w-20",
        )}
      >
        <div className="flex h-20 items-center gap-3 border-b border-white/10 px-5">
          <motion.div
            whileHover={{
              rotate: 8,
              scale: 1.08,
            }}
            className="grid h-11 w-11 shrink-0 place-items-center rounded-2xl bg-gradient-to-br from-cyan-300 to-violet-400 text-slate-950"
          >
            <BrainCircuit size={24} />
          </motion.div>

          {sidebarOpen && (
            <div>
              <p className="font-black text-white">
                Black Swan AI
              </p>

              <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-cyan-300">
                Universal War Room
              </p>
            </div>
          )}
        </div>

        <div className="p-4">
          <motion.button
            type="button"
            whileHover={{
              scale: 1.02,
              x: 2,
            }}
            whileTap={{
              scale: 0.98,
            }}
            onClick={startNewInvestigation}
            className="flex w-full items-center gap-2 rounded-2xl border border-cyan-300/20 bg-cyan-300/10 p-3 text-sm font-semibold text-cyan-100"
          >
            <Plus size={18} />

            {sidebarOpen
              && "New Investigation"}
          </motion.button>

          {sidebarOpen && (
            <div className="relative mt-4">
              <Search
                className="absolute left-3 top-3 text-slate-500"
                size={15}
              />

              <input
                value={search}
                onChange={(event) => {
                  setSearch(
                    event.target.value,
                  );
                }}
                className="w-full rounded-xl border border-white/10 bg-white/5 py-2.5 pl-9 pr-3 text-sm text-white outline-none transition focus:border-cyan-300/30"
                placeholder="Search cases"
              />
            </div>
          )}
        </div>

        <div className="h-[calc(100vh-198px)] overflow-y-auto px-3 pb-16">
          <div className="space-y-1">
            {filteredCases.map(
              (caseItem) => (
                <motion.button
                  type="button"
                  whileHover={{ x: 4 }}
                  key={caseItem.id}
                  onClick={() => {
                    void openCase(
                      caseItem.id,
                    );
                  }}
                  className={cx(
                    "flex w-full gap-3 rounded-2xl p-3 text-left transition",
                    activeCase?.id
                      === caseItem.id
                      ? "bg-white/[0.08] text-white"
                      : "text-slate-500 hover:bg-white/5 hover:text-slate-200",
                  )}
                >
                  <Layers3
                    size={17}
                    className="mt-0.5 shrink-0"
                  />

                  {sidebarOpen && (
                    <div className="min-w-0">
                      <p className="truncate text-sm font-semibold">
                        {caseItem.title}
                      </p>

                      <small className="text-[10px] uppercase tracking-[0.12em] text-slate-600">
                        {caseItem.status}
                      </small>
                    </div>
                  )}
                </motion.button>
              ),
            )}
          </div>
        </div>

        <button
          type="button"
          onClick={() => {
            setSidebarOpen(
              (current) => !current,
            );
          }}
          className="absolute bottom-4 right-4 grid h-10 w-10 place-items-center rounded-xl border border-white/10 bg-slate-900 text-slate-500 transition hover:border-cyan-300/30 hover:text-cyan-200"
        >
          {sidebarOpen ? (
            <PanelLeftClose size={18} />
          ) : (
            <PanelLeftOpen size={18} />
          )}
        </button>
      </aside>

      <div
        className={cx(
          "relative z-10 transition-all duration-500",
          sidebarOpen
            ? "lg:pl-72"
            : "lg:pl-20",
        )}
      >
        <header className="sticky top-0 z-30 flex min-h-20 items-center justify-between gap-4 border-b border-white/10 bg-[#04080f]/80 px-5 py-4 backdrop-blur-xl md:px-8">
          <div className="min-w-0">
            <p className="text-[10px] font-bold uppercase tracking-[0.22em] text-cyan-300">
              Adversarial Decision Intelligence
            </p>

            <h1 className="mt-1 truncate text-lg font-black text-white md:text-xl">
              {activeCase?.title
                ?? "Command Centre"}
            </h1>
          </div>

          <div className="flex shrink-0 items-center gap-3">
            <div className="hidden sm:block">
              <Badge
                tone="emerald"
                pulse
              >
                Local AI online
              </Badge>
            </div>

            {activeCase && (
              <motion.button
                type="button"
                whileHover={{
                  scale: 1.04,
                  boxShadow:
                    "0 0 40px rgba(34,211,238,.4)",
                }}
                whileTap={{ scale: 0.97 }}
                onClick={() => {
                  console.log(
                    "[War Room] Run button clicked",
                  );

                  void runWarRoom();
                }}
                disabled={orchestrating}
                className="flex items-center gap-2 rounded-2xl bg-white px-4 py-2.5 text-sm font-black text-slate-950 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {orchestrating ? (
                  <Loader2
                    className="animate-spin"
                    size={17}
                  />
                ) : (
                  <Play size={17} />
                )}

                <span className="hidden sm:inline">
                  Run War Room
                </span>

                <span className="sm:hidden">
                  Run
                </span>
              </motion.button>
            )}
          </div>
        </header>

        <main className="mx-auto max-w-[1680px] p-5 md:p-8">
          <AnimatePresence>
            {error && (
              <motion.div
                initial={{
                  opacity: 0,
                  y: -10,
                }}
                animate={{
                  opacity: 1,
                  y: 0,
                }}
                exit={{
                  opacity: 0,
                  y: -10,
                }}
                className="mb-5 flex items-start justify-between gap-4 rounded-2xl border border-rose-400/20 bg-rose-400/10 p-4 text-sm text-rose-100"
              >
                <span className="flex gap-2">
                  <AlertCircle
                    className="mt-0.5 shrink-0"
                    size={18}
                  />

                  {error}
                </span>

                <button
                  type="button"
                  onClick={() => setError("")}
                >
                  <X size={17} />
                </button>
              </motion.div>
            )}
          </AnimatePresence>

          {loadingCase ? (
            <div className="space-y-4">
              <Skeleton className="h-52" />

              <div className="grid gap-4 lg:grid-cols-2">
                <Skeleton className="h-72" />
                <Skeleton className="h-72" />
              </div>
            </div>
          ) : !activeCase ? (
            <div className="grid gap-6 xl:grid-cols-[1.1fr_.9fr]">
              <GlassCard className="p-6 md:p-8">
                <Badge tone="cyan" pulse>
                  Universal intake
                </Badge>

                <h2 className="mt-5 text-3xl font-black tracking-tight text-white md:text-5xl">
                  Turn any decision into an{" "}
                  <span className="bg-gradient-to-r from-cyan-200 to-violet-300 bg-clip-text text-transparent">
                    adversarial investigation.
                  </span>
                </h2>

                <p className="my-6 max-w-2xl leading-7 text-slate-400">
                  Classify, route, challenge and review
                  any strategic decision using local AI
                  and deterministic tools.
                </p>

                <form
                  onSubmit={(event) => {
                    event.preventDefault();
                    void createCase();
                  }}
                  className="space-y-4"
                >
                  <div>
                    <label
                      htmlFor="case-title"
                      className="mb-2 block text-xs font-semibold uppercase tracking-[0.14em] text-slate-500"
                    >
                      Case title
                    </label>

                    <input
                      id="case-title"
                      value={form.title}
                      onChange={(event) => {
                        updateForm(
                          "title",
                          event.target.value,
                        );
                      }}
                      placeholder="AI Insurance Claims Platform"
                      className="w-full rounded-2xl border border-white/10 bg-black/25 p-4 text-white outline-none transition focus:border-cyan-300/50 focus:ring-4 focus:ring-cyan-400/10"
                    />
                  </div>

                  <div>
                    <label
                      htmlFor="decision-question"
                      className="mb-2 block text-xs font-semibold uppercase tracking-[0.14em] text-slate-500"
                    >
                      Decision question
                    </label>

                    <textarea
                      id="decision-question"
                      value={form.decision}
                      onChange={(event) => {
                        updateForm(
                          "decision",
                          event.target.value,
                        );
                      }}
                      placeholder="Should we launch an AI-powered insurance claims platform in India?"
                      className="min-h-32 w-full resize-y rounded-2xl border border-white/10 bg-black/25 p-4 text-white outline-none transition focus:border-cyan-300/50 focus:ring-4 focus:ring-cyan-400/10"
                    />
                  </div>

                  <div>
                    <label
                      htmlFor="case-context"
                      className="mb-2 block text-xs font-semibold uppercase tracking-[0.14em] text-slate-500"
                    >
                      Context and constraints
                    </label>

                    <textarea
                      id="case-context"
                      value={form.context}
                      onChange={(event) => {
                        updateForm(
                          "context",
                          event.target.value,
                        );
                      }}
                      placeholder="Budget, geography, deadline, objectives and assumptions..."
                      className="min-h-28 w-full resize-y rounded-2xl border border-white/10 bg-black/25 p-4 text-white outline-none transition focus:border-cyan-300/50 focus:ring-4 focus:ring-cyan-400/10"
                    />
                  </div>

                  <motion.button
                    type="submit"
                    whileHover={{
                      scale: 1.02,
                      boxShadow:
                        "0 0 38px rgba(34,211,238,.30)",
                    }}
                    whileTap={{ scale: 0.98 }}
                    disabled={
                      creatingCase
                      || form.title.trim().length < 3
                      || form.decision.trim().length < 10
                    }
                    className="flex w-full items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-cyan-300 to-violet-300 p-4 font-black text-slate-950 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {creatingCase ? (
                      <Loader2
                        className="animate-spin"
                        size={19}
                      />
                    ) : (
                      <Sparkles size={19} />
                    )}

                    {creatingCase
                      ? "Opening War Room"
                      : "Open War Room"}
                  </motion.button>
                </form>
              </GlassCard>

              <div className="space-y-6">
                <GlassCard>
                  <SectionTitle
                    icon={Network}
                    eyebrow="Agent network"
                    title="Execution flow"
                  />

                  <AgentFlow running={false} />
                </GlassCard>

                <GlassCard>
                  <SectionTitle
                    icon={Zap}
                    eyebrow="System"
                    title="Mission control"
                  />

                  <div className="grid gap-3 sm:grid-cols-2">
                    {FEATURES.map(
                      ({
                        Icon,
                        label,
                        description,
                      }) => (
                        <motion.div
                          key={label}
                          whileHover={{
                            scale: 1.025,
                            y: -3,
                          }}
                          className="rounded-2xl border border-white/10 bg-white/[0.03] p-4 transition hover:border-cyan-300/25"
                        >
                          <Icon className="text-cyan-200" />

                          <p className="mt-3 font-semibold text-white">
                            {label}
                          </p>

                          <p className="mt-1 text-xs leading-5 text-slate-500">
                            {description}
                          </p>
                        </motion.div>
                      ),
                    )}
                  </div>
                </GlassCard>
              </div>
            </div>
          ) : (
            <>
              <div className="mb-6 flex gap-2 overflow-x-auto pb-1">
                {TABS.map(
                  ({ key, label, Icon }) => (
                    <motion.button
                      type="button"
                      whileHover={{ y: -2 }}
                      whileTap={{ scale: 0.96 }}
                      onClick={() => {
                        setActiveTab(key);
                      }}
                      key={key}
                      className={cx(
                        "flex shrink-0 items-center gap-2 rounded-2xl border px-4 py-2.5 text-sm font-semibold transition",
                        activeTab === key
                          ? "border-cyan-300/30 bg-cyan-300/10 text-cyan-100"
                          : "border-white/10 bg-white/[0.025] text-slate-500 hover:border-white/20 hover:text-white",
                      )}
                    >
                      <Icon size={16} />
                      {label}
                    </motion.button>
                  ),
                )}
              </div>

              <AnimatePresence mode="wait">
                {activeTab === "command" && (
                  <motion.div
                    key="command"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="grid gap-6 xl:grid-cols-[.75fr_1.25fr]"
                  >
                    <GlassCard>
                      <SectionTitle
                        icon={Network}
                        eyebrow="Execution"
                        title="Agent map"
                      />

                      <AgentFlow
                        plan={investigationPlan}
                        orchestration={orchestration}
                        running={orchestrating}
                      />
                    </GlassCard>

                    <CommitteePanel
                      data={orchestration?.committee}
                      loading={orchestrating}
                    />
                  </motion.div>
                )}

                {activeTab === "research" && (
                  <motion.div
                    key="research"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="grid gap-6 xl:grid-cols-2"
                  >
                    <ResearchPanel
                      data={orchestration?.research}
                      loading={orchestrating}
                    />

                    <EvidencePanel
                      data={orchestration?.evidence}
                    />
                  </motion.div>
                )}

                {activeTab === "risk" && (
                  <motion.div
                    key="risk"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                  >
                    <RedTeamPanel
                      data={orchestration?.red_team}
                      loading={orchestrating}
                    />
                  </motion.div>
                )}

                {activeTab === "decision" && (
                  <motion.div
                    key="decision"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                  >
                    <CommitteePanel
                      data={orchestration?.committee}
                      loading={orchestrating}
                    />
                  </motion.div>
                )}

                {activeTab === "audit" && (
                  <motion.div
                    key="audit"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                  >
                    <AuditPanel
                      events={auditEvents}
                    />
                  </motion.div>
                )}
              </AnimatePresence>
            </>
          )}
        </main>
      </div>
    </div>
  );
}
