import {
  useState,
} from "react";

import {
  AnimatePresence,
  motion,
} from "framer-motion";

import {
  Activity,
  ArrowRight,
  Check,
  CheckCircle2,
  ChevronDown,
  CircleDashed,
  FileSearch,
  Loader2,
  ShieldCheck,
  Siren,
  TriangleAlert,
  X,
  type LucideIcon,
} from "lucide-react";

import type {
  AuditEvent,
  CommitteeResult,
  EvidenceResult,
  InvestigationPlan,
  Orchestration,
  RedTeamResult,
  ResearchResult,
} from "../types";

import {
  Badge,
  GlassCard,
  SectionTitle,
  Skeleton,
  cx,
  safeArray,
  titleCase,
} from "./ui";


type AgentStep = {
  agent: string;
  title: string;
  purpose: string;
};


type EvidenceStatistic = {
  Icon: LucideIcon;
  label: string;
  value: number;
  tone: "emerald" | "amber" | "rose";
};


type AgentFlowProps = {
  plan?: InvestigationPlan;
  orchestration?: Orchestration;
  running: boolean;
};


type ResearchPanelProps = {
  data?: ResearchResult;
  loading: boolean;
};


type EvidencePanelProps = {
  data?: EvidenceResult;
};


type RedTeamPanelProps = {
  data?: RedTeamResult;
  loading: boolean;
};


type CommitteePanelProps = {
  data?: CommitteeResult;
  loading: boolean;
};


type AuditPanelProps = {
  events: AuditEvent[];
};


const FALLBACK_AGENTS: AgentStep[] = [
  {
    agent: "case_understanding",
    title: "Case Understanding",
    purpose:
      "Interpret the objective and constraints.",
  },
  {
    agent: "research_agent",
    title: "Research Strategy",
    purpose:
      "Map evidence requirements and missing inputs.",
  },
  {
    agent: "evidence_verifier",
    title: "Evidence Gate",
    purpose:
      "Validate evidence quality and provenance.",
  },
  {
    agent: "black_swan_red_team",
    title: "Black Swan Red Team",
    purpose:
      "Challenge assumptions with adversarial scenarios.",
  },
  {
    agent: "committee",
    title: "Decision Committee",
    purpose:
      "Prepare the conditional decision memo.",
  },
];


function getDecisionTone(
  decision: string,
): "emerald" | "amber" | "rose" | "cyan" {
  switch (decision.toUpperCase()) {
    case "PROCEED":
      return "emerald";

    case "REJECT":
      return "rose";

    case "DEFER":
      return "cyan";

    case "PROCEED_WITH_CONDITIONS":
    default:
      return "amber";
  }
}


export function AgentFlow({
  plan,
  orchestration,
  running,
}: AgentFlowProps) {
  const plannedAgents: AgentStep[] =
    plan?.investigation_steps?.length
      ? plan.investigation_steps.map(
          (step) => ({
            agent: step.agent,
            title: step.title,
            purpose: step.purpose,
          }),
        )
      : FALLBACK_AGENTS;

  const executedAgents = new Set(
    safeArray(
      orchestration?.executed_agents,
    ),
  );

  return (
    <div className="relative space-y-2">
      <div className="absolute bottom-6 left-[18px] top-6 w-px bg-gradient-to-b from-cyan-300/60 via-violet-400/30 to-transparent" />

      {plannedAgents.map(
        (agentStep, index) => {
          const completed =
            executedAgents.has(
              agentStep.agent,
            );

          const active =
            running
            && !completed
            && index
              === executedAgents.size;

          return (
            <motion.div
              key={`${agentStep.agent}-${index}`}
              initial={{
                opacity: 0,
                x: -12,
              }}
              animate={
                active
                  ? {
                      opacity: 1,
                      x: 0,
                      boxShadow: [
                        "0 0 0 rgba(34,211,238,0)",
                        "0 0 28px rgba(34,211,238,.25)",
                        "0 0 0 rgba(34,211,238,0)",
                      ],
                    }
                  : {
                      opacity: 1,
                      x: 0,
                    }
              }
              transition={
                active
                  ? {
                      opacity: {
                        duration: 0.25,
                      },
                      x: {
                        duration: 0.25,
                      },
                      boxShadow: {
                        repeat: Infinity,
                        duration: 1.8,
                      },
                    }
                  : {
                      delay: index * 0.04,
                    }
              }
              whileHover={{
                x: 5,
                scale: 1.01,
              }}
              className="relative flex gap-3 rounded-2xl border border-transparent p-2.5 transition-colors hover:border-white/10 hover:bg-white/[0.04]"
            >
              <div
                className={cx(
                  "relative z-10 grid h-9 w-9 shrink-0 place-items-center rounded-full border",
                  completed
                    ? "border-emerald-300/40 bg-emerald-400/15 text-emerald-200"
                    : active
                      ? "border-cyan-300/50 bg-cyan-400/15 text-cyan-100"
                      : "border-white/10 bg-slate-900 text-slate-600",
                )}
              >
                {completed
                  ? (
                    <Check size={16} />
                  )
                  : active
                    ? (
                      <Loader2
                        className="animate-spin"
                        size={16}
                      />
                    )
                    : (
                      <span className="text-xs font-bold">
                        {index + 1}
                      </span>
                    )}
              </div>

              <div className="min-w-0 pt-0.5">
                <div className="flex items-center gap-2">
                  <p className="truncate text-sm font-semibold text-slate-200">
                    {agentStep.title}
                  </p>

                  {active && (
                    <Badge
                      tone="cyan"
                      pulse
                    >
                      Running
                    </Badge>
                  )}

                  {completed && (
                    <Badge tone="emerald">
                      Complete
                    </Badge>
                  )}
                </div>

                <p className="mt-0.5 truncate text-xs text-slate-500">
                  {agentStep.purpose}
                </p>
              </div>
            </motion.div>
          );
        },
      )}
    </div>
  );
}


