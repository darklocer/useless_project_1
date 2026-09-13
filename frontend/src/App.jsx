import React, { useEffect, useRef, useState } from 'react'
import { checkWig } from './api.js'

const MIN_SCAN_MS = 2200

const verdictInfo = {
  'High Wig Suspicion 😂': {
    label: 'HIGH WIG SUSPICION',
    emoji: '🚨',
    tone: 'danger',
    description: 'The algorithm has detected an alarming amount of suspicious hair activity.',
  },
  'Suspicious 👀': {
    label: 'SUSPICIOUS',
    emoji: '👀',
    tone: 'warning',
    description: 'The evidence is looking a little too perfectly assembled.',
  },
  'Uncertain 🤔': {
    label: 'UNCERTAIN',
    emoji: '🤔',
    tone: 'neutral',
    description: 'The AI cannot reach a confident conclusion. The jury remains confused.',
  },
  'Probably Natural 🌱': {
    label: 'PROBABLY NATURAL',
    emoji: '🌱',
    tone: 'natural',
    description: 'The available visual evidence leans toward naturally occurring hair.',
  },
}

const remarks = [
  'The court has reviewed the follicles and remains deeply concerned.',
  'No hair was harmed during this investigation.',
  'The defendant is presumed natural until proven wiggy.',
  'The algorithm would like everyone to remain calm.',
  'This is an extremely serious investigation. Probably.',
]

function getInfo(result) {
  return verdictInfo[result] || {
    label: String(result || 'UNKNOWN VERDICT').replace(/[😂👀🤔🌱]/g, '').trim().toUpperCase(),
    emoji: '⚖️',
    tone: 'neutral',
    description: 'The AI returned a verdict, but the court is still reading the paperwork.',
  }
}

function App() {
  const [stage, setStage] = useState('idle')
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState('')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [dragging, setDragging] = useState(false)
  const inputRef = useRef(null)

  useEffect(() => {
    if (!file) {
      setPreview('')
      return
    }
    const url = URL.createObjectURL(file)
    setPreview(url)
    return () => URL.revokeObjectURL(url)
  }, [file])

  const selectFile = (nextFile) => {
    if (!nextFile) return
    if (!nextFile.type.startsWith('image/')) {
      setError('Please choose an image file.')
      return
    }
    setError('')
    setFile(nextFile)
    setResult(null)
    setStage('ready')
  }

  const analyze = async () => {
    if (!file) return
    setError('')
    setStage('scanning')
    const started = Date.now()

    try {
      const data = await checkWig(file)
      const remaining = MIN_SCAN_MS - (Date.now() - started)
      if (remaining > 0) {
        await new Promise((resolve) => setTimeout(resolve, remaining))
      }
      setResult(data)
      setStage('verdict')
    } catch (err) {
      const remaining = MIN_SCAN_MS - (Date.now() - started)
      if (remaining > 0) {
        await new Promise((resolve) => setTimeout(resolve, remaining))
      }
      setError(err.message || 'Something went wrong.')
      setStage('error')
    }
  }

  const reset = () => {
    setFile(null)
    setPreview('')
    setResult(null)
    setError('')
    setStage('idle')
  }

  const handleDrop = (event) => {
    event.preventDefault()
    setDragging(false)
    selectFile(event.dataTransfer.files?.[0])
  }

  return (
    <div className="app">
      <div className="noise" />
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">W</div>
          <div>
            <strong>WIGCHECK</strong>
            <span>HAIR INVESTIGATION UNIT</span>
          </div>
        </div>
        <div className="status-pill"><span /> AI SYSTEM ONLINE</div>
      </header>

      <main>
        {stage === 'idle' && (
          <section className="hero">
            <div className="eyebrow">CASE FILE #WIG-001</div>
            <h1>IS IT A WIG?</h1>
            <p className="hero-copy">
              Upload photographic evidence and let our highly questionable
              artificial intelligence investigate the hair situation.
            </p>

            <div
              className={`dropzone ${dragging ? 'dragging' : ''}`}
              onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
              onDragLeave={() => setDragging(false)}
              onDrop={handleDrop}
              onClick={() => inputRef.current?.click()}
            >
              <input
                ref={inputRef}
                type="file"
                accept="image/*"
                hidden
                onChange={(e) => selectFile(e.target.files?.[0])}
              />
              <div className="upload-icon">⌁</div>
              <h2>Present the evidence</h2>
              <p>Drop an image here or click to browse</p>
              <small>JPG · PNG · WEBP · One face recommended</small>
            </div>

            <div className="disclaimer">
              <span>⚖</span>
              <p>This is an experimental entertainment tool. A photo cannot reliably prove whether someone is wearing a wig.</p>
            </div>
          </section>
        )}

        {stage === 'ready' && (
          <section className="workspace">
            <div className="section-heading">
              <div>
                <div className="eyebrow">EVIDENCE RECEIVED</div>
                <h1>READY FOR ANALYSIS</h1>
              </div>
              <button className="ghost-btn" onClick={reset}>REMOVE</button>
            </div>

            <div className="evidence-layout">
              <div className="image-panel">
                <div className="exhibit-tag">EXHIBIT A</div>
                <img src={preview} alt="Uploaded evidence" />
                <div className="scan-corners" />
              </div>

              <div className="analysis-panel">
                <div className="case-label">CASE STATUS <b>READY</b></div>
                <h2>Let the AI inspect the evidence.</h2>
                <p>
                  MediaPipe will locate the face and the CLIP model will compare
                  the image against wig and natural-hair descriptions.
                </p>
                <button className="primary-btn" onClick={analyze}>
                  <span>RUN WIG INVESTIGATION</span>
                  <b>→</b>
                </button>
                <div className="mini-note">Expected result: scientifically questionable. Entertainment value: high.</div>
              </div>
            </div>
          </section>
        )}

        {stage === 'scanning' && (
          <section className="scan-screen">
            <div className="scanner-card">
              <div className="scan-image">
                <img src={preview} alt="Being analyzed" />
                <div className="laser" />
                <div className="grid-overlay" />
              </div>
              <div className="scanning-copy">
                <div className="eyebrow">AI DELIBERATION IN PROGRESS</div>
                <h1>EXAMINING HAIR...</h1>
                <div className="progress-track"><div /></div>
                <div className="scan-steps">
                  <span className="done">✓ Face detected</span>
                  <span className="done">✓ Hair region isolated</span>
                  <span className="active">◉ Comparing visual evidence</span>
                  <span>○ Preparing questionable verdict</span>
                </div>
              </div>
            </div>
          </section>
        )}

        {stage === 'verdict' && result && <Verdict result={result} preview={preview} onReset={reset} onAppeal={analyze} />}

        {stage === 'error' && (
          <section className="error-screen">
            <div className="error-symbol">!</div>
            <div className="eyebrow">COURTROOM ERROR</div>
            <h1>THE HAIR COURT HAS FAILED</h1>
            <p>{error}</p>
            <div className="error-actions">
              <button className="primary-btn" onClick={() => setStage(file ? 'ready' : 'idle')}>TRY AGAIN</button>
              <button className="ghost-btn" onClick={reset}>NEW CASE</button>
            </div>
          </section>
        )}
      </main>

      <footer>
        <span>WIGCHECK v2.0</span>
        <span>POWERED BY CLIP + MEDIAPIPE</span>
        <span>NO LEGAL VALUE WHATSOEVER</span>
      </footer>
    </div>
  )
}

