import React from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Sparkles, ArrowRight, Zap, RefreshCw, BarChart, Calendar, LayoutDashboard } from "lucide-react";
import { ModeToggle } from "@/components/mode-toggle";

export default function Landing() {
  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 font-sans text-slate-900 dark:text-slate-50 flex flex-col">
      {/* Navbar */}
      <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 h-14 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-indigo-600 dark:text-indigo-400" />
            <span className="font-bold text-lg">PostCraft AI ✦</span>
          </div>
          <nav className="hidden md:flex gap-6 text-sm font-medium">
            <a href="#features" className="hover:text-indigo-600 transition-colors">Features</a>
            <a href="#how-it-works" className="hover:text-indigo-600 transition-colors">How It Works</a>
            <a href="#pricing" className="hover:text-indigo-600 transition-colors">Pricing</a>
          </nav>
          <div className="flex items-center gap-4">
            <ModeToggle />
            <Link to="/login" className="text-sm font-medium hover:underline underline-offset-4">Login</Link>
            <Link to="/dashboard">
              <Button size="sm" className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-full px-5">Get Started</Button>
            </Link>
          </div>
        </div>
      </header>

      <main className="flex-1">
        {/* Hero Section */}
        <section className="py-24 md:py-32 lg:py-40 bg-gradient-to-b from-indigo-50/50 to-white dark:from-slate-900 dark:to-slate-950 px-4 text-center">
          <div className="container mx-auto max-w-4xl flex flex-col items-center">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-300 text-sm font-medium mb-8">
              <Zap className="h-4 w-4" />
              <span>Version 2.0 is now live</span>
            </div>
            
            <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-6 bg-clip-text text-transparent bg-gradient-to-r from-indigo-600 to-purple-600">
              Your Content.<br />Every Platform.<br />Powered by AI.
            </h1>
            
            <p className="text-lg md:text-xl text-slate-600 dark:text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed">
              Turn one idea, project, video, or achievement into engaging social content for LinkedIn, Instagram and X — in seconds.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto justify-center">
              <Link to="/dashboard">
                <Button size="lg" className="w-full sm:w-auto bg-indigo-600 hover:bg-indigo-700 text-white rounded-full text-base font-semibold px-8 h-12 flex items-center gap-2">
                  Start Creating Free <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
              <Button size="lg" variant="outline" className="w-full sm:w-auto rounded-full text-base font-semibold px-8 h-12">
                See How It Works
              </Button>
            </div>
            
            {/* Hero Visual Mockup */}
            <div className="mt-20 relative w-full max-w-5xl mx-auto">
              <div className="absolute inset-0 bg-gradient-to-t from-white dark:from-slate-950 z-10 h-full w-full pointer-events-none" style={{ background: 'linear-gradient(to top, var(--background) 0%, transparent 50%)' }}></div>
              <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white/50 dark:bg-slate-900/50 backdrop-blur-sm p-4 shadow-2xl relative overflow-hidden flex flex-col md:flex-row gap-6">
                
                {/* Input Side */}
                <div className="flex-1 bg-slate-50 dark:bg-slate-800 rounded-lg p-6 border border-slate-100 dark:border-slate-700 shadow-inner text-left">
                  <div className="flex items-center gap-2 mb-4">
                    <div className="h-3 w-3 rounded-full bg-red-400"></div>
                    <div className="h-3 w-3 rounded-full bg-yellow-400"></div>
                    <div className="h-3 w-3 rounded-full bg-green-400"></div>
                    <span className="text-xs font-medium text-slate-500 ml-2">Raw Input</span>
                  </div>
                  <div className="font-mono text-sm text-slate-700 dark:text-slate-300">
                    <p>"I built a face recognition project using Python and OpenCV. It uses a custom trained model to detect students in a classroom."</p>
                  </div>
                </div>

                {/* Arrow */}
                <div className="hidden md:flex flex-col justify-center items-center">
                  <RefreshCw className="h-6 w-6 text-indigo-500 animate-spin-slow" style={{ animationDuration: '3s' }} />
                </div>

                {/* Output Side */}
                <div className="flex-1 grid grid-cols-2 gap-4">
                  <div className="bg-white dark:bg-slate-950 rounded-lg p-4 shadow-sm border border-slate-200 dark:border-slate-800 text-left">
                     <div className="text-xs font-bold text-blue-600 mb-2">in</div>
                     <p className="text-xs text-slate-600 dark:text-slate-400 line-clamp-3">🚀 Excited to share my latest project! Built a real-time face recognition system for classroom attendance using Python & OpenCV...</p>
                  </div>
                  <div className="bg-white dark:bg-slate-950 rounded-lg p-4 shadow-sm border border-slate-200 dark:border-slate-800 text-left">
                     <div className="text-xs font-bold text-pink-600 mb-2">Instagram</div>
                     <p className="text-xs text-slate-600 dark:text-slate-400 line-clamp-3">No more roll calls! ✋ Just finished building a custom face detection model. Check out how it works below 👇 #Python #MachineLearning...</p>
                  </div>
                </div>

              </div>
            </div>
          </div>
        </section>

        {/* Problem Section */}
        <section className="py-24 px-4 bg-white dark:bg-slate-950 text-center border-t border-slate-100 dark:border-slate-900">
          <div className="container mx-auto max-w-3xl">
            <h2 className="text-3xl md:text-4xl font-bold mb-6">Creating content shouldn't feel like another job.</h2>
            <div className="grid md:grid-cols-2 gap-8 text-left mt-12">
              <div className="space-y-4">
                <div className="flex items-center gap-3"><div className="h-1.5 w-1.5 rounded-full bg-red-500"></div><p className="text-slate-600 dark:text-slate-400">Juggling multiple platforms</p></div>
                <div className="flex items-center gap-3"><div className="h-1.5 w-1.5 rounded-full bg-red-500"></div><p className="text-slate-600 dark:text-slate-400">Not knowing what to post</p></div>
                <div className="flex items-center gap-3"><div className="h-1.5 w-1.5 rounded-full bg-red-500"></div><p className="text-slate-600 dark:text-slate-400">Hours spent writing</p></div>
              </div>
              <div className="space-y-4">
                <div className="flex items-center gap-3"><div className="h-1.5 w-1.5 rounded-full bg-red-500"></div><p className="text-slate-600 dark:text-slate-400">Endless hashtag research</p></div>
                <div className="flex items-center gap-3"><div className="h-1.5 w-1.5 rounded-full bg-red-500"></div><p className="text-slate-600 dark:text-slate-400">Posting-time uncertainty</p></div>
                <div className="flex items-center gap-3"><div className="h-1.5 w-1.5 rounded-full bg-red-500"></div><p className="text-slate-600 dark:text-slate-400">Analytics complexity</p></div>
              </div>
            </div>
            <div className="mt-12 inline-block rounded-xl bg-indigo-50 dark:bg-indigo-900/20 px-8 py-4">
              <p className="text-xl font-semibold text-indigo-700 dark:text-indigo-400">PostCraft AI solves them in one place.</p>
            </div>
          </div>
        </section>

        {/* Feature Section */}
        <section id="features" className="py-24 px-4 bg-slate-50 dark:bg-slate-900 border-t border-slate-100 dark:border-slate-800">
          <div className="container mx-auto max-w-6xl">
            <h2 className="text-3xl font-bold text-center mb-16">Everything you need to grow smarter</h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {[
                { icon: <Sparkles />, title: "AI Content Generator", desc: "Instantly create optimized posts for LinkedIn, Instagram, and X." },
                { icon: <RefreshCw />, title: "Content Repurposing", desc: "Turn blogs or videos into threads, scripts, and carousels." },
                { icon: <BarChart />, title: "Engagement Prediction", desc: "Know how your post will perform before you even hit publish." },
                { icon: <Calendar />, title: "Best Time to Post", desc: "AI predicts exactly when your audience is most active." },
                { icon: <LayoutDashboard />, title: "AI Content Calendar", desc: "Plan your whole week with personalized content pillars." },
              ].map((f, i) => (
                <div key={i} className="bg-white dark:bg-slate-950 p-6 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-800 hover:shadow-md transition-shadow">
                  <div className="h-12 w-12 rounded-lg bg-indigo-100 dark:bg-indigo-900/50 text-indigo-600 dark:text-indigo-400 flex items-center justify-center mb-4">
                    {f.icon}
                  </div>
                  <h3 className="font-semibold text-lg mb-2">{f.title}</h3>
                  <p className="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">{f.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>

      <footer className="py-8 text-center text-sm text-slate-500 border-t border-border bg-white dark:bg-slate-950">
        <p>© 2026 PostCraft AI. All rights reserved.</p>
      </footer>
    </div>
  );
}
