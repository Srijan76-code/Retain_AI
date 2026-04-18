"use client";

import React from "react";
import Link from "next/link";
import { ArrowRight, Sparkles, Shield, Zap } from "lucide-react";


export default function HomePage() {
  return (
    <div className="min-h-screen w-full bg-black relative flex flex-col overflow-hidden">
      {/* ── Layer 1: Colored noise dots ── */}
      <div
        className="absolute inset-0 z-0"
        style={{
          background: "#000000",
          backgroundImage: `
       radial-gradient(circle at 25% 25%, #222222 0.5px, transparent 1px),
       radial-gradient(circle at 75% 75%, #111111 0.5px, transparent 1px)
          `,
          backgroundSize: "20px 20px, 30px 30px, 25px 25px",
          backgroundPosition: "0 0, 10px 10px, 15px 5px",
          maskImage:
            "radial-gradient(ellipse 90% 80% at 50% 45%, rgba(0,0,0,1) 0%, rgba(0,0,0,0.8) 40%, rgba(0,0,0,0.4) 65%, rgba(0,0,0,0.1) 85%, transparent 100%)",
          WebkitMaskImage:
            "radial-gradient(ellipse 90% 80% at 50% 45%, rgba(0,0,0,1) 0%, rgba(0,0,0,0.8) 40%, rgba(0,0,0,0.4) 65%, rgba(0,0,0,0.1) 85%, transparent 100%)",
        }}
      />

      {/* ── Layer 2: Soft center glow behind content ── */}
      <div
        className="absolute inset-0 z-[1] pointer-events-none"
        style={{
          background:
            "radial-gradient(ellipse 50% 45% at 50% 48%, rgba(255,255,255,0.04) 0%, rgba(255,255,255,0.02) 30%, transparent 70%)",
        }}
      />

      {/* ── Layer 3: Top edge light leak ── */}
      <div
        className="fixed top-0 left-0 right-0 h-[1px] z-[1] pointer-events-none"
        style={{
          background:
            "linear-gradient(90deg, transparent 15%, rgba(255,255,255,0.3) 35%, rgba(255,255,255,0.5) 50%, rgba(255,255,255,0.3) 65%, transparent 85%)",
        }}
      />

      {/* ── Layer 4: Orbital rings (retention metaphor) ── */}
      <div className="absolute inset-0 z-[1] pointer-events-none">
        {/* rings with radial mask — visible only near center */}
        <div
          style={{
            position: "absolute",
            inset: 0,
            maskImage:
              "radial-gradient(ellipse 55% 50% at 50% 48%, rgba(0,0,0,0.5) 0%, rgba(0,0,0,0.2) 50%, transparent 75%)",
            WebkitMaskImage:
              "radial-gradient(ellipse 55% 50% at 50% 48%, rgba(0,0,0,0.5) 0%, rgba(0,0,0,0.2) 50%, transparent 75%)",
          }}
        >
          <div className="orbit-ring orbit-1" />
          <div className="orbit-ring orbit-2" />
          <div className="orbit-ring orbit-3" />
          <div className="orbit-ring orbit-4" />

          {/* orbiting dots */}
          <div className="orbit-dot-track dot-track-1" />
          <div className="orbit-dot-track dot-track-2" />
          <div className="orbit-dot-track dot-track-3" />
          <div className="orbit-dot-track dot-track-5" />
        </div>

        {/* center core */}
        <div className="retain-core" />
      </div>

      {/* ── Navbar ── */}
      <header className="relative z-10 flex items-center justify-between px-8 h-16 max-w-7xl mx-auto w-full">
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-[24px] h-[24px] rounded-[6px] bg-[#fafafa] flex items-center justify-center">
            <span
              className="text-[12px] font-bold text-[#09090b] leading-none"
              style={{ fontFamily: "var(--font-raleway)" }}
            >
              R
            </span>
          </div>
          <span
            className="text-[17px] font-semibold text-[#fafafa] tracking-[-0.02em] group-hover:opacity-80 transition-opacity"
            style={{ fontFamily: "var(--font-raleway)" }}
          >
            Retain AI
          </span>
        </Link>
      </header>

      {/* ── Hero Content ── */}
      <main className="relative z-10 flex-1 flex items-center justify-center px-8">
        <div className="max-w-3xl text-center">
          {/* pill */}
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.04)] backdrop-blur-md mb-8">
            <Sparkles className="w-3.5 h-3.5 text-[#a1a1aa]" />
            <span className="text-[12px] text-[#a1a1aa] tracking-wide">
              AI-Powered Retention Intelligence
            </span>
          </div>

          {/* headline */}
          <h1
            className="text-[56px] md:text-[72px] font-bold text-[#fafafa] leading-[1.05] tracking-[-0.035em] mb-6"
            style={{ fontFamily: "var(--font-raleway)" }}
          >
            Stop the churn.
            <br />
            <span className="bg-gradient-to-b from-[#71717a] to-[#3f3f46] bg-clip-text text-transparent">
              Start retaining.
            </span>
          </h1>

          <p className="text-[18px] text-[#71717a] leading-[1.7] mb-10 max-w-xl mx-auto">
            Upload your data, answer a few questions, and get actionable
            retention strategies powered by AI. Takes ~4 minutes.
          </p>

          {/* CTA */}
          <Link
            href="/form"
            className="inline-flex items-center gap-2.5 h-12 px-8 rounded-xl bg-[#fafafa] text-[#09090b] text-[15px] font-semibold hover:bg-white transition-all duration-200 shadow-[0_0_40px_rgba(255,255,255,0.06)]"
          >
            Get Started
            <ArrowRight className="w-4.5 h-4.5" />
          </Link>

          {/* trust signals */}
          <div className="flex items-center justify-center gap-8 mt-14">
            {[
              { icon: Shield, text: "Your data stays private" },
              { icon: Zap, text: "Results in minutes" },
              { icon: Sparkles, text: "AI-driven insights" },
            ].map(({ icon: Icon, text }) => (
              <div
                key={text}
                className="flex items-center gap-2 text-[12px] text-[#52525b]"
              >
                <Icon className="w-3.5 h-3.5" />
                {text}
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}