function Verdict({ result, preview, onReset, onAppeal }) {
  const info = getInfo(result.result)
  const wig = Number(result.wig_probability ?? 0)
  const natural = Number(result.natural_probability ?? Math.max(0, 100 - wig))
  const remark = remarks[Math.floor(Math.random() * remarks.length)]

  return (
    <section className="verdict-page">
      <div className="verdict-header">
        <div>
          <div className="eyebrow">FINAL AI REPORT · CASE CLOSED</div>
          <h1>THE VERDICT</h1>
        </div>
        <div className={`verdict-badge ${info.tone}`}>{info.emoji} {info.label}</div>
      </div>

      <div className="verdict-grid">
        <div className="portrait-card">
          <div className="portrait-top"><span>EXHIBIT A</span><span>ANALYZED</span></div>
          <img src={preview} alt="Analyzed evidence" />
          <div className="portrait-bottom">
            <span>VISUAL EVIDENCE</span>
            <span>WIGCHECK</span>
          </div>
        </div>

        <div className="report-card">
          <div className="report-kicker">AI ASSESSMENT</div>
          <div className="big-verdict">{info.label}</div>
          <p className="verdict-description">{info.description}</p>

          <div className="probability-section">
            <div className="prob-row">
              <div><span>WIG PROBABILITY</span><strong>{wig.toFixed(1)}%</strong></div>
              <div className="bar"><div style={{ width: `${Math.min(100, Math.max(0, wig))}%` }} /></div>
            </div>
            <div className="prob-row natural-row">
              <div><span>NATURAL HAIR</span><strong>{natural.toFixed(1)}%</strong></div>
              <div className="bar"><div style={{ width: `${Math.min(100, Math.max(0, natural))}%` }} /></div>
            </div>
          </div>

          <div className="signal-box">
            <span>STRONGEST AI SIGNAL</span>
            <p>“{result.strongest_signal || 'No dominant signal returned.'}”</p>
            <small>Relative CLIP prompt score: {Number(result.signal_confidence ?? 0).toFixed(1)}%</small>
          </div>

          <div className="judge-note">
            <span>THE COURT NOTES</span>
            <p>“{remark}”</p>
          </div>
        </div>
      </div>

      <div className="verdict-actions">
        <button className="primary-btn" onClick={onAppeal}>↻ RUN AGAIN</button>
        <button className="ghost-btn" onClick={onReset}>+ NEW CASE</button>
      </div>

      <p className="final-disclaimer">
        CLIP scores shown here are relative prompt scores, not calibrated real-world probabilities.
      </p>
    </section>
  )
}

export default App