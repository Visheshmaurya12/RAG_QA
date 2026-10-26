import React, { useState, useRef, useCallback, useEffect } from 'react'

// ──────────────────────────────────────────────
// Icons
// ──────────────────────────────────────────────
const FileIcon = () => <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/></svg>
const UploadCloudIcon = () => <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242"/><path d="M12 12v9"/><path d="m16 16-4-4-4 4"/></svg>
const SettingsIcon = () => <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
const MenuIcon = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="4" x2="20" y1="12" y2="12"/><line x1="4" x2="20" y1="6" y2="6"/><line x1="4" x2="20" y1="18" y2="18"/></svg>
const CloseIcon = () => <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
const CopyIcon = () => <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>
const RefreshIcon = () => <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg>
const SendIcon = () => <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/></svg>
const DocumentIcon = () => <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/><line x1="16" x2="8" y1="13" y2="13"/><line x1="16" x2="8" y1="17" y2="17"/><line x1="10" x2="8" y1="9" y2="9"/></svg>
const MoreVerticalIcon = () => <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="1"/><circle cx="12" cy="5" r="1"/><circle cx="12" cy="19" r="1"/></svg>

// ──────────────────────────────────────────────
// Helpers
// ──────────────────────────────────────────────

function AnswerText({ text }) {
  if (!text) return null
  const parts = text.split(/(\[S\d+(?:,\s*S\d+)*\])/g)
  return (
    <div className="text-slate-800 leading-relaxed text-base whitespace-pre-wrap">
      {parts.map((part, i) => {
        const match = part.match(/^\[(.*)\]$/)
        if (match) {
          const labels = match[1].split(/,\s*/).map((s) => s.trim()).filter(Boolean)
          return (
            <span key={i} className="inline-flex items-center gap-1 mx-0.5">
              {labels.map((label) => (
                <a
                  key={label}
                  href={`#source-${label}`}
                  className="inline-flex items-center justify-center px-1.5 py-0.5 text-xs font-semibold bg-blue-50 text-blue-700 hover:bg-blue-100 hover:text-blue-800 rounded transition-colors cursor-pointer border border-blue-200"
                  title={`Jump to source ${label}`}
                >
                  {label}
                </a>
              ))}
            </span>
          )
        }
        return <span key={i}>{part}</span>
      })}
    </div>
  )
}

