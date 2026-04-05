import { useEffect, useMemo, useRef, useState } from "react";
import { useChat } from "@ai-sdk/react";
import type { UIMessage } from "ai";
import type { ChangeEvent } from "react";
import type { FormEvent } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { API_BASE_URL, chatEndpointFetch } from "./lib/api";
import "./App.css";

const USC_SSO_URL = "https://my.usc.edu";
const AUTH_STORAGE_KEY = "usc-shibboleth-authenticated";

const quickActions = ["Code", "Learn", "Write", "Life stuff", "Surprise me"];
const studentTasks = {
  new: [
    "New Student Orientation",
    "Housing Explorer",
    "Building Finder / Map",
    "Course Registration Guidance",
    "International Student Support",
  ],
  existing: [
    "Library Study Rooms",
    "Assignment Deadlines",
    "Health Center Appointments",
  ],
} as const;

const quickActionPrompts: Record<string, string> = {
  Code: "Help me write clean, production-ready code for this task.",
  Learn: "Teach me this topic step by step with a simple example.",
  Write: "Help me draft a polished message I can send as-is.",
  "Life stuff": "Give me a practical plan I can follow today.",
  "Surprise me": "Surprise me with one useful thing I can do right now.",
};

const studentTaskPrompts: Record<string, string> = {
  "New Student Orientation":
    "Guide me through new student orientation essentials.",
  "Housing Explorer":
    "Help me compare housing options and choose the best fit.",
  "Building Finder / Map":
    "Help me find campus buildings quickly with directions.",
  "Course Registration Guidance":
    "Help me pick and register for courses this term.",
  "International Student Support":
    "Show me support resources for international students.",
  "Library Study Rooms": "Help me find and book a library study room.",
  "Assignment Deadlines": "Help me organize upcoming assignment deadlines.",
  "Health Center Appointments": "Help me book a health center appointment.",
};

const publicIcons = [
  "/Generated Image April 04, 2026 - 1_08PM.png",
  "/Generated Image April 04, 2026 - 1_09PM (1).png",
  "/Generated Image April 04, 2026 - 1_09PM (2).png",
  "/Generated Image April 04, 2026 - 1_09PM.png",
];
const randomIconIndex = Math.floor(Math.random() * publicIcons.length);
const selectedIcon = encodeURI(publicIcons[randomIconIndex]);

const getMessageText = (message: UIMessage): string => {
  const text = message.parts
    .filter((part) => part.type === "text")
    .map((part) => part.text)
    .join("\n")
    .trim();

  return text || "";
};