export function ResearchPanel({
  data,
  loading,
}: ResearchPanelProps) {
  if (loading) {
    return (
      <GlassCard>
        <SectionTitle
          icon={FileSearch}
          eyebrow="Research"
          title="Building evidence plan"
        />

        <div className="space-y-3">
          <Skeleton />
          <Skeleton />
          <Skeleton />
        </div>
      </GlassCard>
    );
  }

  const researchItems = safeArray(
    data?.research_plan,
  );

  return (
    <GlassCard>
      <SectionTitle
        icon={FileSearch}
        eyebrow="Research strategy"
        title="Evidence requirements"
        trailing={
          <Badge
            tone={
              data?.source_retrieval_performed
                ? "emerald"
                : "amber"
            }
          >
            {data?.source_retrieval_performed
              ? "Sources retrieved"
              : "Plan only"}
          </Badge>
        }
      />

      {researchItems.length === 0
        ? (
          <div className="rounded-2xl border border-white/10 bg-white/[0.025] p-5">
            <p className="text-sm text-slate-500">
              Run the War Room to
              generate research tasks
              and evidence requirements.
            </p>
          </div>
        )
        : (
          <div className="space-y-3">
            {researchItems.map(
              (item, index) => (
                <motion.article
                  key={
                    item.id
                    || `research-${index}`
                  }
                  whileHover={{
                    x: 6,
                    scale: 1.006,
                  }}
                  transition={{
                    type: "spring",
                    stiffness: 260,
                    damping: 22,
                  }}
                  className="rounded-2xl border border-white/10 bg-white/[0.03] p-4 transition-colors hover:border-cyan-300/25 hover:bg-cyan-300/[0.04]"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-cyan-300">
                        {item.id
                          || `RQ-${index + 1}`}
                      </p>

                      <p className="mt-1 text-sm font-semibold leading-6 text-slate-200">
                        {item.question}
                      </p>
                    </div>

                    <Badge
                      tone={
                        item.priority
                          === "CRITICAL"
                          ? "rose"
                          : item.priority
                            === "HIGH"
                            ? "amber"
                            : "cyan"
                      }
                    >
                      {item.priority
                        || "Medium"}
                    </Badge>
                  </div>

                  <div className="mt-3 flex flex-wrap gap-2">
                    {safeArray(
                      item.preferred_source_types,
                    ).map(
                      (sourceType) => (
                        <Badge
                          key={sourceType}
                        >
                          {sourceType}
                        </Badge>
                      ),
                    )}
                  </div>
                </motion.article>
              ),
            )}
          </div>
        )}
    </GlassCard>
  );
}


