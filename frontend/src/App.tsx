import { useRef, useState } from 'react'
import { useChat } from '@ai-sdk/react'
import type { UIMessage } from 'ai'
import type { ChangeEvent } from 'react'
import './App.css'

const quickActions = ['Code', 'Learn', 'Write', 'Life stuff', 'Surprise me']
const studentTasks = {
  new: [
    'New Student Orientation',
    'Housing Explorer',
    'Building Finder / Map',
    'Course Registration Guidance',
    'International Student Support',
  ],
  existing: [
    'Library Study Rooms',
    'Assignment Deadlines',
    'Health Center Appointments',
  ],
} as const

const quickActionPrompts: Record<string, string> = {
  Code: 'Help me write clean, production-ready code for this task.',
  Learn: 'Teach me this topic step by step with a simple example.',
  Write: 'Help me draft a polished message I can send as-is.',
  'Life stuff': 'Give me a practical plan I can follow today.',
  'Surprise me': 'Surprise me with one useful thing I can do right now.',
}

const studentTaskPrompts: Record<string, string> = {
  'New Student Orientation': 'Guide me through new student orientation essentials.',
  'Housing Explorer': 'Help me compare housing options and choose the best fit.',
  'Building Finder / Map': 'Help me find campus buildings quickly with directions.',
  'Course Registration Guidance': 'Help me pick and register for courses this term.',
  'International Student Support': 'Show me support resources for international students.',
  'Library Study Rooms': 'Help me find and book a library study room.',
  'Assignment Deadlines': 'Help me organize upcoming assignment deadlines.',
  'Health Center Appointments': 'Help me book a health center appointment.',
}

const publicIcons = [
  '/Generated Image April 04, 2026 - 1_08PM.png',
  '/Generated Image April 04, 2026 - 1_09PM (1).png',
  '/Generated Image April 04, 2026 - 1_09PM (2).png',
  '/Generated Image April 04, 2026 - 1_09PM.png',
]
const randomIconIndex = Math.floor(Math.random() * publicIcons.length)
const selectedIcon = encodeURI(publicIcons[randomIconIndex])

const getMessageText = (message: UIMessage): string => {
  const text = message.parts
    .filter((part) => part.type === 'text')
    .map((part) => part.text)
    .join('\n')

  return text || '[non-text response]'
}

function App() {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [selectedFiles, setSelectedFiles] = useState<string[]>([])
  const [userType, setUserType] = useState<'new' | 'existing' | null>(null)

  const {
    messages,
    input,
    status,
    error,
    handleInputChange,
    handleSubmit,
    setInput,
  } = useChat({
    api: '/api/chat',
  })

  const handlePickFile = () => {
    fileInputRef.current?.click()
  }

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files
    if (!files || files.length === 0) {
      setSelectedFiles([])
      return
    }

    setSelectedFiles(Array.from(files).map((file) => file.name))
  }

  const hasHistory = messages.length > 0
  const oneClickTasks = userType ? studentTasks[userType] : []

  return (
    <div className="page-shell">
      {userType === null && (
        <div className="modal-backdrop" role="presentation">
          <section
            className="user-type-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="user-type-title"
          >
            <h2 id="user-type-title">Select Student Type</h2>
            <p>Are you a new student or an existing student?</p>
            <div className="modal-actions">
              <button type="button" onClick={() => setUserType('new')}>
                New Student
              </button>
              <button type="button" onClick={() => setUserType('existing')}>
                Existing Student
              </button>
            </div>
          </section>
        </div>
      )}

      <aside className="rail" aria-hidden="true">
        <button type="button" className="rail-item active" />
        <button type="button" className="rail-item" />
        <button type="button" className="rail-item" />
        <button type="button" className="rail-item" />
      </aside>

      <main className="chat-stage">
        <header className="top-header">
          <p className="brand">TrojanClaw</p>
          <div className="header-actions">
            <button type="button" className="auth-btn">
              Authenticate
            </button>
            <div className="user-icon" aria-label="User profile" role="img">
              <span>A</span>
            </div>
          </div>
        </header>

        <section className={`conversation ${hasHistory ? 'with-history' : ''}`}>
          {!hasHistory && (
            <h1 className="greeting">
              <img className="greeting-icon" src={selectedIcon} alt="TrojanClaw icon" />
              <span>TrojanClaw</span>
            </h1>
          )}

          {hasHistory && (
            <div className="history" aria-live="polite">
              {messages.map((message) => (
                <article key={message.id} className={`bubble ${message.role}`}>
                  <p>{getMessageText(message)}</p>
                </article>
              ))}
            </div>
          )}

          {oneClickTasks.length > 0 && (
            <div className="chip-row task-row" aria-label="One-click student tasks">
              {oneClickTasks.map((task) => (
                <button
                  key={task}
                  type="button"
                  className="chip"
                  onClick={() => setInput(studentTaskPrompts[task] ?? `Help me with ${task}.`)}
                >
                  {task}
                </button>
              ))}
            </div>
          )}

          <form className="prompt-card" onSubmit={handleSubmit}>
            <input
              ref={fileInputRef}
              className="file-input"
              type="file"
              multiple
              onChange={handleFileChange}
            />

            <label htmlFor="prompt" className="sr-only">
              Enter your prompt
            </label>
            <textarea
              id="prompt"
              value={input}
              onChange={handleInputChange}
              rows={3}
              placeholder="How can I help you today?"
            />

            <div className="prompt-bottom">
              <button
                type="button"
                className="plus-btn"
                aria-label="Add attachment"
                onClick={handlePickFile}
              >
                +
              </button>
              <button
                type="submit"
                className="send-btn"
                disabled={!input.trim() || status === 'submitted' || status === 'streaming'}
              >
                {status === 'submitted' || status === 'streaming' ? 'Sending...' : 'Send'}
              </button>
            </div>

            {selectedFiles.length > 0 && (
              <p className="file-meta" title={selectedFiles.join(', ')}>
                {selectedFiles.length} file(s) selected: {selectedFiles.join(', ')}
              </p>
            )}
          </form>

          <div className="chip-row" aria-label="Quick actions">
            {quickActions.map((item) => (
              <button
                key={item}
                type="button"
                className="chip"
                onClick={() => setInput(quickActionPrompts[item] ?? `Help me with ${item}.`)}
              >
                {item}
              </button>
            ))}
          </div>

          {error && <p className="error-text">Unable to reach /api/chat right now.</p>}
        </section>
      </main>
    </div>
  )
}

export default App