function App() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const endOfMessagesRef = useRef<HTMLDivElement>(null);
  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);
  const [userType, setUserType] = useState<"new" | "existing" | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    if (typeof window === "undefined") return false;
    return localStorage.getItem(AUTH_STORAGE_KEY) === "true";
  });
  const [showAuthConfirm, setShowAuthConfirm] = useState(false);
  const [showAuthRequired, setShowAuthRequired] = useState(false);
  const [showAuthSuccess, setShowAuthSuccess] = useState(false);

  const userContext = useMemo(
    () => ({
      student_type: userType,
      authenticated: isAuthenticated,
    }),
    [isAuthenticated, userType],
  );

  const {
    messages,
    input,
    status,
    error,
    handleInputChange,
    handleSubmit,
    setInput,
    stop,
    reload,
  } = useChat({
    api: `${API_BASE_URL}/chat`,
    streamProtocol: "text",
    experimental_prepareRequestBody: ({ messages: uiMessages }) => ({
      messages: uiMessages
        .map((message) => ({
          role: message.role === "assistant" ? "assistant" : "user",
          content: getMessageText(message),
        }))
        .filter((message) => message.content.length > 0),
      user_context: userContext,
    }),
    fetch: chatEndpointFetch,
  });

  useEffect(() => {
    if (!showAuthSuccess) return;

    const timer = window.setTimeout(() => {
      setShowAuthSuccess(false);
    }, 3200);

    return () => window.clearTimeout(timer);
  }, [showAuthSuccess]);

  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "end",
    });
  }, [messages, status]);

  const openAuthInNewTab = () => {
    window.open(USC_SSO_URL, "_blank", "noopener,noreferrer");
    setShowAuthConfirm(true);
  };

  const confirmAuth = () => {
    setIsAuthenticated(true);
    localStorage.setItem(AUTH_STORAGE_KEY, "true");
    setShowAuthConfirm(false);
    setShowAuthRequired(false);
    setShowAuthSuccess(true);
  };

  const handlePickFile = () => {
    if (!isAuthenticated) {
      setShowAuthRequired(true);
      return;
    }

    fileInputRef.current?.click();
  };

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) {
      setSelectedFiles([]);
      return;
    }

    setSelectedFiles(Array.from(files).map((file) => file.name));
  };

  const hasHistory = messages.length > 0;
  const oneClickTasks = userType ? studentTasks[userType] : [];
  const isLoading = status === "submitted" || status === "streaming";

  const handlePromptSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!isAuthenticated) {
      setShowAuthRequired(true);
      return;
    }

    handleSubmit(event);
  };

  const handleQuickAction = (item: string) => {
    if (!isAuthenticated) {
      setShowAuthRequired(true);
      return;
    }

    setInput(quickActionPrompts[item] ?? `Help me with ${item}.`);
  };

  const handleStudentTask = (task: string) => {
    if (!isAuthenticated) {
      setShowAuthRequired(true);
      return;
    }

    setInput(studentTaskPrompts[task] ?? `Help me with ${task}.`);
  };

  return (
    <div className="page-shell">
      {showAuthSuccess && (
        <p className="auth-toast">Authentication successful</p>
      )}

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
              <button type="button" onClick={() => setUserType("new")}>
                New Student
              </button>
              <button type="button" onClick={() => setUserType("existing")}>
                Existing Student
              </button>
            </div>
          </section>
        </div>
      )}

      {showAuthConfirm && (
        <div className="modal-backdrop" role="presentation">
          <section
            className="user-type-modal auth-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="auth-confirm-title"
          >
            <h2 id="auth-confirm-title">Complete USC Sign In</h2>
            <p>
              USC login opened in a new tab. After you finish sign in there,
              come back and confirm below.
            </p>
            <div className="modal-actions">
              <button type="button" onClick={() => setShowAuthConfirm(false)}>
                Not yet
              </button>
              <button type="button" onClick={confirmAuth}>
                I have authenticated
              </button>
            </div>
          </section>
        </div>
      )}

      {showAuthRequired && (
        <div className="modal-backdrop" role="presentation">
          <section
            className="user-type-modal auth-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="auth-required-title"
          >
            <h2 id="auth-required-title">Authentication Required</h2>
            <p>
              Please authenticate with USC Shibboleth before using prompting
              features.
            </p>
            <div className="modal-actions">
              <button type="button" onClick={() => setShowAuthRequired(false)}>
                Close
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowAuthRequired(false);
                  openAuthInNewTab();
                }}
              >
                Authenticate now
              </button>
            </div>
          </section>
        </div>
      )}

      <main className="chat-stage">
        <header className="top-header">
          <div />
          <div className="header-actions">
            <button
              type="button"
              className="refresh-btn"
              onClick={() => void reload()}
              disabled={messages.length === 0 || isLoading}
            >
              Regenerate
            </button>
            <button
              type="button"
              className={`auth-btn ${isAuthenticated ? "authenticated" : ""}`}
              onClick={openAuthInNewTab}
            >
              {isAuthenticated ? "Authenticated" : "Authenticate"}
            </button>
            <div className="user-icon" aria-label="User profile" role="img">
              <span>A</span>
            </div>
          </div>
        </header>

        <section
          className={`conversation ${hasHistory ? "with-history" : ""}`}
          aria-busy={isLoading}
        >
          {!hasHistory && (
            <div className="hero-branding">
              <img
                className="hero-logo"
                src={selectedIcon}
                alt="TrojanClaw logo"
              />
              <h1 className="hero-title">TrojanClaw</h1>
              <p className="hero-subtitle">USC AI Concierge</p>
              <p className="hero-description">
                Ask about schedules, campus resources, study spaces, and student
                life in one place.
              </p>
              {isLoading && (
                <div className="hero-skeletons" aria-hidden="true">
                  <div className="skeleton skeleton-pill" />
                  <div className="skeleton skeleton-pill short" />
                </div>
              )}
            </div>
          )}

          {hasHistory && (
            <div className="history" aria-live="polite">
              {messages.map((message) => (
                <article key={message.id} className={`bubble ${message.role}`}>
                  <div className="bubble-meta">
                    {message.role === "user" ? "You" : "TrojanClaw"}
                  </div>
                  {message.role === "assistant" ? (
                    <div className="markdown-body">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {getMessageText(message)}
                      </ReactMarkdown>
                    </div>
                  ) : (
                    <p>{getMessageText(message)}</p>
                  )}
                </article>
              ))}
              {isLoading && (
                <article className="bubble assistant loading">
                  <div className="bubble-meta">TrojanClaw</div>
                  <div className="skeleton skeleton-line" />
                  <div className="skeleton skeleton-line short" />
                </article>
              )}
              <div ref={endOfMessagesRef} />
            </div>
          )}

          {oneClickTasks.length > 0 && (
            <div
              className="chip-row task-row"
              aria-label="One-click student tasks"
            >
              {oneClickTasks.map((task) => (
                <button
                  key={task}
                  type="button"
                  className="chip"
                  onClick={() => handleStudentTask(task)}
                  disabled={!isAuthenticated}
                >
                  {task}
                </button>
              ))}
            </div>
          )}

          <form className="prompt-card" onSubmit={handlePromptSubmit}>
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
              disabled={!isAuthenticated}
              rows={3}
              placeholder={
                isAuthenticated
                  ? "How can I help you today?"
                  : "Authenticate with USC first to start prompting."
              }
            />

            <div className="prompt-bottom">
              <button
                type="button"
                className="plus-btn"
                aria-label="Add attachment"
                onClick={handlePickFile}
                disabled={!isAuthenticated}
              >
                +
              </button>
              <button
                type="submit"
                className="send-btn"
                disabled={!isAuthenticated || !input.trim() || isLoading}
              >
                {isLoading ? "Sending..." : "Send"}
              </button>
              {isLoading && (
                <button type="button" className="stop-btn" onClick={stop}>
                  Stop
                </button>
              )}
            </div>

            {selectedFiles.length > 0 && (
              <p className="file-meta" title={selectedFiles.join(", ")}>
                {selectedFiles.length} file(s) selected:{" "}
                {selectedFiles.join(", ")}
              </p>
            )}
          </form>

          <div className="chip-row" aria-label="Quick actions">
            {quickActions.map((item) => (
              <button
                key={item}
                type="button"
                className="chip"
                onClick={() => handleQuickAction(item)}
                disabled={!isAuthenticated}
              >
                {item}
              </button>
            ))}
          </div>

          {!isAuthenticated && (
            <p className="auth-hint">
              USC authentication is required before any prompting.
            </p>
          )}

          {isLoading && (
            <p className="loading-indicator" role="status" aria-live="polite">
              TrojanClaw is searching USC sources...
            </p>
          )}

          {error && <p className="error-text">{error.message}</p>}
        </section>
      </main>
    </div>
  );
}

export default App;
