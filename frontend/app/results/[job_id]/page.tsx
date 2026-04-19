"use client";

import { useEffect, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import toast from "react-hot-toast";
import {
  Loader2,
  CheckCircle2,
  Flame,
  LayoutDashboard,
  BrainCircuit,
  Target,
  Rocket,
  ChevronDown,
  RefreshCw,
  Settings2,
  Search,
} from "lucide-react";

/* ───────────────────────────────────────────────────────── */
/*  Types                                                    */
/* ───────────────────────────────────────────────────────── */
interface RiskData {
  high_risk_count: number;
  total_active: number;
  risk_pct: number;
  confidence: number;
  insight: string;
  has_model: boolean;
}

interface Cohort {
  characteristics: string;
  size: number;
  retention_rate: number;
}


interface Hypothesis {
  hypothesis: string;
  confidence: number;
  supported_by: string[];
}

interface ProblemSolution {
  priority: number;
  problem: { title: string; description: string; affected_segment: string; current_impact: string };
  solution: { title: string; description: string; framework_used: string; key_actions: string[] };
  retention_impact: {
    estimated_lift_percent: number;
    estimated_users_retained: number;
    estimated_revenue_impact: string;
    confidence: number;
    time_to_impact: string;
  };
  implementation_steps: { step: number; action: string; owner: string; timeline: string }[];
}

interface PhaseSummary {
  theme: string;
  goals: string[];
  expected_lift: string;
}

interface Playbook {
  title: string;
  executive_summary: {
    total_problems_identified: number;
    total_projected_retention_lift: string;
    estimated_timeline: string;
    estimated_budget: string;
    confidence_level: string;
  };
  problems_and_solutions: ProblemSolution[];
  "30_60_90_roadmap": {
    phase_1_30_days: PhaseSummary;
    phase_2_60_days: PhaseSummary;
    phase_3_90_days: PhaseSummary;
  };
}

/* ───────────────────────────────────────────────────────── */
/*  Survival curve helpers                                   */
/* ───────────────────────────────────────────────────────── */
function parseSurvivalCurve(curve: Record<string, number>): { time: number; survival: number }[] {
  return Object.entries(curve)
    .map(([k, v]) => ({ time: parseInt(k.replace(/\D/g, ""), 10), survival: v }))
    .filter((p) => !isNaN(p.time))
    .sort((a, b) => a.time - b.time);
}

function getChurnAtPeriod(points: { time: number; survival: number }[], period: number): number {
  if (points.length === 0) return 0;
  let entry = points[0];
  for (const p of points) {
    if (p.time <= period) entry = p;
    else break;
  }
  return Math.round((1 - entry.survival) * 1000) / 10;
}

/* ───────────────────────────────────────────────────────── */
/*  Progress Steps                                           */
/* ───────────────────────────────────────────────────────── */
const STEPS = [
  { key: "risk_ready", label: "Signal" },
  { key: "churn_profile_ready", label: "Patterns" },
  { key: "diagnosis_ready", label: "Diagnosis" },
  { key: "solution_ready", label: "Strategy" },
];

function ProgressSteps({ stagesData }: { stagesData: Record<string, any> }) {
  const completedCount = STEPS.filter((s) => stagesData[s.key]).length;
  return (
    <div className="flex items-center gap-1 text-xs font-mono">
      {STEPS.map((step, i) => {
        const done = !!stagesData[step.key];
        const active = !done && completedCount === i;
        return (
          <div key={step.key} className="flex items-center gap-1">
            {i > 0 && <span className={`w-6 h-px ${done ? "bg-emerald-500/60" : "bg-white/10"}`} />}
            <span
              className={`px-2 py-0.5 rounded-full transition-all duration-500 ${done
                  ? "bg-emerald-500/15 text-emerald-400"
                  : active
                    ? "bg-blue-500/15 text-blue-400 animate-pulse"
                    : "bg-white/5 text-white/25"
                }`}
            >
              {done ? "✓" : i + 1} {step.label}
            </span>
          </div>
        );
      })}
    </div>
  );
}

/* ───────────────────────────────────────────────────────── */
/*  Section Wrapper                                          */
/* ───────────────────────────────────────────────────────── */
function Section({
  icon,
  title,
  accentColor,
  children,
  visible,
}: {
  icon: React.ReactNode;
  title: string;
  accentColor: string;
  children: React.ReactNode;
  visible: boolean;
}) {
  return (
    <div
      className={`transition-all duration-700 ease-out ${visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4 pointer-events-none h-0 overflow-hidden"
        }`}
    >
      <div className="flex items-center gap-3 mb-5">
        <span className={accentColor}>{icon}</span>
        <h2 className="text-lg font-semibold tracking-tight">{title}</h2>
      </div>
      {children}
    </div>
  );
}

/* ───────────────────────────────────────────────────────── */
/*  Page                                                     */
/* ───────────────────────────────────────────────────────── */
export default function ResultsPage() {
  const params = useParams();
  const router = useRouter();
  const jobId = params.job_id as string;

  const [connectionStatus, setConnectionStatus] = useState<"connecting" | "connected" | "complete" | "error">("connecting");
  const [stagesData, setStagesData] = useState<Record<string, any>>({});
  const [isRerunning, setIsRerunning] = useState(false);
  const [expandedFix, setExpandedFix] = useState<number | null>(null);
  const [showDeep, setShowDeep] = useState(false);
  const [tenureSlider, setTenureSlider] = useState<number>(0);

  /* SSE streaming */
  const sseRef = useRef<EventSource | null>(null);
  useEffect(() => {
    if (!jobId) return;

    const saved = sessionStorage.getItem(`job_${jobId}`);
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setStagesData(parsed.stagesData || {});
        if (parsed.connectionStatus === "complete") {
          setConnectionStatus("complete");
          return;
        }
      } catch { }
    }

    const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const sse = new EventSource(`${API_BASE}/analyze/stream/${jobId}`);
    sseRef.current = sse;

    sse.onopen = () => setConnectionStatus("connected");

    sse.onmessage = (e) => {
      try {
        const event = JSON.parse(e.data);
        setStagesData((prev) => {
          const updated = { ...prev, [event.type]: event.data };
          sessionStorage.setItem(
            `job_${jobId}`,
            JSON.stringify({ stagesData: updated, connectionStatus: event.type === "complete" ? "complete" : "connected" })
          );
          return updated;
        });
        if (event.type === "complete") {
          setConnectionStatus("complete");
          sse.close();
          sseRef.current = null;
        }
      } catch (err) {
        console.error("SSE parse error:", err);
      }
    };

    sse.onerror = () => {
      sse.close();
      sseRef.current = null;
      setConnectionStatus("error");
    };

    return () => {
      sse.close();
      sseRef.current = null;
    };
  }, [jobId]);

  /* Init tenure slider to max_tenure when churn profile arrives */
  useEffect(() => {
    const max = stagesData.churn_profile_ready?.max_tenure;
    if (max && tenureSlider === 0) setTenureSlider(max);
  }, [stagesData.churn_profile_ready]);

  /* Rerun */
  const handleRerun = async () => {
    const payloadStr = sessionStorage.getItem("latest_form_payload");
    if (!payloadStr) return toast.error("No previous form data found to rerun.");
    setIsRerunning(true);
    try {
      const res = await fetch("http://localhost:8000/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: payloadStr,
      });
      if (!res.ok) throw new Error();
      const data = await res.json();
      toast.success("Rerun started successfully!");
      router.push(`/results/${data.job_id}`);
    } catch {
      toast.error("Failed to rerun analysis.");
      setIsRerunning(false);
    }
  };

  /* Extracted data */
  const risk: RiskData | null = stagesData.risk_ready ?? null;
  const churnProfile = stagesData.churn_profile_ready ?? null;
  const cohorts: Cohort[] = churnProfile?.behavior_cohorts ?? [];
  const survivalPoints = parseSurvivalCurve(churnProfile?.survival_curve ?? {});
  const maxTenure = churnProfile?.max_tenure ?? 0;
  const sliderChurnPct = getChurnAtPeriod(survivalPoints, tenureSlider);
  const medianSurvival: number | null = churnProfile?.median_survival_time ?? null;
  const milestones: Record<string, number> = churnProfile?.milestone_retention ?? {};
  const hypotheses: Hypothesis[] = stagesData.diagnosis_ready?.merged_hypotheses ?? [];
  const playbook: Playbook | null = stagesData.solution_ready?.final_playbook ?? null;
  const problems: ProblemSolution[] = playbook?.problems_and_solutions?.slice(0, 2) ?? [];
  const roadmap = playbook?.["30_60_90_roadmap"];
  const exec = playbook?.executive_summary;

  return (
    <div className="min-h-screen bg-black text-[#fafafa] selection:bg-purple-500/30">
      <div className="max-w-[760px] mx-auto px-6 py-12 space-y-14">
        {/* ── Header ──────────────────────────────────────── */}
        <header className="space-y-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-semibold tracking-tight">Retention Intelligence</h1>
            <div className="flex items-center gap-2">
              <button
                onClick={() => router.push("/form")}
                className="flex items-center gap-2 bg-white/[.04] hover:bg-white/[.08] border border-white/[.06] text-sm px-4 py-2 rounded-lg font-medium transition-colors"
              >
                <Settings2 className="w-3.5 h-3.5" />
                Refine Context
              </button>
              <button
                onClick={handleRerun}
                disabled={isRerunning}
                className="flex items-center gap-2 bg-white/[.07] hover:bg-white/[.12] border border-white/[.08] text-sm px-4 py-2 rounded-lg font-medium transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
              >
                {isRerunning ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <RefreshCw className="w-3.5 h-3.5" />}
                {isRerunning ? "Rerunning…" : "Rerun"}
              </button>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3 text-xs text-[#71717a]">
              <span className="font-mono">{jobId.split("-")[0]}</span>
              <span>•</span>
              <span className="flex items-center gap-1.5">
                {connectionStatus === "connecting" && <><Loader2 className="w-3 h-3 animate-spin" /> Connecting</>}
                {connectionStatus === "connected" && <><div className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse" /> Analyzing</>}
                {connectionStatus === "complete" && <><CheckCircle2 className="w-3 h-3 text-emerald-500" /> Complete</>}
                {connectionStatus === "error" && <span className="text-red-400">Interrupted</span>}
              </span>
            </div>
            <ProgressSteps stagesData={stagesData} />
          </div>

          <div className="h-px bg-white/[.06]" />
        </header>

        {/* ── 1. Risk Overview ───────────────────────────── */}
        <Section
          icon={<Flame className="w-5 h-5" />}
          title="Risk Overview"
          accentColor="text-amber-400"
          visible={!!risk}
        >
          {risk && (
            <div className="space-y-4">
              {risk.has_model ? (
                <div className="grid grid-cols-3 gap-4">
                  <div className="p-4 rounded-xl bg-white/[.02] border border-white/[.06]">
                    <p className="text-[11px] uppercase tracking-widest text-[#71717a] mb-1">High Risk Users</p>
                    <p className="text-3xl font-bold text-amber-400">{risk.high_risk_count}</p>
                    <p className="text-xs text-[#52525b] mt-1">of {risk.total_active} active</p>
                  </div>
                  <div className="p-4 rounded-xl bg-white/[.02] border border-white/[.06]">
                    <p className="text-[11px] uppercase tracking-widest text-[#71717a] mb-1">At Risk</p>
                    <p className="text-3xl font-bold text-amber-400">{risk.risk_pct}%</p>
                    <p className="text-xs text-[#52525b] mt-1">of user base</p>
                  </div>
                  <div className="p-4 rounded-xl bg-white/[.02] border border-white/[.06]">
                    <p className="text-[11px] uppercase tracking-widest text-[#71717a] mb-1">Confidence</p>
                    <p className="text-3xl font-bold text-white">{risk.confidence}%</p>
                    <p className="text-xs text-[#52525b] mt-1">model accuracy</p>
                  </div>
                </div>
              ) : (
                <div className="p-4 rounded-xl bg-white/[.02] border border-white/[.06] text-sm text-[#a1a1aa]">
                  Predictive risk modeling requires churn and tenure columns in your dataset.
                </div>
              )}
              <p className="text-sm text-[#a1a1aa] border-l-2 border-amber-500/30 pl-3">{risk.insight}</p>
            </div>
          )}
        </Section>

        {/* ── 2. Churn Profile ───────────────────────────── */}
        <Section
          icon={<LayoutDashboard className="w-5 h-5" />}
          title="Churn Profile"
          accentColor="text-blue-400"
          visible={!!churnProfile}
        >
          <div className="space-y-4">
            {/* Main Probability Card */}
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
              <div className="p-4 rounded-xl bg-blue-500/[.03] border border-blue-500/10 sm:col-span-2 flex flex-col justify-between gap-4">
                <div>
                  <p className="text-[10px] uppercase tracking-widest text-blue-400 font-semibold mb-2">Churn Probability</p>
                  <div className="flex items-end gap-2">
                    <p className="text-4xl font-bold">{sliderChurnPct}%</p>
                    <p className="text-sm text-[#71717a] mb-1">by month {tenureSlider}</p>
                  </div>
                </div>
                {maxTenure > 0 && (
                  <div className="space-y-1">
                    <input
                      type="range"
                      min={1}
                      max={maxTenure}
                      value={tenureSlider}
                      onChange={(e) => setTenureSlider(Number(e.target.value))}
                      className="w-full accent-blue-500 cursor-pointer"
                    />
                    <div className="flex justify-between text-[10px] text-[#52525b]">
                      <span>Month 1</span>
                      <span>Month {maxTenure}</span>
                    </div>
                  </div>
                )}
              </div>

              {/* Median Survival */}
              <div className="p-4 rounded-xl bg-white/[.02] border border-white/[.06] sm:col-span-2 flex flex-col justify-between">
                <p className="text-[10px] uppercase tracking-widest text-[#71717a] mb-3">Median Survival</p>
                {medianSurvival ? (
                  <>
                    <p className="text-4xl font-bold">Mo. {medianSurvival}</p>
                    <p className="text-xs text-[#52525b] mt-4 italic">
                      Half of your users churn by month {medianSurvival}.
                    </p>
                  </>
                ) : (
                  <p className="text-xs text-[#52525b]">More than 50% of users are still active at end of observation.</p>
                )}
              </div>
            </div>

            {/* Milestone Retention Strip */}
            {Object.keys(milestones).length > 0 && (
              <div className="grid grid-cols-3 sm:grid-cols-6 gap-2">
                {Object.entries(milestones).map(([key, val]) => {
                  const month = parseInt(key.replace("month_", ""));
                  const pct = Math.round(val * 100);
                  const color = pct >= 80 ? "text-emerald-400" : pct >= 60 ? "text-yellow-400" : "text-red-400";
                  return (
                    <div key={key} className="p-3 rounded-lg bg-white/[.02] border border-white/[.06] text-center">
                      <p className="text-[10px] text-[#52525b] mb-1">Mo. {month}</p>
                      <p className={`text-sm font-semibold ${color}`}>{pct}%</p>
                    </div>
                  );
                })}
              </div>
            )}

            {/* Cohorts Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {cohorts.slice(0, 3).map((cohort, i) => (
                <div
                  key={i}
                  className="p-4 rounded-xl bg-white/[.02] border border-white/[.06] flex flex-col justify-between"
                >
                  <div>
                    <p className="text-[10px] uppercase tracking-widest text-[#71717a] mb-2">
                      {cohort.characteristics}
                    </p>
                    <p className="text-xl font-semibold">{cohort.size} users</p>
                  </div>
                  <div className="mt-4 flex items-center justify-between border-t border-white/[.04] pt-2">
                    <span className="text-[10px] text-[#52525b] uppercase">Retention</span>
                    <span className="text-sm font-semibold text-emerald-400">
                      {cohort.retention_rate ? `${Math.round(cohort.retention_rate * 100)}%` : "N/A"}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </Section>

        {/* ── 3. Root Cause ──────────────────────────────── */}
        <Section
          icon={<BrainCircuit className="w-5 h-5" />}
          title="Root Cause"
          accentColor="text-purple-400"
          visible={hypotheses.length > 0}
        >
          <div className="space-y-2">
            {hypotheses.slice(0, 3).map((h, i) => (
              <div
                key={i}
                className="flex items-center justify-between p-4 rounded-xl bg-white/[.02] border border-white/[.06] hover:border-white/[.12] transition-colors group"
              >
                <div className="flex items-center gap-3">
                  <span className="w-6 h-6 rounded-full bg-purple-500/15 text-purple-400 text-xs font-bold flex items-center justify-center flex-shrink-0">
                    {i + 1}
                  </span>
                  <span className="font-medium text-[15px]">{h.hypothesis}</span>
                </div>
                <span className="text-sm font-mono text-purple-400 flex-shrink-0 ml-4">
                  {(h.confidence * 100).toFixed(0)}%
                </span>
              </div>
            ))}
          </div>
        </Section>

        {/* ── 3. What to Fix First ───────────────────────── */}
        <Section
          icon={<Target className="w-5 h-5" />}
          title="What to Fix First"
          accentColor="text-emerald-400"
          visible={problems.length > 0}
        >
          <div className="space-y-3">
            {problems.map((ps, i) => {
              const isPrimary = i === 0;
              const isExpanded = expandedFix === i;
              return (
                <div
                  key={i}
                  className={`rounded-xl border transition-all ${isPrimary
                      ? "bg-emerald-500/[.04] border-emerald-500/20"
                      : "bg-white/[.02] border-white/[.06]"
                    }`}
                >
                  <div className={`p-5 ${isPrimary ? "" : "p-4"}`}>
                    {isPrimary && (
                      <span className="text-[10px] uppercase tracking-widest text-emerald-400 font-semibold mb-2 block">
                        Priority Fix
                      </span>
                    )}
                    <h4 className={`font-semibold mb-3 ${isPrimary ? "text-[17px]" : "text-[15px] text-[#d4d4d8]"}`}>
                      {ps.problem.title}
                    </h4>

                    <div className={`grid gap-3 text-sm ${isPrimary ? "grid-cols-2 sm:grid-cols-4" : "grid-cols-2 sm:grid-cols-4"}`}>
                      <div>
                        <p className="text-[11px] text-[#71717a] uppercase tracking-wider">Lift</p>
                        <p className={`font-semibold ${isPrimary ? "text-emerald-400" : "text-[#d4d4d8]"}`}>
                          +{ps.retention_impact.estimated_lift_percent}%
                        </p>
                      </div>
                      <div>
                        <p className="text-[11px] text-[#71717a] uppercase tracking-wider">Revenue</p>
                        <p className="font-semibold">{ps.retention_impact.estimated_revenue_impact}</p>
                      </div>
                      <div>
                        <p className="text-[11px] text-[#71717a] uppercase tracking-wider">Timeline</p>
                        <p className="font-semibold">{ps.retention_impact.time_to_impact}</p>
                      </div>
                      <div>
                        <p className="text-[11px] text-[#71717a] uppercase tracking-wider">Confidence</p>
                        <p className="font-semibold">{(ps.retention_impact.confidence * 100).toFixed(0)}%</p>
                      </div>
                    </div>

                    {/* Expand actions */}
                    <button
                      onClick={() => setExpandedFix(isExpanded ? null : i)}
                      className="mt-4 flex items-center gap-1.5 text-xs text-[#71717a] hover:text-white transition-colors"
                    >
                      <ChevronDown className={`w-3.5 h-3.5 transition-transform ${isExpanded ? "rotate-180" : ""}`} />
                      {isExpanded ? "Hide actions" : "View actions"}
                    </button>
                  </div>

                  {isExpanded && (
                    <div className="px-5 pb-5 border-t border-white/[.06] pt-4">
                      <ul className="space-y-2">
                        {ps.solution.key_actions.slice(0, 3).map((action, idx) => (
                          <li key={idx} className="flex items-start gap-2 text-sm text-[#d4d4d8]">
                            <span className="text-emerald-500 mt-1 flex-shrink-0">→</span>
                            {action}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </Section>

        {/* ── 4. Execution Plan ──────────────────────────── */}
        <Section
          icon={<Rocket className="w-5 h-5" />}
          title="Execution Plan"
          accentColor="text-blue-400"
          visible={!!roadmap}
        >
          {roadmap && exec && (
            <div className="space-y-4">
              {/* Total projected lift */}
              <div className="flex items-center justify-between p-4 rounded-xl bg-blue-500/[.06] border border-blue-500/15">
                <span className="text-sm text-blue-300">Total Projected Lift</span>
                <span className="text-xl font-bold text-blue-300">{exec.total_projected_retention_lift}</span>
              </div>

              {/* 30-60-90 grid */}
              <div className="grid grid-cols-3 gap-3">
                {[
                  { phase: roadmap.phase_1_30_days, label: "30 Days" },
                  { phase: roadmap.phase_2_60_days, label: "60 Days" },
                  { phase: roadmap.phase_3_90_days, label: "90 Days" },
                ].map(({ phase, label }, i) => (
                  <div key={i} className="p-4 rounded-xl bg-white/[.02] border border-white/[.06] space-y-3">
                    <h5 className="font-semibold text-sm">{label}</h5>
                    <ul className="space-y-1.5">
                      {phase.goals?.slice(0, 2).map((g: string, idx: number) => (
                        <li key={idx} className="text-xs text-[#a1a1aa] flex items-start gap-1.5">
                          <span className="text-blue-400 mt-0.5 flex-shrink-0">•</span>
                          {g}
                        </li>
                      ))}
                    </ul>
                    <p className="text-xs font-mono text-blue-400 pt-1 border-t border-white/[.04]">
                      → {phase.expected_lift} lift
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </Section>

        {/* ── 5. Deep Execution ──────────────────────────── */}
        {problems.length > 0 && (
          <div className={`transition-all duration-700 ${playbook ? "opacity-100" : "opacity-0"}`}>
            <button
              onClick={() => setShowDeep(!showDeep)}
              className="flex items-center gap-2 text-sm text-[#71717a] hover:text-white transition-colors"
            >
              <Search className="w-4 h-4" />
              {showDeep ? "Hide detailed plan" : "View detailed plan"}
              <ChevronDown className={`w-3.5 h-3.5 transition-transform ${showDeep ? "rotate-180" : ""}`} />
            </button>

            {showDeep && (
              <div className="mt-5 space-y-6">
                {problems.map((ps, i) => (
                  <div key={i} className="space-y-3">
                    <h4 className="text-sm font-semibold text-[#d4d4d8]">{ps.problem.title}</h4>
                    <div className="rounded-xl border border-white/[.06] overflow-hidden">
                      <table className="w-full text-xs">
                        <thead>
                          <tr className="bg-white/[.03] text-[#71717a] uppercase tracking-wider">
                            <th className="text-left p-3 font-medium">#</th>
                            <th className="text-left p-3 font-medium">Action</th>
                            <th className="text-left p-3 font-medium">Timeline</th>
                          </tr>
                        </thead>
                        <tbody>
                          {ps.implementation_steps.map((step, idx) => (
                            <tr key={idx} className="border-t border-white/[.04] hover:bg-white/[.02]">
                              <td className="p-3 text-[#71717a] font-mono">{step.step}</td>
                              <td className="p-3 text-[#d4d4d8]">{step.action}</td>
                              <td className="p-3 text-[#a1a1aa]">{step.timeline}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ── Loading state ──────────────────────────────── */}
        {connectionStatus === "connecting" && (
          <div className="flex items-center justify-center py-20 text-[#71717a]">
            <Loader2 className="w-5 h-5 animate-spin mr-3" />
            <span className="text-sm">Connecting to analysis pipeline…</span>
          </div>
        )}

        {connectionStatus === "connected" && !risk && (
          <div className="flex items-center justify-center py-20 text-[#71717a]">
            <Loader2 className="w-5 h-5 animate-spin mr-3" />
            <span className="text-sm">Processing your data…</span>
          </div>
        )}
      </div>
    </div>
  );
}