function SourceCard({ source }) {
  const pageRange =
    source.page_start != null && source.page_end != null
      ? source.page_start === source.page_end
        ? `Page ${source.page_start}`
        : `Pages ${source.page_start}–${source.page_end}`
      : source.page_start != null
        ? `Page ${source.page_start}`
        : source.page_end != null
          ? `Page ${source.page_end}`
          : null

  return (
    <div
      id={`source-${source.label}`}
      className="bg-white border border-slate-200 rounded-xl p-5 scroll-mt-24 shadow-sm hover:shadow-md transition-shadow duration-200"
    >
      <div className="flex items-start gap-4">
        {/* Label badge */}
        <span className="shrink-0 mt-0.5 inline-flex items-center px-2.5 py-1 rounded-md text-xs font-bold bg-blue-600 text-white shadow-sm">
          {source.label}
        </span>

        <div className="min-w-0 flex-1">
          {/* Filename + pages */}
          <div className="flex flex-wrap items-center gap-3 mb-3">
            <span className="text-sm font-semibold text-slate-900 truncate">
              {source.filename}
            </span>
            {pageRange && (
              <span className="text-xs font-medium text-slate-600 bg-slate-100 px-2.5 py-1 rounded-md border border-slate-200">
                {pageRange}
              </span>
            )}
          </div>

          {/* Passage excerpt */}
          {source.text && (
            <p className="text-sm text-slate-600 leading-relaxed border-l-2 border-blue-200 pl-4 py-1 italic bg-slate-50 rounded-r-md">
              "{source.text}"
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

// ──────────────────────────────────────────────
// Main App
// ──────────────────────────────────────────────

export default function App() {
  const [question, setQuestion] = useState('')
  const [lastSubmittedQuestion, setLastSubmittedQuestion] = useState('')
  const [result, setResult]   = useState(null)   
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState(null)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [copied, setCopied] = useState(false)
  
  // Real indexed document in the Chroma vector store
  const [documents] = useState([
    { id: '1', filename: 'RAG_NOTES.pdf', pages: 6, status: 'ready' },
  ])
  const [uploadNote, setUploadNote] = useState(null)
  
  const textareaRef = useRef(null)
  const fileInputRef = useRef(null)

  const handleSubmit = useCallback(async (e, overrideQuestion) => {
    if (e && e.preventDefault) e.preventDefault()
    const q = (overrideQuestion != null ? overrideQuestion : question).trim()
    if (!q || loading) return

    setLoading(true)
    setError(null)
    setResult(null)
    setCopied(false)
    setLastSubmittedQuestion(q)

    try {
      const res = await fetch('/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: q }),
      })

      if (!res.ok) {
        let errorDetail = `Server error ${res.status}`
        try {
          const data = await res.json()
          if (data && data.detail) {
            errorDetail = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail)
          }
        } catch {
          // not json
        }
        throw new Error(errorDetail)
      }

      const data = await res.json()
      setResult(data)
    } catch (err) {
      setError(err.message || 'Failed to connect to the backend server. Is it running?')
    } finally {
      setLoading(false)
    }
  }, [question, loading])

  const handleCopy = () => {
    if (result?.answer) {
      navigator.clipboard.writeText(result.answer)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  // Upload trigger prepared for future integration
  const handleUploadClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click()
    }
  }

  const handleFileChange = (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    setUploadNote(`Backend ingestion endpoint is not configured for "${file.name}" yet.`)
    setTimeout(() => setUploadNote(null), 5000)
    e.target.value = ''
  }

  const hasQuestion = question.trim().length > 0

  return (
    <div className="flex h-screen bg-[#F8FAFC] font-sans text-slate-900 overflow-hidden">
      
      {/* ── Mobile Sidebar Overlay ── */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-slate-900/50 z-20 lg:hidden transition-opacity"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* ── Sidebar ── */}
      <aside className={`
        fixed inset-y-0 left-0 z-30 w-72 bg-white border-r border-slate-200 transform transition-transform duration-300 ease-in-out flex flex-col
        lg:relative lg:translate-x-0
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="flex items-center justify-between h-16 px-6 border-b border-slate-200 shrink-0">
          <div className="flex items-center gap-2 text-blue-600 font-bold text-lg tracking-tight">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center shrink-0">
              <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
              </svg>
            </div>
            <span>Academic RAG</span>
          </div>
          <button className="lg:hidden text-slate-400 hover:text-slate-600" onClick={() => setSidebarOpen(false)}>
            <CloseIcon />
          </button>
        </div>

        <div className="p-4 flex-1 overflow-y-auto">
          <div className="mb-6">
            <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">Documents</h3>
            
            {/* Upload Area */}
            <div className="mb-4">
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileChange}
                accept=".pdf"
                className="hidden"
              />
              <button 
                type="button"
                onClick={handleUploadClick}
                className="w-full flex items-center justify-center gap-2 bg-white border-2 border-dashed border-slate-300 rounded-xl p-4 text-slate-600 hover:border-blue-500 hover:text-blue-600 hover:bg-blue-50 transition-all group"
              >
                <UploadCloudIcon />
                <span className="font-medium text-sm">+ Upload PDF</span>
              </button>
              {uploadNote && (
                <p className="mt-2 text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded-lg p-2 font-medium">
                  {uploadNote}
                </p>
              )}
            </div>

            {/* Document List */}
            <div className="space-y-2">
              {documents.map(doc => (
                <div key={doc.id} className="group flex items-center justify-between p-3 rounded-lg border border-slate-200 bg-white hover:border-blue-300 hover:shadow-sm transition-all cursor-default">
                  <div className="flex items-start gap-3 overflow-hidden">
                    <div className="mt-0.5 text-blue-500 shrink-0">
                      <FileIcon />
                    </div>
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-slate-800 truncate" title={doc.filename}>
                        {doc.filename}
                      </p>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-xs text-slate-500">{doc.pages} pages</span>
                        <span className="w-1 h-1 rounded-full bg-slate-300"></span>
                        <span className="flex items-center gap-1 text-xs font-medium text-green-600">
                          <span className="w-1.5 h-1.5 rounded-full bg-green-500"></span>
                          Ready
                        </span>
                      </div>
                    </div>
                  </div>
                  <button className="text-slate-400 hover:text-slate-700 opacity-0 group-hover:opacity-100 transition-opacity p-1">
                    <MoreVerticalIcon />
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
        
        <div className="p-4 border-t border-slate-200 bg-slate-50">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center text-slate-500 font-bold text-xs">
              U
            </div>
            <div className="text-sm font-medium text-slate-700">User Account</div>
          </div>
        </div>
      </aside>

      {/* ── Main Layout ── */}
      <div className="flex-1 flex flex-col min-w-0 h-screen">
        
        {/* ── Top Header ── */}
        <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-4 sm:px-6 shrink-0 z-10">
          <div className="flex items-center gap-3">
            <button 
              className="lg:hidden p-1.5 -ml-1.5 text-slate-500 hover:bg-slate-100 rounded-md"
              onClick={() => setSidebarOpen(true)}
            >
              <MenuIcon />
            </button>
            <div className="hidden sm:block">
              <h1 className="text-sm font-bold text-slate-900">Academic Question Answering System</h1>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 px-3 py-1 bg-green-50 rounded-full border border-green-100">
              <span className="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)] animate-pulse"></span>
              <span className="text-xs font-semibold text-green-700">System Ready</span>
            </div>
            <button className="text-slate-400 hover:text-slate-700 transition-colors">
              <SettingsIcon />
            </button>
          </div>
        </header>

        {/* ── Scrollable Content Area ── */}
        <main className="flex-1 overflow-y-auto p-4 sm:p-8">
          <div className="max-w-4xl mx-auto space-y-8">
            
            {/* Header / Intro */}
            <div className="text-center sm:text-left space-y-2">
              <h2 className="text-3xl font-bold text-slate-900 tracking-tight">Ask your academic documents</h2>
              <p className="text-slate-500 text-base">Get grounded answers with page-level citations based on your uploaded PDFs.</p>
            </div>

            {/* Input Area */}
            <section className="bg-white rounded-2xl shadow-sm border border-slate-200 p-2 focus-within:border-blue-400 focus-within:ring-4 focus-within:ring-blue-50 transition-all duration-200">
              <div className="flex items-center px-4 pt-3 pb-2 border-b border-slate-100 mb-2">
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider bg-slate-100 px-2 py-1 rounded-md">
                  Scope: All Documents
                </span>
              </div>
              
              <form onSubmit={handleSubmit} className="relative">
                <textarea
                  id="question-input"
                  ref={textareaRef}
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  onKeyDown={(e) => {
                    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                      e.preventDefault()
                      handleSubmit(e)
                    }
                  }}
                  placeholder="Ask a question about your documents..."
                  rows={3}
                  className="w-full bg-transparent px-4 py-2 text-base text-slate-800 placeholder-slate-400 resize-none focus:outline-none"
                  disabled={loading}
                />
                <div className="flex items-center justify-between px-4 pb-2 pt-2">
                  <div className="text-xs text-slate-400 hidden sm:flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 bg-slate-100 border border-slate-200 rounded text-slate-500 font-mono text-[10px]">Ctrl</kbd>
                    <span>+</span>
                    <kbd className="px-1.5 py-0.5 bg-slate-100 border border-slate-200 rounded text-slate-500 font-mono text-[10px]">Enter</kbd>
                    <span className="ml-1">to submit</span>
                  </div>
                  <div className="flex-1 sm:hidden"></div>
                  
                  <button
                    type="submit"
                    disabled={!hasQuestion || loading}
                    className="inline-flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 disabled:text-blue-50 text-white text-sm font-semibold rounded-xl transition-all shadow-sm disabled:shadow-none cursor-pointer disabled:cursor-not-allowed"
                  >
                    {loading ? (
                      <>
                        <svg className="animate-spin w-4 h-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"/>
                        </svg>
                        Searching
                      </>
                    ) : (
                      <>
                        Ask
                        <SendIcon />
                      </>
                    )}
                  </button>
                </div>
              </form>
            </section>

            {/* Error Message */}
            {error && (
              <div className="rounded-xl border border-red-200 bg-red-50 p-4 flex gap-3 items-start shadow-sm">
                <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5 text-red-500 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
                </svg>
                <div className="flex-1">
                  <h4 className="text-sm font-bold text-red-800">Failed to generate answer</h4>
                  <p className="text-sm text-red-600 mt-1">{error}</p>
                  <button
                    type="button"
                    onClick={() => handleSubmit(null, lastSubmittedQuestion || question)}
                    disabled={loading}
                    className="mt-3 inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-red-700 bg-red-100 hover:bg-red-200 rounded-lg transition-colors cursor-pointer disabled:opacity-50"
                  >
                    <RefreshIcon /> Retry Request
                  </button>
                </div>
              </div>
            )}

            {/* Loading Skeleton */}
            {loading && (
              <div className="space-y-6 animate-pulse">
                <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-4">
                  <div className="h-5 bg-slate-200 rounded-md w-1/4"></div>
                  <div className="space-y-3">
                    <div className="h-4 bg-slate-200 rounded w-full"></div>
                    <div className="h-4 bg-slate-200 rounded w-5/6"></div>
                    <div className="h-4 bg-slate-200 rounded w-4/6"></div>
                  </div>
                </div>
              </div>
            )}

            {/* Results Area */}
            {result && !loading && (
              <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                
                {/* Answer Section */}
                <section className="bg-white rounded-2xl border border-slate-200 shadow-md overflow-hidden">
                  <div className="px-6 py-4 border-b border-slate-100 bg-slate-50/50 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-6 h-6 rounded bg-blue-100 flex items-center justify-center text-blue-600">
                        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
                      </div>
                      <h3 className="text-sm font-bold uppercase tracking-wider text-slate-700">Answer</h3>
                    </div>
                    <div className="flex items-center gap-2">
                      <button 
                        onClick={handleCopy}
                        className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors cursor-pointer"
                      >
                        {copied ? (
                          <span className="text-green-600 flex items-center gap-1">Copied!</span>
                        ) : (
                          <><CopyIcon /> Copy</>
                        )}
                      </button>
                      <button 
                        onClick={() => handleSubmit(null, lastSubmittedQuestion || question)}
                        className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors cursor-pointer"
                      >
                        <RefreshIcon /> Regenerate
                      </button>
                    </div>
                  </div>
                  <div className="p-6 md:p-8">
                    <AnswerText text={result.answer} />
                  </div>
                </section>

                {/* Sources Section */}
                {result.sources && result.sources.length > 0 && (
                  <section className="space-y-4">
                    <div className="flex items-center gap-2 px-2">
                      <h3 className="text-sm font-bold uppercase tracking-wider text-slate-500">
                        Sources &amp; Citations
                      </h3>
                      <span className="bg-slate-200 text-slate-600 text-xs font-bold px-2 py-0.5 rounded-full">
                        {result.sources.length}
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-1 gap-4">
                      {result.sources.map((src) => (
                        <SourceCard key={src.label} source={src} />
                      ))}
                    </div>
                  </section>
                )}
              </div>
            )}

            {/* Empty State */}
            {!result && !loading && !error && (
              <div className="flex flex-col items-center justify-center py-20 px-4 text-center animate-in fade-in duration-700">
                <div className="w-24 h-24 mb-6 text-slate-200">
                  <DocumentIcon />
                </div>
                <h3 className="text-xl font-bold text-slate-700 mb-2">Ask your documents</h3>
                <p className="text-slate-500 max-w-md mx-auto">
                  Upload your research papers, articles, or reports, and ask questions to get AI-generated answers with exact citations.
                </p>
                <div className="mt-8 flex gap-3 text-sm">
                  <button
                    type="button"
                    onClick={() => {
                      setQuestion('What is RAG?')
                      handleSubmit(null, 'What is RAG?')
                    }}
                    className="bg-white border border-slate-200 text-slate-600 hover:border-blue-400 hover:text-blue-600 px-4 py-2 rounded-full shadow-sm transition-colors cursor-pointer"
                  >
                    What is RAG?
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setQuestion('What documents should I collect?')
                      handleSubmit(null, 'What documents should I collect?')
                    }}
                    className="bg-white border border-slate-200 text-slate-600 hover:border-blue-400 hover:text-blue-600 px-4 py-2 rounded-full shadow-sm hidden sm:block transition-colors cursor-pointer"
                  >
                    What documents should I collect?
                  </button>
                </div>
              </div>
            )}

          </div>
        </main>
      </div>
    </div>
  )
}