export function EvidencePanel({
  data,
}: EvidencePanelProps) {
  const statistics: EvidenceStatistic[] = [
    {
      Icon: CheckCircle2,
      label: "Verified",
      value:
        data?.verified_evidence_count
        ?? 0,
      tone: "emerald",
    },
    {
      Icon: CircleDashed,
      label: "Unverified",
      value:
        data?.unverified_evidence_count
        ?? 0,
      tone: "amber",
    },
    {
      Icon: X,
      label: "Rejected",
      value:
        data?.rejected_evidence_count
        ?? 0,
      tone: "rose",
    },
  ];

  const evidenceStatus =
    data?.status ?? "PENDING";

  return (
    <GlassCard>
      <SectionTitle
        icon={ShieldCheck}
        eyebrow="Evidence gate"
        title="Verification"
        trailing={
          <Badge
            tone={
              evidenceStatus === "PASS"
                ? "emerald"
                : "amber"
            }
            pulse
          >
            {evidenceStatus}
          </Badge>
        }
      />

      <div className="grid gap-3 sm:grid-cols-3">
        {statistics.map(
          ({
            Icon,
            label,
            value,
            tone,
          }) => (
            <motion.div
              key={label}
              whileHover={{
                scale: 1.04,
                y: -4,
              }}
              transition={{
                type: "spring",
                stiffness: 260,
                damping: 20,
              }}
              className="rounded-2xl border border-white/10 bg-white/[0.03] p-4 transition-colors hover:border-cyan-300/20 hover:bg-white/[0.055]"
            >
              <Icon
                size={17}
                className={
                  tone === "emerald"
                    ? "text-emerald-200"
                    : tone === "amber"
                      ? "text-amber-200"
                      : "text-rose-200"
                }
              />

              <p className="mt-3 text-xs text-slate-500">
                {label}
              </p>

              <strong className="text-xl text-white">
                {value}
              </strong>
            </motion.div>
          ),
        )}
      </div>

      <div className="mt-4 rounded-2xl border border-white/10 bg-white/[0.025] p-4">
        <p className="text-sm leading-6 text-slate-400">
          {data?.reason
            ?? (
              "No evidence result "
              + "is available yet."
            )}
        </p>
      </div>
    </GlassCard>
  );
}


