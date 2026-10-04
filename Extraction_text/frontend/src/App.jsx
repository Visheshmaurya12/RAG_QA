import { useState, useRef, useCallback } from 'react'

// ──────────────────────────────────────────────
// Helpers
// ──────────────────────────────────────────────

/**
 * Renders answer text and wraps every [Sn] citation with a styled badge.
 * Clicking a badge scrolls to the corresponding source card.
 */
function AnswerText({ text }) {
  const parts = text.split(/(\[S\d+\])/g)
  return (
    <p className="text-slate-700 leading-relaxed text-base whitespace-pre-wrap">
      {parts.map((part, i) => {
        const match = part.match(/^\[(S\d+)\]$/)
        if (match) {
          const label = match[1]
          return (
            <a
              key={i}
              href={`#source-${label}`}
              className="citation-badge"
              title={`Jump to source ${label}`}
            >
              {label}
            </a>
          )
        }
        return <span key={i}>{part}</span>
      })}
    </p>
  )
}

/**
 * Single source card shown in the Sources section.
 */
function SourceCard({ source }) {
  const pageRange =
    source.page_start != null && source.page_end != null
      ? source.page_start === source.page_end
        ? `Page ${source.page_start}`
        : `Pages ${source.page_start}–${source.page_end}`
      : null

  return (
    <div
      id={`source-${source.label}`}
      className="bg-white border border-slate-200 rounded-lg p-4 scroll-mt-8"
    >
      <div className="flex items-start gap-3">
        {/* Label badge */}
        <span className="shrink-0 mt-0.5 inline-flex items-center px-2 py-0.5 rounded text-xs font-bold bg-blue-600 text-white">
          {source.label}
        </span>

        <div className="min-w-0 flex-1">
          {/* Filename + pages */}
          <div className="flex flex-wrap items-center gap-2 mb-2">
            <span className="text-sm font-semibold text-slate-800 truncate">
              {source.filename}
            </span>
            {pageRange && (
              <span className="text-xs text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full border border-slate-200">
                {pageRange}
              </span>
            )}
          </div>

          {/* Passage excerpt */}
          {source.text && (
            <p className="text-xs text-slate-500 leading-relaxed line-clamp-3 border-l-2 border-slate-200 pl-3">
              {source.text}
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
  const [result, setResult]   = useState(null)   // { answer, sources }
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState(null)
  const textareaRef = useRef(null)

  const handleSubmit = useCallback(async (e) => {
    e.preventDefault()
    const q = question.trim()
    if (!q) return

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const res = await fetch('/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: q }),
      })

      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.detail || `Server error ${res.status}`)
      }

      const data = await res.json()
      setResult(data)
    } catch (err) {
      setError(err.message || 'Unexpected error. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }, [question])

  const handleClear = () => {
    setQuestion('')
    setResult(null)
    setError(null)
    textareaRef.current?.focus()
  }

  const hasQuestion = question.trim().length > 0

  return (
    <div className="min-h-screen bg-slate-50">

      {/* ── Top bar ── */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-3xl mx-auto px-4 py-3 flex items-center gap-3">
          {/* Icon */}
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center shrink-0">
            <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
            </svg>
          </div>
          <div>
            <h1 className="text-sm font-semibold text-slate-900 leading-tight">Academic RAG</h1>
            <p className="text-xs text-slate-500">Question Answering from PDF Documents</p>
          </div>
        </div>
      </header>

      {/* ── Main content ── */}
      <main className="max-w-3xl mx-auto px-4 py-8 space-y-6">

        {/* ── Question form ── */}
        <section>
          <form onSubmit={handleSubmit} className="space-y-3">
            <label htmlFor="question-input" className="block text-sm font-medium text-slate-700">
              Ask an academic question
            </label>

            <textarea
              id="question-input"
              ref={textareaRef}
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => {
                // Ctrl+Enter or Cmd+Enter submits
                if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') handleSubmit(e)
              }}
              placeholder="e.g. What is Retrieval-Augmented Generation?"
              rows={4}
              className="w-full rounded-lg border border-slate-300 bg-white px-4 py-3 text-base text-slate-800 placeholder-slate-400 shadow-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              disabled={loading}
            />

            <div className="flex items-center gap-3">
              <button
                id="ask-btn"
                type="submit"
                disabled={!hasQuestion || loading}
                className="inline-flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white text-sm font-medium rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              >
                {loading ? (
                  <>
                    <svg className="animate-spin w-4 h-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"/>
                    </svg>
                    Searching…
                  </>
                ) : (
                  <>
                    <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-4.35-4.35m0 0A7.5 7.5 0 104.5 4.5a7.5 7.5 0 0012.15 12.15z" />
                    </svg>
                    Ask
                  </>
                )}
              </button>

              {(hasQuestion || result || error) && (
                <button
                  id="clear-btn"
                  type="button"
                  onClick={handleClear}
                  className="text-sm text-slate-500 hover:text-slate-700 underline focus:outline-none"
                >
                  Clear
                </button>
              )}

              <span className="ml-auto text-xs text-slate-400 hidden sm:block">
                Ctrl+Enter to submit
              </span>
            </div>
          </form>
        </section>

        {/* ── Error state ── */}
        {error && (
          <section
            id="error-message"
            role="alert"
            className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 flex gap-3 items-start"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5 text-red-500 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
            </svg>
            <div>
              <p className="text-sm font-medium text-red-700">Request failed</p>
              <p className="text-sm text-red-600 mt-0.5">{error}</p>
            </div>
          </section>
        )}

        {/* ── Loading indicator ── */}
        {loading && (
          <section className="space-y-3 animate-pulse">
            <div className="h-4 bg-slate-200 rounded w-1/4"></div>
            <div className="h-4 bg-slate-200 rounded w-full"></div>
            <div className="h-4 bg-slate-200 rounded w-5/6"></div>
            <div className="h-4 bg-slate-200 rounded w-4/6"></div>
          </section>
        )}

        {/* ── Answer + Sources ── */}
        {result && !loading && (
          <>
            {/* Answer card */}
            <section id="answer-section" className="bg-white rounded-lg border border-slate-200 shadow-sm p-6 space-y-2">
              <h2 className="text-xs font-semibold uppercase tracking-wide text-slate-400">Answer</h2>
              <AnswerText text={result.answer} />
            </section>

            {/* Sources */}
            {result.sources && result.sources.length > 0 && (
              <section id="sources-section" className="space-y-3">
                <h2 className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                  Sources — {result.sources.length} retrieved
                </h2>
                <div className="space-y-3">
                  {result.sources.map((src) => (
                    <SourceCard key={src.label} source={src} />
                  ))}
                </div>
              </section>
            )}
          </>
        )}

        {/* ── Empty state ── */}
        {!result && !loading && !error && (
          <section className="text-center py-16 text-slate-400">
            <svg xmlns="http://www.w3.org/2000/svg" className="mx-auto w-12 h-12 mb-4 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z" />
            </svg>
            <p className="text-sm font-medium text-slate-500">Ask a question to get started</p>
            <p className="text-xs mt-1 text-slate-400">
              Answers are grounded in your PDF documents with inline citations.
            </p>
          </section>
        )}
      </main>

      {/* ── Footer ── */}
      <footer className="text-center py-6 text-xs text-slate-400 border-t border-slate-200 mt-8">
        Academic RAG · Powered by ChromaDB, BAAI/bge-small-en-v1.5 &amp; Groq
      </footer>
    </div>
  )
}
