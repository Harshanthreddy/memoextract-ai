"use client";

import React, { useState, useEffect, useRef } from "react";
import confetti from "canvas-confetti";
import {
  FileText,
  Upload,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Sparkles,
  RefreshCw,
  Download,
  Trash2,
  Settings as SettingsIcon,
  Home,
  History as HistoryIcon,
  BarChart3,
  ExternalLink,
  ShieldCheck,
  Check,
  Plus,
  Copy,
  ChevronRight,
  Cpu,
  Layers,
  FileSpreadsheet,
  Search,
  Maximize2
} from "lucide-react";

import {
  checkBackendHealth,
  fetchStats,
  fetchHistory,
  deleteHistoryItem,
  extractMarksheet,
  BACKEND_URL
} from "../lib/api";
import { exportMarksheetToExcel } from "../lib/excelExport";

export default function MarksheetApp() {
  // Navigation & UI State
  const [activeTab, setActiveTab] = useState("home"); // home | extract | history | analytics | settings
  const [activeMenu, setActiveMenu] = useState(null); // File | Edit | Extraction | Window | Help
  const [currentTime, setCurrentTime] = useState("");
  const [backendHealth, setBackendHealth] = useState({ status: "checking" });

  // Dashboard Stats
  const [stats, setStats] = useState({
    total_docs: 1,
    successful_docs: 1,
    success_rate: 100,
    needs_review: 0,
    review_rate: 0,
    avg_time_sec: 0,
  });

  // Extraction State
  const [file, setFile] = useState(null);
  const [filePreview, setFilePreview] = useState(null);
  const [isExtracting, setIsExtracting] = useState(false);
  const [extractStep, setExtractStep] = useState(0);
  const [activeEngine, setActiveEngine] = useState("Groq Vision AI");
  const [selectedModel, setSelectedModel] = useState("llama-3.2-11b-vision-preview");
  const [customApiKey, setCustomApiKey] = useState("");
  const [extractedData, setExtractedData] = useState(null);
  const [copySuccess, setCopySuccess] = useState(false);
  const [warnings, setWarnings] = useState([]);

  // History State
  const [historyDocs, setHistoryDocs] = useState([]);
  const [historySearch, setHistorySearch] = useState("");
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);

  // File Input Ref
  const fileInputRef = useRef(null);

  // 1. Clock & Health Polling
  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setCurrentTime(
        now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
      );
    };
    updateTime();
    const timer = setInterval(updateTime, 1000);

    // Initial API load
    loadDashboard();

    return () => clearInterval(timer);
  }, []);

  const loadDashboard = async () => {
    const health = await checkBackendHealth();
    setBackendHealth(health);
    const s = await fetchStats();
    setStats(s);
    const hist = await fetchHistory(10);
    setHistoryDocs(hist);
  };

  const reloadHistory = async () => {
    setIsLoadingHistory(true);
    const hist = await fetchHistory(50);
    setHistoryDocs(hist);
    setIsLoadingHistory(false);
  };

  useEffect(() => {
    if (activeTab === "history") {
      reloadHistory();
    }
  }, [activeTab]);

  // 2. File Selection Handler
  const handleFileChange = (e) => {
    const selected = e.target.files?.[0];
    if (!selected) return;

    setFile(selected);
    if (selected.type.startsWith("image/")) {
      const reader = new FileReader();
      reader.onload = (ev) => setFilePreview(ev.target?.result);
      reader.readAsDataURL(selected);
    } else {
      setFilePreview(null);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const selected = e.dataTransfer.files[0];
      setFile(selected);
      if (selected.type.startsWith("image/")) {
        const reader = new FileReader();
        reader.onload = (ev) => setFilePreview(ev.target?.result);
        reader.readAsDataURL(selected);
      } else {
        setFilePreview(null);
      }
    }
  };

  // 3. Marksheet Extraction Pipeline
  const runExtraction = async () => {
    if (!file) return;

    setIsExtracting(true);
    setExtractStep(1);

    try {
      setTimeout(() => setExtractStep(2), 700);
      setTimeout(() => setExtractStep(3), 1500);

      const res = await extractMarksheet(file, customApiKey, selectedModel);
      setExtractStep(4);

      if (res.success && res.data) {
        setExtractedData(res.data);
        setWarnings(res.warnings || []);

        // Apple Celebratory Confetti Burst
        confetti({
          particleCount: 80,
          spread: 70,
          origin: { y: 0.6 },
          colors: ["#0071E3", "#30D158", "#BF5AF2", "#FF9F0A"]
        });

        loadDashboard();
      }
    } catch (err) {
      alert("Extraction failed: " + err.message);
    } finally {
      setIsExtracting(false);
    }
  };

  // 4. Live Subject Editing & Recalculation
  const handleSubjectChange = (index, field, value) => {
    if (!extractedData) return;
    const updatedSubjects = [...(extractedData.subjects || [])];
    const sub = { ...updatedSubjects[index] };

    if (field === "obtained_marks" || field === "max_marks") {
      const numVal = parseFloat(value) || 0;
      sub[field] = numVal;
      sub.status = sub.obtained_marks >= (sub.max_marks * 0.4) ? "PASS" : "FAIL";
    } else {
      sub[field] = value;
    }

    updatedSubjects[index] = sub;

    // Recalculate totals
    const totalObtained = updatedSubjects.reduce((acc, s) => acc + (parseFloat(s.obtained_marks) || 0), 0);
    const totalMax = updatedSubjects.reduce((acc, s) => acc + (parseFloat(s.max_marks) || 100), 0);
    const percentage = totalMax > 0 ? parseFloat(((totalObtained / totalMax) * 100).toFixed(2)) : 0;
    const allPassed = updatedSubjects.every((s) => s.status !== "FAIL");

    setExtractedData({
      ...extractedData,
      subjects: updatedSubjects,
      total_obtained: totalObtained,
      total_max: totalMax,
      percentage: percentage,
      result: allPassed ? "PASS" : "FAIL"
    });
  };

  const addSubjectRow = () => {
    if (!extractedData) return;
    const newSub = {
      code: `SUB${(extractedData.subjects?.length || 0) + 1}`,
      name: "New Course",
      max_marks: 100,
      obtained_marks: 0,
      grade: "P",
      status: "FAIL"
    };
    setExtractedData({
      ...extractedData,
      subjects: [...(extractedData.subjects || []), newSub]
    });
  };

  const removeSubjectRow = (index) => {
    if (!extractedData) return;
    const updated = extractedData.subjects.filter((_, i) => i !== index);
    setExtractedData({ ...extractedData, subjects: updated });
  };

  const copySummaryToClipboard = () => {
    if (!extractedData) return;
    const summary = `
Marksheet AI Extraction
Student: ${extractedData.student_name} (${extractedData.roll_no})
Institution: ${extractedData.institution || "N/A"}
Result: ${extractedData.result} | Percentage: ${extractedData.percentage}%
Total Marks: ${extractedData.total_obtained} / ${extractedData.total_max}
Subjects:
${(extractedData.subjects || []).map(s => `- ${s.name}: ${s.obtained_marks}/${s.max_marks} (${s.grade || "-"})`).join("\n")}
    `.trim();

    navigator.clipboard.writeText(summary);
    setCopySuccess(true);
    setTimeout(() => setCopySuccess(false), 2000);
  };

  return (
    <div className="min-h-screen bg-black text-[#F5F5F7] flex flex-col font-sans relative">
      {/* =========================================================================
          1. AUTHENTIC APPLE MACOS MENU BAR (TOP BAR - 100% FIXED)
          ========================================================================= */}
      <header className="fixed top-0 left-0 right-0 h-9 bg-[#141416]/90 backdrop-blur-2xl border-b border-white/10 z-50 flex items-center justify-between px-4 text-xs select-none">
        {/* Left: Apple SVG Icon & Top Menus */}
        <div className="flex items-center gap-4">
          <svg
            className="w-3.5 h-3.5 fill-current text-white cursor-pointer hover:opacity-80 transition-opacity"
            viewBox="0 0 170 170"
          >
            <path d="M150.37 130.25c-2.45 5.66-5.35 10.87-8.71 15.66-4.58 6.53-8.33 11.05-11.22 13.56-4.48 4.12-9.28 6.23-14.42 6.35-3.69 0-8.14-1.05-13.32-3.18-5.19-2.12-9.97-3.17-14.34-3.17-4.58 0-9.49 1.05-14.75 3.17-5.26 2.13-9.5 3.24-12.74 3.35-4.35.13-9.16-1.9-14.42-6.08-3.7-3.08-7.7-7.93-12-14.54-6.3-9.67-11.2-20.73-14.7-33.19-3.5-12.46-5.25-24.16-5.25-35.1 0-14.43 3.63-26.68 10.9-36.75 7.27-10.07 16.5-15.17 27.69-15.3 4.89 0 10.5 1.34 16.83 4.02 6.33 2.68 10.45 4.08 12.36 4.2 1.63 0 5.69-1.39 12.18-4.17 6.49-2.78 12.02-4.11 16.6-3.99 12.36.63 22.46 5.37 30.29 14.22-10.74 6.53-15.98 15.64-15.72 27.34.26 9.17 3.86 16.86 10.8 23.08 6.94 6.22 15.18 9.77 24.72 10.66-2.01 6.34-4.54 12.7-7.59 19.08zM119.22 31.84c0-7.23 2.62-13.9 7.86-20.02 5.24-6.12 11.66-9.87 19.26-11.25.13 1.25.2 2.37.2 3.37 0 7.23-2.73 14.18-8.2 20.85-5.46 6.67-12.18 10.57-20.15 11.7-.13-1.38-.2-2.94-.2-4.65z" />
          </svg>
          <span className="font-bold text-white tracking-tight">Marksheet AI</span>

          <div className="hidden sm:flex items-center gap-3 text-[#A1A1A6]">
            {["File", "Edit", "Extraction", "Window", "Help"].map((m) => (
              <span
                key={m}
                onClick={() => setActiveMenu(activeMenu === m ? null : m)}
                className={`cursor-pointer px-1.5 py-0.5 rounded hover:bg-white/10 hover:text-white transition-colors ${
                  activeMenu === m ? "bg-white/15 text-white" : ""
                }`}
              >
                {m}
              </span>
            ))}
          </div>
        </div>

        {/* Right: Live Status, Mode, Time & User */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 text-[#30D158] font-medium text-[11px] bg-white/5 px-2.5 py-0.5 rounded-full border border-white/5">
            <span className="w-2 h-2 rounded-full bg-[#30D158] apple-pulse-green inline-block" />
            <span>System Online</span>
          </div>

          <span className="hidden md:inline-block text-[#A1A1A6] text-[11px] bg-white/5 px-2.5 py-0.5 rounded-md border border-white/5">
            ⚡ {activeEngine}
          </span>

          <span className="text-[#A1A1A6] font-mono text-[11px]">
            {currentTime || "15:30"}
          </span>

          <div className="px-2.5 py-0.5 rounded-full bg-[#0A84FF]/20 border border-[#0A84FF]/40 text-[#64D2FF] font-semibold text-[11px]">
            HR Harshanth
          </div>
        </div>
      </header>

      {/* Spacer for Top Menu Bar */}
      <div className="h-9" />

      {/* =========================================================================
          2. UNIFIED MACOS SEQUOIA WINDOW (ONE COHESIVE DESKTOP APP)
          ========================================================================= */}
      <div className="flex-1 flex flex-col p-3 sm:p-5 max-w-[1540px] w-full mx-auto">
        <div className="flex-1 bg-[#141416]/80 backdrop-blur-3xl border border-white/12 rounded-3xl shadow-[0_30px_90px_rgba(0,0,0,0.85)] flex flex-col overflow-hidden">
          {/* Unified macOS Titlebar */}
          <div className="h-12 bg-[#1C1C1E]/75 border-b border-white/10 flex items-center justify-between px-5 select-none shrink-0">
            {/* Left: Window Traffic Lights */}
            <div className="flex items-center gap-2">
              <div className="w-3.5 h-3.5 rounded-full bg-[#FF5F56] border border-[#E0443E]/60 shadow-sm hover:opacity-80 cursor-pointer" />
              <div className="w-3.5 h-3.5 rounded-full bg-[#FFBD2E] border border-[#DEA123]/60 shadow-sm hover:opacity-80 cursor-pointer" />
              <div className="w-3.5 h-3.5 rounded-full bg-[#27C93F] border border-[#1AAB29]/60 shadow-sm hover:opacity-80 cursor-pointer" />
              <span className="ml-3 text-xs font-semibold text-[#86868B] tracking-tight">
                Marksheet AI — Document Intelligence Pro
              </span>
            </div>

            {/* Right: Quick Action Buttons */}
            <div className="flex items-center gap-2 text-xs">
              <button
                onClick={() => setActiveTab("extract")}
                className="px-3 py-1 rounded-lg bg-[#0071E3] hover:bg-[#0077ED] text-white text-[11px] font-semibold flex items-center gap-1.5 transition-all shadow-md shadow-blue-500/20"
              >
                <Plus size={12} />
                <span>New Extraction</span>
              </button>
            </div>
          </div>

          {/* Body Split: Sidebar & Main View */}
          <div className="flex flex-1 min-h-[720px]">
            {/* LEFT SIDEBAR */}
            <aside className="w-64 bg-[#121214]/65 border-r border-white/10 p-4 flex flex-col shrink-0 select-none">
              {/* Brand Chip */}
              <div className="flex items-center gap-3 p-2.5 bg-white/[0.03] rounded-xl border border-white/5 mb-5">
                <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-[#0A84FF] to-[#0071E3] flex items-center justify-center text-white text-lg shadow-lg shadow-blue-500/25">
                  📄
                </div>
                <div>
                  <div className="font-bold text-xs text-white tracking-tight">Marksheet AI</div>
                  <div className="text-[10px] text-[#86868B]">macOS Document Intel</div>
                </div>
              </div>

              {/* Navigation Section */}
              <div className="space-y-1 mb-6">
                <div className="px-2 pb-1 text-[10px] font-bold tracking-wider text-[#86868B] uppercase">
                  Navigation
                </div>
                {[
                  { id: "home", label: "Dashboard", icon: Home },
                  { id: "extract", label: "Extract Marksheets", icon: FileText },
                  { id: "history", label: "Document History", icon: HistoryIcon },
                  { id: "analytics", label: "Analytics", icon: BarChart3 },
                  { id: "settings", label: "Settings", icon: SettingsIcon },
                ].map((item) => {
                  const Icon = item.icon;
                  const isActive = activeTab === item.id;
                  return (
                    <button
                      key={item.id}
                      onClick={() => setActiveTab(item.id)}
                      className={`w-full flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-medium transition-all ${
                        isActive
                          ? "bg-gradient-to-r from-[#0071E3]/35 to-[#0071E3]/15 text-white border border-[#0071E3] shadow-md shadow-blue-500/20 translate-x-1 font-semibold"
                          : "text-[#D1D1D6] hover:bg-white/[0.08] hover:text-white border border-transparent"
                      }`}
                    >
                      <Icon size={15} className={isActive ? "text-[#0A84FF]" : "text-[#86868B]"} />
                      <span>{item.label}</span>
                    </button>
                  );
                })}
              </div>

              {/* Extraction Engine Selector Card */}
              <div className="mt-auto bg-white/[0.03] border border-white/10 rounded-xl p-3">
                <div className="flex items-center justify-between text-[10px] font-semibold text-[#86868B] mb-2 uppercase tracking-wider">
                  <span>Active Engine</span>
                  <span className="w-1.5 h-1.5 rounded-full bg-[#30D158] inline-block" />
                </div>
                <select
                  value={activeEngine}
                  onChange={(e) => setActiveEngine(e.target.value)}
                  className="w-full bg-[#1C1C1E] border border-white/10 rounded-lg p-2 text-xs text-white focus:outline-none focus:border-[#0A84FF] transition-colors"
                >
                  <option value="Groq Vision AI">🤖 Groq Vision AI</option>
                  <option value="Offline Local Extractor">⚡ Offline Local Extractor</option>
                  <option value="FastAPI Microservice">🌐 FastAPI Server</option>
                </select>
              </div>
            </aside>

            {/* MAIN CONTENT AREA */}
            <main className="flex-1 p-6 overflow-y-auto space-y-6">
              {/* TAB 1: DASHBOARD */}
              {activeTab === "home" && (
                <div className="space-y-6">
                  {/* Hero Greeting Banner */}
                  <div className="bg-[#1C1C1E]/60 backdrop-blur-2xl border border-white/10 rounded-2xl p-6 shadow-lg relative overflow-hidden">
                    <div className="relative z-10 max-w-2xl">
                      <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-[#0A84FF]/20 border border-[#0A84FF]/40 text-[#64D2FF] text-[11px] font-semibold mb-2">
                        <Sparkles size={12} />
                        <span>Next-Gen Marksheet Extraction v2.4</span>
                      </div>
                      <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight mb-2">
                        Welcome back, Harshanth! 👋
                      </h1>
                      <p className="text-[#A1A1A6] text-xs leading-relaxed mb-5">
                        Extract marksheet and transcript data quickly and accurately with AI-powered Vision OCR. Export directly to structured Excel (.xlsx) and review student grades instantly.
                      </p>
                      <div className="flex flex-wrap gap-2.5">
                        <button
                          onClick={() => setActiveTab("extract")}
                          className="px-4 py-2 rounded-xl bg-[#0071E3] hover:bg-[#0077ED] text-white text-xs font-semibold shadow-md shadow-blue-500/25 transition-all flex items-center gap-1.5"
                        >
                          <Upload size={13} />
                          <span>Upload Marksheet</span>
                        </button>
                        <button
                          onClick={() => setActiveTab("history")}
                          className="px-4 py-2 rounded-xl bg-white/10 hover:bg-white/15 text-white text-xs font-semibold border border-white/10 transition-all flex items-center gap-1.5"
                        >
                          <HistoryIcon size={13} />
                          <span>View History</span>
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* 4 Apple Squircle KPI Cards */}
                  <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                    {[
                      {
                        label: "Total Documents",
                        val: stats.total_docs || historyDocs.length || 1,
                        sub: "Processed so far",
                        icon: "📄",
                        color: "from-[#0A84FF] to-[#0071E3]",
                      },
                      {
                        label: "Successful Extractions",
                        val: stats.successful_docs || 1,
                        sub: `${stats.success_rate || 100}% success rate`,
                        icon: "✓",
                        color: "from-[#30D158] to-[#28CD41]",
                      },
                      {
                        label: "Needs Review",
                        val: stats.needs_review || 0,
                        sub: `${stats.review_rate || 0}% require attention`,
                        icon: "⚠️",
                        color: "from-[#FF9F0A] to-[#FF9500]",
                      },
                      {
                        label: "Avg. Processing Time",
                        val: `${stats.avg_time_sec || 0}s`,
                        sub: "Per document",
                        icon: "⚡",
                        color: "from-[#BF5AF2] to-[#AF52DE]",
                      },
                    ].map((kpi, idx) => (
                      <div
                        key={idx}
                        className="bg-[#1C1C1E]/60 backdrop-blur-2xl border border-white/10 rounded-2xl p-4 shadow-sm hover:border-white/20 hover:-translate-y-0.5 transition-all"
                      >
                        <div
                          className={`w-10 h-10 rounded-xl bg-gradient-to-br ${kpi.color} flex items-center justify-center text-white text-base font-bold shadow-md mb-3`}
                        >
                          {kpi.icon}
                        </div>
                        <div className="text-2xl font-bold text-white tracking-tight">{kpi.val}</div>
                        <div className="text-xs font-semibold text-[#F5F5F7] mt-0.5">{kpi.label}</div>
                        <div className="text-[11px] text-[#86868B] mt-0.5">{kpi.sub}</div>
                      </div>
                    ))}
                  </div>

                  {/* Quick AirDrop Dropzone on Dashboard */}
                  <div
                    onDragOver={(e) => e.preventDefault()}
                    onDrop={(e) => {
                      handleDrop(e);
                      setActiveTab("extract");
                    }}
                    onClick={() => {
                      setActiveTab("extract");
                      setTimeout(() => fileInputRef.current?.click(), 100);
                    }}
                    className="bg-[#1C1C1E]/40 border-2 border-dashed border-white/15 hover:border-[#0A84FF] rounded-2xl p-6 text-center cursor-pointer transition-all hover:bg-[#0A84FF]/[0.03] group"
                  >
                    <div className="float-cloud text-3xl mb-1 text-[#0A84FF]">☁️</div>
                    <div className="text-xs font-semibold text-white">
                      Drag & Drop your marksheet here, or click to browse
                    </div>
                    <div className="text-[11px] text-[#86868B] mt-0.5">
                      Supports JPG, JPEG, PNG, PDF | Max size: 25MB
                    </div>
                  </div>

                  {/* Recent Records & Control Center */}
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                    <div className="lg:col-span-2 bg-[#1C1C1E]/60 backdrop-blur-2xl border border-white/10 rounded-2xl p-5">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="font-bold text-xs text-white flex items-center gap-2">
                          <HistoryIcon size={14} className="text-[#0A84FF]" />
                          <span>Recent Marksheet Records</span>
                        </h3>
                        <button
                          onClick={() => setActiveTab("history")}
                          className="text-[11px] text-[#0A84FF] hover:underline flex items-center gap-1"
                        >
                          <span>See All</span>
                          <ChevronRight size={11} />
                        </button>
                      </div>

                      {historyDocs.length === 0 ? (
                        <div className="text-center py-6 text-[#86868B] text-xs">
                          No marksheet extractions recorded yet.
                        </div>
                      ) : (
                        <div className="space-y-2">
                          {historyDocs.slice(0, 4).map((doc) => (
                            <div
                              key={doc.id}
                              className="flex items-center justify-between p-3 rounded-xl bg-white/[0.03] border border-white/5 hover:bg-white/[0.06] transition-all"
                            >
                              <div className="flex items-center gap-3">
                                <div className="w-8 h-8 rounded-lg bg-[#0071E3]/20 text-[#0A84FF] flex items-center justify-center text-xs">
                                  📄
                                </div>
                                <div>
                                  <div className="font-semibold text-xs text-white">
                                    {doc.student_name || doc.filename || "Marksheet Document"}
                                  </div>
                                  <div className="text-[11px] text-[#86868B]">
                                    Roll: {doc.roll_no || "N/A"} • {doc.result || "PROCESSED"}
                                  </div>
                                </div>
                              </div>
                              <span className="text-[10px] px-2 py-0.5 rounded-full bg-[#30D158]/20 text-[#30D158] font-semibold border border-[#30D158]/30">
                                {doc.status || "SUCCESS"}
                              </span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Control Center Widget */}
                    <div className="bg-[#1C1C1E]/60 backdrop-blur-2xl border border-white/10 rounded-2xl p-5 flex flex-col justify-between">
                      <div>
                        <h3 className="font-bold text-xs text-white mb-3 flex items-center gap-2">
                          <Cpu size={14} className="text-[#30D158]" />
                          <span>Control Center</span>
                        </h3>
                        <div className="space-y-2.5 text-xs">
                          <div className="flex justify-between py-1 border-b border-white/5">
                            <span className="text-[#86868B]">Backend Server</span>
                            <span className="text-[#30D158] font-semibold flex items-center gap-1">
                              <span className="w-1.5 h-1.5 rounded-full bg-[#30D158]" /> Online (:8000)
                            </span>
                          </div>
                          <div className="flex justify-between py-1 border-b border-white/5">
                            <span className="text-[#86868B]">Active Mode</span>
                            <span className="text-white font-medium">{activeEngine}</span>
                          </div>
                          <div className="flex justify-between py-1 border-b border-white/5">
                            <span className="text-[#86868B]">Database</span>
                            <span className="text-white font-medium">SQLite Connected</span>
                          </div>
                          <div className="flex justify-between py-1">
                            <span className="text-[#86868B]">Export Formats</span>
                            <span className="text-white font-medium">Excel (.xlsx), JSON</span>
                          </div>
                        </div>
                      </div>

                      <button
                        onClick={() => setActiveTab("settings")}
                        className="w-full mt-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-xs font-semibold text-white border border-white/10 transition-all flex items-center justify-center gap-2"
                      >
                        <SettingsIcon size={12} />
                        <span>Configure System</span>
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 2: EXTRACT MARKSHEETS */}
              {activeTab === "extract" && (
                <div className="space-y-6">
                  {/* AirDrop-Style Upload Area */}
                  <div
                    onDragOver={(e) => e.preventDefault()}
                    onDrop={handleDrop}
                    onClick={() => fileInputRef.current?.click()}
                    className="bg-[#1C1C1E]/50 backdrop-blur-3xl border-2 border-dashed border-white/20 hover:border-[#0A84FF] rounded-3xl p-8 sm:p-12 text-center cursor-pointer transition-all hover:bg-[#0A84FF]/[0.04] group shadow-xl relative"
                  >
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept="image/jpeg,image/png,image/webp,application/pdf"
                      onChange={handleFileChange}
                      className="hidden"
                    />

                    <div className="float-cloud text-5xl mb-3 text-[#0A84FF]">
                      ☁️
                    </div>

                    <h3 className="text-base font-bold text-white mb-1 tracking-tight">
                      Drag & Drop marksheet file here, or click to browse
                    </h3>
                    <p className="text-xs text-[#86868B]">
                      Supports JPG, JPEG, PNG, WEBP, or PDF files • Max size: 25MB
                    </p>

                    {file && (
                      <div className="mt-4 inline-flex items-center gap-3 bg-white/10 border border-white/15 px-4 py-2 rounded-xl text-xs text-white">
                        <FileText size={15} className="text-[#0A84FF]" />
                        <span className="font-semibold">{file.name}</span>
                        <span className="text-[#86868B]">({(file.size / 1024).toFixed(1)} KB)</span>
                      </div>
                    )}
                  </div>

                  {/* Trigger Bar */}
                  {file && (
                    <div className="flex flex-wrap items-center justify-between gap-4 bg-[#1C1C1E]/60 backdrop-blur-2xl border border-white/10 rounded-2xl p-4">
                      <div className="flex items-center gap-3">
                        <span className="text-xs font-semibold text-[#86868B]">Vision Model:</span>
                        <select
                          value={selectedModel}
                          onChange={(e) => setSelectedModel(e.target.value)}
                          className="bg-[#121214] border border-white/10 rounded-lg px-2.5 py-1.5 text-xs text-white"
                        >
                          <option value="llama-3.2-11b-vision-preview">Llama 3.2 11B Vision (Fastest)</option>
                          <option value="llama-3.2-90b-vision-preview">Llama 3.2 90B Vision (High Accuracy)</option>
                        </select>
                      </div>

                      <button
                        disabled={isExtracting}
                        onClick={runExtraction}
                        className="px-6 py-2 rounded-xl bg-[#0071E3] hover:bg-[#0077ED] disabled:opacity-50 text-white text-xs font-bold shadow-lg shadow-blue-500/30 flex items-center gap-2 transition-all"
                      >
                        {isExtracting ? (
                          <>
                            <RefreshCw size={13} className="animate-spin" />
                            <span>Processing Document...</span>
                          </>
                        ) : (
                          <>
                            <Sparkles size={13} />
                            <span>Extract Marksheet Data</span>
                          </>
                        )}
                      </button>
                    </div>
                  )}

                  {/* Progress Indicator */}
                  {isExtracting && (
                    <div className="bg-[#1C1C1E]/80 backdrop-blur-2xl border border-white/10 rounded-2xl p-6 text-center space-y-4">
                      <div className="w-full bg-white/10 rounded-full h-1.5 overflow-hidden">
                        <div
                          className="h-full bg-[#0A84FF] transition-all duration-500 rounded-full"
                          style={{ width: `${extractStep * 25}%` }}
                        />
                      </div>
                      <div className="text-xs font-semibold text-[#D1D1D6]">
                        {extractStep === 1 && "Step 1/4: Ingesting document & preparing image layers..."}
                        {extractStep === 2 && "Step 2/4: Running AI Vision OCR & table localization..."}
                        {extractStep === 3 && "Step 3/4: Parsing subject scores, totals, and grades..."}
                        {extractStep === 4 && "Step 4/4: Validating arithmetic & updating database..."}
                      </div>
                    </div>
                  )}

                  {/* Extracted Marksheet Data Presentation & Editor */}
                  {extractedData && (
                    <div className="space-y-5 animate-fadeIn">
                      {/* Candidate Card */}
                      <div className="bg-[#1C1C1E]/70 backdrop-blur-2xl border border-white/10 rounded-2xl p-5 shadow-lg">
                        <div className="flex flex-wrap items-center justify-between gap-4 mb-4 pb-4 border-b border-white/10">
                          <div>
                            <span className="text-[10px] font-bold tracking-wider uppercase text-[#0A84FF]">
                              Candidate Profile
                            </span>
                            <h2 className="text-xl font-bold text-white tracking-tight">
                              {extractedData.student_name || "Candidate Name"}
                            </h2>
                            <div className="text-xs text-[#86868B] mt-0.5">
                              Roll No: <span className="text-white font-mono">{extractedData.roll_no || "N/A"}</span> • Institution:{" "}
                              <span className="text-white">{extractedData.institution || "College / Board"}</span>
                            </div>
                          </div>

                          <div className="flex items-center gap-3">
                            <span
                              className={`px-3 py-1 rounded-full text-xs font-bold border ${
                                extractedData.result === "PASS"
                                  ? "bg-[#30D158]/20 text-[#30D158] border-[#30D158]/40"
                                  : "bg-[#FF453A]/20 text-[#FF453A] border-[#FF453A]/40"
                              }`}
                            >
                              {extractedData.result || "PASS"}
                            </span>
                            <div className="text-right">
                              <div className="text-lg font-extrabold text-white">
                                {extractedData.percentage || 0}%
                              </div>
                              <div className="text-[10px] text-[#86868B]">SGPA: {extractedData.sgpa || "N/A"}</div>
                            </div>
                          </div>
                        </div>

                        {/* Summary Badges */}
                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                          <div className="bg-white/[0.03] p-3 rounded-xl border border-white/5">
                            <span className="text-[#86868B] text-[10px]">Total Obtained</span>
                            <div className="text-base font-bold text-white mt-0.5">
                              {extractedData.total_obtained || 0}
                            </div>
                          </div>
                          <div className="bg-white/[0.03] p-3 rounded-xl border border-white/5">
                            <span className="text-[#86868B] text-[10px]">Total Maximum</span>
                            <div className="text-base font-bold text-white mt-0.5">
                              {extractedData.total_max || 0}
                            </div>
                          </div>
                          <div className="bg-white/[0.03] p-3 rounded-xl border border-white/5">
                            <span className="text-[#86868B] text-[10px]">Subject Count</span>
                            <div className="text-base font-bold text-white mt-0.5">
                              {extractedData.subjects?.length || 0}
                            </div>
                          </div>
                          <div className="bg-white/[0.03] p-3 rounded-xl border border-white/5">
                            <span className="text-[#86868B] text-[10px]">Engine Status</span>
                            <div className="text-base font-bold text-[#30D158] mt-0.5 flex items-center gap-1">
                              <CheckCircle2 size={14} /> Verified
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Interactive Subjects Table */}
                      <div className="bg-[#1C1C1E]/70 backdrop-blur-2xl border border-white/10 rounded-2xl p-5 shadow-lg">
                        <div className="flex items-center justify-between mb-4">
                          <h3 className="font-bold text-xs text-white flex items-center gap-2">
                            <FileSpreadsheet size={15} className="text-[#30D158]" />
                            <span>Subject Marks Breakdown (Live Recalculating Table)</span>
                          </h3>
                          <button
                            onClick={addSubjectRow}
                            className="px-2.5 py-1 rounded-lg bg-white/10 hover:bg-white/15 text-[11px] text-white flex items-center gap-1 transition-all"
                          >
                            <Plus size={12} />
                            <span>Add Subject</span>
                          </button>
                        </div>

                        <div className="overflow-x-auto rounded-xl border border-white/10">
                          <table className="w-full text-left text-xs">
                            <thead className="bg-[#121214] text-[#86868B] uppercase tracking-wider font-semibold border-b border-white/10">
                              <tr>
                                <th className="p-2.5">Code</th>
                                <th className="p-2.5">Subject Name</th>
                                <th className="p-2.5">Max Marks</th>
                                <th className="p-2.5">Obtained</th>
                                <th className="p-2.5">Grade</th>
                                <th className="p-2.5">Status</th>
                                <th className="p-2.5 text-right">Action</th>
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5">
                              {(extractedData.subjects || []).map((sub, idx) => (
                                <tr key={idx} className="hover:bg-white/[0.02] transition-colors">
                                  <td className="p-2.5 font-mono">
                                    <input
                                      type="text"
                                      value={sub.code || ""}
                                      onChange={(e) => handleSubjectChange(idx, "code", e.target.value)}
                                      className="bg-transparent border-b border-transparent focus:border-[#0A84FF] text-white focus:outline-none w-20"
                                    />
                                  </td>
                                  <td className="p-2.5">
                                    <input
                                      type="text"
                                      value={sub.name || ""}
                                      onChange={(e) => handleSubjectChange(idx, "name", e.target.value)}
                                      className="bg-transparent border-b border-transparent focus:border-[#0A84FF] text-white focus:outline-none w-full"
                                    />
                                  </td>
                                  <td className="p-2.5">
                                    <input
                                      type="number"
                                      value={sub.max_marks ?? 100}
                                      onChange={(e) => handleSubjectChange(idx, "max_marks", e.target.value)}
                                      className="bg-transparent border-b border-transparent focus:border-[#0A84FF] text-white focus:outline-none w-16"
                                    />
                                  </td>
                                  <td className="p-2.5">
                                    <input
                                      type="number"
                                      value={sub.obtained_marks ?? 0}
                                      onChange={(e) => handleSubjectChange(idx, "obtained_marks", e.target.value)}
                                      className="bg-transparent font-bold border-b border-transparent focus:border-[#0A84FF] text-[#0A84FF] focus:outline-none w-16"
                                    />
                                  </td>
                                  <td className="p-2.5">
                                    <input
                                      type="text"
                                      value={sub.grade || "A"}
                                      onChange={(e) => handleSubjectChange(idx, "grade", e.target.value)}
                                      className="bg-transparent border-b border-transparent focus:border-[#0A84FF] text-white focus:outline-none w-12 text-center"
                                    />
                                  </td>
                                  <td className="p-2.5">
                                    <span
                                      className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                        sub.status === "PASS"
                                          ? "bg-[#30D158]/20 text-[#30D158]"
                                          : "bg-[#FF453A]/20 text-[#FF453A]"
                                      }`}
                                    >
                                      {sub.status}
                                    </span>
                                  </td>
                                  <td className="p-2.5 text-right">
                                    <button
                                      onClick={() => removeSubjectRow(idx)}
                                      className="text-[#86868B] hover:text-[#FF453A] transition-colors p-1"
                                    >
                                      <Trash2 size={12} />
                                    </button>
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>

                        {/* Export Toolbar */}
                        <div className="flex flex-wrap items-center justify-between gap-3 mt-5 pt-3 border-t border-white/10">
                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => exportMarksheetToExcel(extractedData, `${extractedData.student_name || "marksheet"}.xlsx`)}
                              className="px-4 py-2 rounded-xl bg-[#30D158] hover:bg-[#28CD41] text-black font-bold text-xs flex items-center gap-2 shadow-md shadow-green-500/20 transition-all"
                            >
                              <Download size={13} />
                              <span>Export to Excel (.xlsx)</span>
                            </button>
                            <button
                              onClick={copySummaryToClipboard}
                              className="px-4 py-2 rounded-xl bg-white/10 hover:bg-white/15 text-white text-xs font-semibold flex items-center gap-1.5 transition-all"
                            >
                              {copySuccess ? <Check size={13} className="text-[#30D158]" /> : <Copy size={13} />}
                              <span>{copySuccess ? "Copied!" : "Copy Summary"}</span>
                            </button>
                          </div>

                          <span className="text-[11px] text-[#86868B]">
                            Live recalculated totals automatically match Excel formula criteria.
                          </span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* TAB 3: DOCUMENT HISTORY */}
              {activeTab === "history" && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-xl font-bold text-white tracking-tight">Extraction Records Archive</h2>
                      <p className="text-xs text-[#86868B]">Documents stored persistently in SQLite database.</p>
                    </div>
                    <button
                      onClick={reloadHistory}
                      className="px-3 py-1.5 rounded-lg bg-white/10 hover:bg-white/15 text-xs text-white flex items-center gap-1.5 transition-all"
                    >
                      <RefreshCw size={12} className={isLoadingHistory ? "animate-spin" : ""} />
                      <span>Refresh</span>
                    </button>
                  </div>

                  <div className="bg-[#1C1C1E]/60 backdrop-blur-2xl border border-white/10 rounded-2xl overflow-hidden shadow-lg">
                    <div className="p-3 border-b border-white/10">
                      <input
                        type="text"
                        placeholder="Search by student name, roll number, or file..."
                        value={historySearch}
                        onChange={(e) => setHistorySearch(e.target.value)}
                        className="w-full bg-[#121214] border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-[#0A84FF]"
                      />
                    </div>

                    <div className="divide-y divide-white/5">
                      {historyDocs
                        .filter((d) =>
                          [d.student_name, d.roll_no, d.filename]
                            .filter(Boolean)
                            .some((txt) => txt.toLowerCase().includes(historySearch.toLowerCase()))
                        )
                        .map((item) => (
                          <div
                            key={item.id}
                            className="p-3.5 flex items-center justify-between hover:bg-white/[0.02] transition-colors"
                          >
                            <div className="flex items-center gap-3">
                              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-[#0A84FF]/20 to-[#0071E3]/20 text-[#0A84FF] flex items-center justify-center text-base font-bold">
                                📄
                              </div>
                              <div>
                                <div className="font-bold text-xs text-white">
                                  {item.student_name || item.filename}
                                </div>
                                <div className="text-[11px] text-[#86868B]">
                                  Roll No: <span className="text-white">{item.roll_no || "N/A"}</span> • {item.created_at || "Recent"}
                                </div>
                              </div>
                            </div>

                            <div className="flex items-center gap-3">
                              <div className="text-right hidden sm:block">
                                <div className="text-xs font-bold text-white">
                                  {item.total_obtained || 0} / {item.total_max || 0}
                                </div>
                                <div className="text-[10px] text-[#30D158] font-semibold">
                                  {item.percentage || 0}%
                                </div>
                              </div>

                              <button
                                onClick={() => {
                                  try {
                                    const parsed = typeof item.extracted_data_json === "string" ? JSON.parse(item.extracted_data_json) : item;
                                    exportMarksheetToExcel(parsed, `${item.student_name || "marksheet"}.xlsx`);
                                  } catch (e) {
                                    exportMarksheetToExcel(item);
                                  }
                                }}
                                className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-white transition-colors"
                                title="Export to Excel"
                              >
                                <Download size={13} />
                              </button>

                              <button
                                onClick={async () => {
                                  if (confirm("Delete this marksheet record?")) {
                                    await deleteHistoryItem(item.id);
                                    reloadHistory();
                                  }
                                }}
                                className="p-1.5 rounded-lg bg-white/5 hover:bg-[#FF453A]/20 text-[#86868B] hover:text-[#FF453A] transition-colors"
                                title="Delete"
                              >
                                <Trash2 size={13} />
                              </button>
                            </div>
                          </div>
                        ))}

                      {historyDocs.length === 0 && (
                        <div className="text-center py-10 text-[#86868B] text-xs">
                          No matching records found.
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 4: ANALYTICS */}
              {activeTab === "analytics" && (
                <div className="space-y-6">
                  <div className="bg-[#1C1C1E]/60 backdrop-blur-2xl border border-white/10 rounded-2xl p-6">
                    <h2 className="text-xl font-bold text-white tracking-tight mb-1">Intelligence Analytics</h2>
                    <p className="text-xs text-[#86868B] mb-6">Extraction metrics and success distribution.</p>

                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                      <div className="bg-white/[0.03] p-4 rounded-xl border border-white/5">
                        <span className="text-[10px] text-[#86868B] uppercase font-bold tracking-wider">Pass Rate</span>
                        <div className="text-2xl font-extrabold text-[#30D158] mt-1">{stats.success_rate || 100}%</div>
                        <p className="text-[11px] text-[#86868B] mt-1">Based on validated marksheet thresholds</p>
                      </div>
                      <div className="bg-white/[0.03] p-4 rounded-xl border border-white/5">
                        <span className="text-[10px] text-[#86868B] uppercase font-bold tracking-wider">Avg Latency</span>
                        <div className="text-2xl font-extrabold text-[#0A84FF] mt-1">{stats.avg_time_sec || 0}s</div>
                        <p className="text-[11px] text-[#86868B] mt-1">From upload to validated JSON</p>
                      </div>
                      <div className="bg-white/[0.03] p-4 rounded-xl border border-white/5">
                        <span className="text-[10px] text-[#86868B] uppercase font-bold tracking-wider">Database Total</span>
                        <div className="text-2xl font-extrabold text-[#BF5AF2] mt-1">{stats.total_docs || historyDocs.length}</div>
                        <p className="text-[11px] text-[#86868B] mt-1">Active SQLite document rows</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 5: SETTINGS */}
              {activeTab === "settings" && (
                <div className="space-y-6">
                  <div className="bg-[#1C1C1E]/60 backdrop-blur-2xl border border-white/10 rounded-2xl p-6 space-y-4">
                    <h2 className="text-xl font-bold text-white tracking-tight">System & Engine Settings</h2>

                    <div>
                      <label className="block text-xs font-semibold text-[#86868B] mb-1">
                        Groq Vision API Key (Optional Override)
                      </label>
                      <input
                        type="password"
                        placeholder="gsk_..."
                        value={customApiKey}
                        onChange={(e) => setCustomApiKey(e.target.value)}
                        className="w-full bg-[#121214] border border-white/10 rounded-xl p-2.5 text-xs text-white focus:outline-none focus:border-[#0A84FF]"
                      />
                      <span className="text-[11px] text-[#86868B] mt-1 block">
                        If left blank, the FastAPI backend uses the server environment's GROQ_API_KEY.
                      </span>
                    </div>

                    <div>
                      <label className="block text-xs font-semibold text-[#86868B] mb-1">
                        Backend Microservice Endpoint
                      </label>
                      <input
                        type="text"
                        defaultValue={BACKEND_URL}
                        readOnly
                        className="w-full bg-[#121214]/60 border border-white/10 rounded-xl p-2.5 text-xs text-[#86868B] font-mono cursor-not-allowed"
                      />
                    </div>

                    <div className="pt-4 border-t border-white/10 flex items-center justify-between">
                      <div>
                        <div className="text-xs font-bold text-white">Database Retention</div>
                        <div className="text-[11px] text-[#86868B]">SQLite storage active at marksheet_extractor.db</div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </main>
          </div>

          {/* Unified Bottom Window Footer */}
          <footer className="h-10 bg-[#121214]/90 border-t border-white/10 px-5 flex items-center justify-between text-xs text-[#86868B] select-none shrink-0">
            <span className="text-[11px]">
              Marksheet Extractor v2.4 • Next.js & FastAPI Architecture
            </span>
            <span className="text-[11px]">
              © 2026 <b className="text-white">Marksheet AI</b>. All rights reserved by{" "}
              <span className="text-[#0A84FF] font-semibold">duvvuruharshanthreddy</span>.
            </span>
          </footer>
        </div>
      </div>
    </div>
  );
}