export function RedTeamPanel({
  data,
  loading,
}: RedTeamPanelProps) {
  const [expandedIndex, setExpandedIndex] =
    useState(0);

  if (loading) {
    return (
      <GlassCard>
        <SectionTitle
          icon={Siren}
          eyebrow="Red Team"
          title="Generating attack chains"
        />

        <div className="space-y-3">
          <Skeleton />
          <Skeleton />
          <Skeleton />
        </div>
      </GlassCard>
    );
  }

  const scenarios = safeArray(
    data?.compound_scenarios,
  );

  return (
    <GlassCard>
      <SectionTitle
        icon={Siren}
        eyebrow="Adversarial review"
        title="Black Swan Red Team"
        trailing={
          <Badge tone="rose">
            Hypothetical
          </Badge>
        }
      />

      {scenarios.length === 0
        ? (
          <div className="rounded-2xl border border-white/10 bg-white/[0.025] p-5">
            <p className="text-sm text-slate-500">
              Run the War Room to
              generate case-specific
              adversarial scenarios.
            </p>
          </div>
        )
        : (
          <div className="space-y-3">
            {scenarios.map(
              (scenario, index) => {
                const expanded =
                  expandedIndex === index;

                const critical =
                  scenario.severity
                  === "CRITICAL";

                return (
                  <motion.article
                    key={
                      scenario.id
                      || `scenario-${index}`
                    }
                    animate={
                      critical
                        ? {
                            borderColor: [
                              "rgba(244,63,94,.18)",
                              "rgba(244,63,94,.60)",
                              "rgba(244,63,94,.18)",
                            ],
                          }
                        : undefined
                    }
                    transition={
                      critical
                        ? {
                            repeat: Infinity,
                            duration: 2.2,
                          }
                        : undefined
                    }
                    className="overflow-hidden rounded-2xl border border-white/10 bg-white/[0.025]"
                  >
                    <button
                      type="button"
                      onClick={
                        () => {
                          setExpandedIndex(
                            expanded
                              ? -1
                              : index,
                          );
                        }
                      }
                      className="flex w-full items-center justify-between gap-4 p-4 text-left transition-colors hover:bg-white/[0.05]"
                    >
                      <div className="min-w-0">
                        <div className="flex flex-wrap gap-2">
                          <Badge
                            tone={
                              critical
                                ? "rose"
                                : "amber"
                            }
                          >
                            {scenario.severity
                              || "HIGH"}
                          </Badge>

                          <Badge>
                            {scenario.likelihood
                              || "UNKNOWN"}
                          </Badge>
                        </div>

                        <p className="mt-2 truncate text-sm font-semibold text-white">
                          {scenario.risk_dimension
                            || scenario.challenge}
                        </p>
                      </div>

                      <ChevronDown
                        size={18}
                        className={cx(
                          "shrink-0 text-slate-500 transition-transform duration-300",
                          expanded
                            && "rotate-180",
                        )}
                      />
                    </button>

                    <AnimatePresence
                      initial={false}
                    >
                      {expanded && (
                        <motion.div
                          initial={{
                            height: 0,
                            opacity: 0,
                          }}
                          animate={{
                            height: "auto",
                            opacity: 1,
                          }}
                          exit={{
                            height: 0,
                            opacity: 0,
                          }}
                          transition={{
                            duration: 0.3,
                          }}
                        >
                          <div className="space-y-4 border-t border-white/10 p-4">
                            <div>
                              <p className="text-[10px] font-bold uppercase tracking-[0.15em] text-slate-500">
                                Challenge
                              </p>

                              <p className="mt-2 text-sm leading-6 text-slate-300">
                                {scenario.challenge}
                              </p>
                            </div>

                            <div>
                              <p className="text-[10px] font-bold uppercase tracking-[0.15em] text-slate-500">
                                Transmission path
                              </p>

                              <div className="mt-3 flex flex-wrap items-center gap-2">
                                {safeArray(
                                  scenario
                                    .transmission_path,
                                ).map(
                                  (
                                    pathStep,
                                    pathIndex,
                                  ) => (
                                    <div
                                      key={
                                        `${pathStep}-${pathIndex}`
                                      }
                                      className="contents"
                                    >
                                      <motion.span
                                        whileHover={{
                                          scale: 1.05,
                                        }}
                                        className="rounded-xl border border-white/10 bg-slate-900 px-3 py-2 text-xs text-slate-300"
                                      >
                                        {pathStep}
                                      </motion.span>

                                      {pathIndex
                                        < scenario
                                          .transmission_path
                                          .length - 1 && (
                                        <ArrowRight
                                          size={14}
                                          className="text-rose-300"
                                        />
                                      )}
                                    </div>
                                  ),
                                )}
                              </div>
                            </div>

                            <div>
                              <p className="text-[10px] font-bold uppercase tracking-[0.15em] text-slate-500">
                                Potential impact
                              </p>

                              <p className="mt-2 text-sm leading-6 text-rose-100">
                                {scenario.impact}
                              </p>
                            </div>
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </motion.article>
                );
              },
            )}
          </div>
        )}

      {data?.summary && (
        <div className="mt-4 rounded-2xl border border-white/10 bg-white/[0.025] p-4">
          <p className="text-sm leading-6 text-slate-400">
            {data.summary}
          </p>
        </div>
      )}
    </GlassCard>
  );
}


export function CommitteePanel({
  data,
  loading,
}: CommitteePanelProps) {
  if (loading) {
    return (
      <GlassCard>
        <SectionTitle
          icon={ShieldCheck}
          eyebrow="Committee"
          title="Preparing decision memo"
        />

        <div className="grid gap-4 lg:grid-cols-2">
          <Skeleton className="h-52" />

          <div className="space-y-3">
            <Skeleton />
            <Skeleton />
          </div>
        </div>
      </GlassCard>
    );
  }

  const decision =
    data?.decision ?? "PENDING";

  const conditions = safeArray(
    data?.conditions,
  );

  const unresolvedQuestions =
    safeArray(
      data?.unresolved_questions,
    );

  return (
    <motion.div
      initial={{
        opacity: 0,
        y: 32,
      }}
      animate={{
        opacity: 1,
        y: 0,
      }}
      transition={{
        type: "spring",
        stiffness: 180,
        damping: 23,
      }}
    >
      <GlassCard className="bg-gradient-to-br from-slate-950/85 to-cyan-950/20">
        <SectionTitle
          icon={ShieldCheck}
          eyebrow="Conditional decision memo"
          title="War Room Committee"
          trailing={
            <Badge
              tone={
                getDecisionTone(
                  decision,
                )
              }
              pulse
            >
              {decision}
            </Badge>
          }
        />

        <h2 className="text-3xl font-black text-white">
          {titleCase(decision)}
        </h2>

        <p className="mt-3 text-sm leading-7 text-slate-300">
          {data?.executive_summary
            ?? (
              "Run the War Room "
              + "to create a recommendation."
            )}
        </p>

        <div className="mt-5 flex items-center gap-2 rounded-2xl border border-amber-300/20 bg-amber-300/10 p-3 text-sm text-amber-100">
          <ShieldCheck
            size={17}
            className="shrink-0"
          />

          Human approval required
        </div>

        <div className="mt-6 grid gap-6 md:grid-cols-2">
          <div>
            <p className="mb-3 text-[10px] font-bold uppercase tracking-[0.16em] text-slate-500">
              Conditions
            </p>

            {conditions.length === 0
              ? (
                <p className="text-sm text-slate-600">
                  No conditions available.
                </p>
              )
              : (
                <ul className="space-y-2">
                  {conditions.map(
                    (condition) => (
                      <motion.li
                        key={condition}
                        whileHover={{
                          x: 4,
                        }}
                        className="flex gap-2 text-sm leading-5 text-slate-400"
                      >
                        <CheckCircle2
                          size={15}
                          className="mt-0.5 shrink-0 text-cyan-300"
                        />

                        {condition}
                      </motion.li>
                    ),
                  )}
                </ul>
              )}
          </div>

          <div>
            <p className="mb-3 text-[10px] font-bold uppercase tracking-[0.16em] text-slate-500">
              Unresolved questions
            </p>

            {unresolvedQuestions.length
              === 0
              ? (
                <p className="text-sm text-slate-600">
                  No unresolved questions.
                </p>
              )
              : (
                <ul className="space-y-2">
                  {unresolvedQuestions.map(
                    (question) => (
                      <motion.li
                        key={question}
                        whileHover={{
                          x: 4,
                        }}
                        className="flex gap-2 text-sm leading-5 text-slate-400"
                      >
                        <TriangleAlert
                          size={15}
                          className="mt-0.5 shrink-0 text-amber-300"
                        />

                        {question}
                      </motion.li>
                    ),
                  )}
                </ul>
              )}
          </div>
        </div>
      </GlassCard>
    </motion.div>
  );
}


export function AuditPanel({
  events,
}: AuditPanelProps) {
  return (
    <GlassCard>
      <SectionTitle
        icon={Activity}
        eyebrow="Observability"
        title="Agent audit trail"
        trailing={
          <Badge>
            {events.length} events
          </Badge>
        }
      />

      {events.length === 0
        ? (
          <div className="rounded-2xl border border-white/10 bg-white/[0.025] p-5">
            <p className="text-sm text-slate-500">
              No audit events are
              available yet.
            </p>
          </div>
        )
        : (
          <div className="relative space-y-3">
            <div className="absolute bottom-4 left-[15px] top-4 w-px bg-gradient-to-b from-cyan-300/40 to-transparent" />

            {events.map(
              (event, index) => (
                <motion.article
                  initial={{
                    opacity: 0,
                    x: 12,
                  }}
                  animate={{
                    opacity: 1,
                    x: 0,
                  }}
                  transition={{
                    delay: index * 0.04,
                  }}
                  whileHover={{
                    x: 5,
                  }}
                  key={
                    event.id
                    || `audit-${index}`
                  }
                  className="relative flex gap-4"
                >
                  <div className="relative z-10 grid h-8 w-8 shrink-0 place-items-center rounded-full border border-cyan-300/30 bg-slate-950 text-xs font-bold text-cyan-200">
                    {index + 1}
                  </div>

                  <div className="min-w-0 flex-1 rounded-2xl border border-white/10 bg-white/[0.03] p-4 transition-colors hover:border-cyan-300/20 hover:bg-white/[0.05]">
                    <div className="flex flex-wrap items-center gap-2">
                      <Badge>
                        {event.event_type}
                      </Badge>

                      <strong className="text-sm text-white">
                        {event.agent}
                      </strong>
                    </div>

                    <p className="mt-2 text-sm leading-6 text-slate-400">
                      {event.summary}
                    </p>

                    {event.created_at && (
                      <p className="mt-2 text-xs text-slate-600">
                        {new Date(
                          event.created_at,
                        ).toLocaleString(
                          "en-IN",
                        )}
                      </p>
                    )}
                  </div>
                </motion.article>
              ),
            )}
          </div>
        )}
    </GlassCard>
  );
}