"use client"

import { useCallback, useEffect, useRef, useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { AnimatePresence, motion } from "framer-motion"
import { GiEarthAfricaEurope } from "react-icons/gi"
import { useTranslation } from "../../../../i18n/LanguageProvider"

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
const VOICE_REPLY_PROBABILITY = 0.3

interface SessionInfo {
  level: string
  target_language: string
  native_language: string
}

type MessageRole = "user" | "assistant"
type MessageKind = "text" | "voice"

interface ChatMessage {
  id: string
  role: MessageRole
  kind: MessageKind
  text?: string
  audioSrc?: string
  timestamp: Date
  isLoading?: boolean
}

// Seeded waveform bars — consistent per message id
function waveBars(seed: string, count = 22): number[] {
  let h = 5381
  for (let i = 0; i < seed.length; i++) h = ((h << 5) + h) ^ seed.charCodeAt(i)
  return Array.from({ length: count }, (_, i) => {
    const v = Math.sin((h * (i + 1) * 127773) % 1) * 43758.5453
    return 18 + Math.abs(v - Math.floor(v)) * 62
  })
}

function VoicePlayer({
  src,
  isUser,
  msgId,
}: {
  src: string
  isUser: boolean
  msgId: string
}) {
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const [playing, setPlaying] = useState(false)
  const [progress, setProgress] = useState(0)
  const [duration, setDuration] = useState(0)
  const bars = waveBars(msgId)

  useEffect(() => {
    const audio = new Audio(src)
    audioRef.current = audio

    audio.onloadedmetadata = () => {
      if (isFinite(audio.duration)) setDuration(audio.duration)
    }
    audio.ondurationchange = () => {
      if (isFinite(audio.duration)) setDuration(audio.duration)
    }
    audio.ontimeupdate = () => {
      if (isFinite(audio.duration) && audio.duration > 0) {
        setProgress(audio.currentTime / audio.duration)
      }
    }
    audio.onended = () => {
      setPlaying(false)
      setProgress(0)
    }

    return () => {
      audio.pause()
      audioRef.current = null
    }
  }, [src])

  function toggle() {
    const audio = audioRef.current
    if (!audio) return
    if (playing) {
      audio.pause()
      setPlaying(false)
    } else {
      audio.play()
      setPlaying(true)
    }
  }

  function fmt(s: number) {
    const m = Math.floor(s / 60)
    const sec = Math.floor(s % 60)
    return `${m}:${sec.toString().padStart(2, "0")}`
  }

  return (
    <div className="flex items-center gap-2.5 min-w-[190px]">
      <button
        onClick={toggle}
        className={`w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0 transition-all ${
          isUser
            ? "bg-white/20 hover:bg-white/30 active:bg-white/40"
            : "bg-indigo-100 dark:bg-indigo-500/20 hover:bg-indigo-200 dark:hover:bg-indigo-500/30"
        }`}
      >
        {playing ? (
          <svg
            className={`w-4 h-4 ${isUser ? "text-white" : "text-indigo-600 dark:text-indigo-400"}`}
            fill="currentColor"
            viewBox="0 0 24 24"
          >
            <rect x="6" y="4" width="4" height="16" rx="1" />
            <rect x="14" y="4" width="4" height="16" rx="1" />
          </svg>
        ) : (
          <svg
            className={`w-4 h-4 translate-x-0.5 ${isUser ? "text-white" : "text-indigo-600 dark:text-indigo-400"}`}
            fill="currentColor"
            viewBox="0 0 24 24"
          >
            <path d="M8 5v14l11-7z" />
          </svg>
        )}
      </button>

      <div className="flex-1 flex flex-col gap-1 min-w-0">
        {/* Waveform */}
        <div className="flex items-center gap-px h-7">
          {bars.map((h, i) => {
            const filled = progress * bars.length > i
            return (
              <div
                key={i}
                style={{ height: `${h}%` }}
                className={`w-[3px] rounded-full flex-shrink-0 transition-colors duration-100 ${
                  filled
                    ? isUser
                      ? "bg-white"
                      : "bg-indigo-500"
                    : isUser
                      ? "bg-white/35"
                      : "bg-slate-300 dark:bg-slate-600"
                }`}
              />
            )
          })}
        </div>
        <span
          className={`text-[10px] leading-none ${
            isUser ? "text-white/65" : "text-slate-400 dark:text-gray-500"
          }`}
        >
          {duration > 0 ? fmt(duration * (playing ? progress : 1)) : "0:00"}
        </span>
      </div>
    </div>
  )
}

export default function ConvoChatPage() {
  const router = useRouter()
  const { t } = useTranslation()

  const [sessionInfo, setSessionInfo] = useState<SessionInfo | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [inputText, setInputText] = useState("")
  const [sending, setSending] = useState(false)
  const [recording, setRecording] = useState(false)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)

  const historyRef = useRef<{ role: string; content: string }[]>([])
  const sendingRef = useRef(false)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const bottomRef = useRef<HTMLDivElement | null>(null)
  const inputRef = useRef<HTMLInputElement | null>(null)

  // Keep sendingRef in sync
  useEffect(() => {
    sendingRef.current = sending
  }, [sending])

  // Fetch session info
  useEffect(() => {
    const userId = localStorage.getItem("nedlang_user_id")
    if (!userId) {
      router.replace("/auth/signup")
      return
    }
    fetch(`${BACKEND_URL}/convo/session?user_id=${encodeURIComponent(userId)}`)
      .then((r) => {
        if (!r.ok) throw new Error()
        return r.json()
      })
      .then(setSessionInfo)
      .catch(() => {})
  }, [])

  // Auto-scroll to bottom
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  // Keep conversation history in sync (text only, for API)
  useEffect(() => {
    historyRef.current = messages
      .filter((m) => !m.isLoading && m.text)
      .map((m) => ({ role: m.role, content: m.text! }))
  }, [messages])

  function addLoadingBubble(): string {
    const id = `loading-${Date.now()}-${Math.random()}`
    setMessages((prev) => [
      ...prev,
      { id, role: "assistant", kind: "text", timestamp: new Date(), isLoading: true },
    ])
    return id
  }

  function resolveLoadingBubble(
    id: string,
    data: { assistant_text: string; assistant_audio: string },
  ) {
    const useVoice = Math.random() < VOICE_REPLY_PROBABILITY && !!data.assistant_audio
    setMessages((prev) =>
      prev.map((m) =>
        m.id === id
          ? {
              ...m,
              id: `msg-${Date.now()}-${Math.random()}`,
              isLoading: false,
              kind: useVoice ? "voice" : "text",
              text: useVoice ? data.assistant_text : data.assistant_text,
              audioSrc: useVoice ? `data:audio/mp3;base64,${data.assistant_audio}` : undefined,
            }
          : m,
      ),
    )
  }

  async function sendText() {
    const text = inputText.trim()
    if (!text || sendingRef.current) return
    const userId = localStorage.getItem("nedlang_user_id")
    if (!userId) return

    setInputText("")
    setSending(true)
    setErrorMsg(null)

    const userMsg: ChatMessage = {
      id: `u-${Date.now()}`,
      role: "user",
      kind: "text",
      text,
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, userMsg])
    const loadingId = addLoadingBubble()

    try {
      const res = await fetch(`${BACKEND_URL}/convo/chat/text-turn`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId, text, history: historyRef.current }),
      })
      if (!res.ok) throw new Error()
      const data = await res.json()
      resolveLoadingBubble(loadingId, data)
    } catch {
      setMessages((prev) => prev.filter((m) => m.id !== loadingId))
      setErrorMsg(t("chat_error_send"))
    } finally {
      setSending(false)
    }
  }

  const sendVoice = useCallback(
    async (blob: Blob) => {
      const userId = localStorage.getItem("nedlang_user_id")
      if (!userId) return

      setSending(true)
      setErrorMsg(null)

      const blobUrl = URL.createObjectURL(blob)
      const userMsgId = `u-${Date.now()}`
      const userMsg: ChatMessage = {
        id: userMsgId,
        role: "user",
        kind: "voice",
        audioSrc: blobUrl,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, userMsg])
      const loadingId = `loading-${Date.now()}-${Math.random()}`
      setMessages((prev) => [
        ...prev,
        { id: loadingId, role: "assistant", kind: "text", timestamp: new Date(), isLoading: true },
      ])

      try {
        const ext = blob.type.includes("ogg") ? "ogg" : blob.type.includes("mp4") ? "mp4" : "webm"
        const form = new FormData()
        form.append("audio", blob, `recording.${ext}`)
        form.append("history", JSON.stringify(historyRef.current))

        const res = await fetch(
          `${BACKEND_URL}/convo/chat/turn?user_id=${encodeURIComponent(userId)}`,
          { method: "POST", body: form },
        )
        if (!res.ok) throw new Error()
        const data = await res.json()

        // Attach transcription to user's voice bubble
        setMessages((prev) =>
          prev.map((m) => (m.id === userMsgId ? { ...m, text: data.user_text } : m)),
        )

        const useVoice =
          Math.random() < VOICE_REPLY_PROBABILITY && !!data.assistant_audio
        setMessages((prev) =>
          prev.map((m) =>
            m.id === loadingId
              ? {
                  ...m,
                  id: `msg-${Date.now()}`,
                  isLoading: false,
                  kind: useVoice ? "voice" : "text",
                  text: data.assistant_text,
                  audioSrc: useVoice
                    ? `data:audio/mp3;base64,${data.assistant_audio}`
                    : undefined,
                }
              : m,
          ),
        )
      } catch {
        setMessages((prev) => prev.filter((m) => m.id !== loadingId))
        setErrorMsg(t("chat_error_send"))
      } finally {
        setSending(false)
      }
    },
    [t],
  )

  const startRecording = useCallback(async () => {
    if (sendingRef.current) return
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mimeType = [
        "audio/webm;codecs=opus",
        "audio/webm",
        "audio/ogg;codecs=opus",
        "audio/mp4",
      ].find((t) => MediaRecorder.isTypeSupported(t)) ?? ""
      const mr = new MediaRecorder(stream, mimeType ? { mimeType } : undefined)
      mediaRecorderRef.current = mr
      chunksRef.current = []
      mr.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data)
      }
      mr.onstop = () => {
        stream.getTracks().forEach((t) => t.stop())
        const actualType = mr.mimeType || mimeType || "audio/webm"
        const blob = new Blob(chunksRef.current, { type: actualType })
        if (blob.size > 0) sendVoice(blob)
      }
      mr.start()
      setRecording(true)
      setErrorMsg(null)
    } catch {
      setErrorMsg(t("convo_error_mic"))
    }
  }, [sendVoice, t])

  const stopRecording = useCallback(() => {
    if (!recording || !mediaRecorderRef.current) return
    mediaRecorderRef.current.stop()
    mediaRecorderRef.current = null
    setRecording(false)
  }, [recording])

  function fmtTime(d: Date) {
    return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
  }

  return (
    <div className="h-screen bg-slate-100 dark:bg-slate-950 flex flex-col overflow-hidden">

      {/* ── Header ── */}
      <header className="flex-shrink-0 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-white/8 px-4 sm:px-6 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3 min-w-0">
          <Link
            href="/dashboard/convo"
            className="flex-shrink-0 flex items-center justify-center w-8 h-8 rounded-full hover:bg-slate-100 dark:hover:bg-white/8 transition-colors text-slate-500 dark:text-gray-400 hover:text-slate-900 dark:hover:text-white"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </Link>

          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-sm flex-shrink-0">
              <GiEarthAfricaEurope className="w-4 h-4 text-white" />
            </div>
            <div className="min-w-0">
              <p className="text-sm font-semibold text-slate-900 dark:text-white leading-none truncate">
                {t("chat_tutor_name")}
              </p>
              {sessionInfo && (
                <p className="text-xs text-slate-500 dark:text-gray-400 mt-0.5 truncate">
                  {sessionInfo.target_language} · {t("convo_level_label")} {sessionInfo.level}
                </p>
              )}
            </div>
          </div>
        </div>

        <Link href="/" className="group flex-shrink-0">
          <span className="font-bold text-slate-900 dark:text-white text-base tracking-tight group-hover:text-indigo-600 dark:group-hover:text-indigo-300 transition-colors">
            NedLang
          </span>
        </Link>
      </header>

      {/* ── Message thread ── */}
      <div className="flex-1 overflow-y-auto px-3 sm:px-6 py-4 space-y-0.5">

        {/* Empty state */}
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full gap-3 text-center pb-8">
            <div className="w-14 h-14 rounded-full bg-indigo-50 dark:bg-indigo-500/10 border border-indigo-100 dark:border-indigo-500/20 flex items-center justify-center">
              <svg
                className="w-7 h-7 text-indigo-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                />
              </svg>
            </div>
            <p className="text-sm text-slate-500 dark:text-gray-400 max-w-[240px] leading-relaxed">
              {t("chat_empty")}{" "}
              <span className="font-semibold text-indigo-500">
                {sessionInfo?.target_language ?? "…"}
              </span>
              !
            </p>
          </div>
        )}

        {/* Bubbles */}
        {messages.map((msg) => {
          const isUser = msg.role === "user"
          return (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 10, scale: 0.97 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              transition={{ duration: 0.18, ease: "easeOut" }}
              className={`flex ${isUser ? "justify-end" : "justify-start"} mb-1`}
            >
              {/* AI avatar */}
              {!isUser && (
                <div className="w-7 h-7 rounded-full bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center flex-shrink-0 mr-2 mt-auto mb-0.5">
                  <GiEarthAfricaEurope className="w-3.5 h-3.5 text-white" />
                </div>
              )}

              <div
                className={`max-w-[78%] sm:max-w-[62%] flex flex-col ${
                  isUser ? "items-end" : "items-start"
                }`}
              >
                {/* Bubble */}
                <div
                  className={`px-4 py-2.5 rounded-2xl shadow-sm ${
                    isUser
                      ? "bg-indigo-600 text-white rounded-br-md"
                      : "bg-white dark:bg-slate-800 text-slate-800 dark:text-gray-100 rounded-bl-md border border-slate-100 dark:border-white/8"
                  }`}
                >
                  {msg.isLoading ? (
                    /* Typing indicator */
                    <span className="flex items-center gap-1 py-0.5 px-0.5">
                      {[0, 160, 320].map((delay) => (
                        <span
                          key={delay}
                          style={{ animationDelay: `${delay}ms` }}
                          className="w-2 h-2 rounded-full bg-slate-300 dark:bg-slate-500 animate-bounce"
                        />
                      ))}
                    </span>
                  ) : msg.kind === "voice" && msg.audioSrc ? (
                    <VoicePlayer src={msg.audioSrc} isUser={isUser} msgId={msg.id} />
                  ) : (
                    <p className="text-sm leading-relaxed whitespace-pre-wrap break-words">
                      {msg.text}
                    </p>
                  )}
                </div>

                {/* Timestamp + ticks */}
                {!msg.isLoading && (
                  <div
                    className={`flex items-center gap-1 mt-1 ${isUser ? "flex-row-reverse" : ""}`}
                  >
                    <span className="text-[10px] text-slate-400 dark:text-gray-600">
                      {fmtTime(msg.timestamp)}
                    </span>
                    {isUser && (
                      <svg
                        className="w-4 h-3.5 text-indigo-400"
                        viewBox="0 0 16 12"
                        fill="none"
                      >
                        <path
                          d="M1 6l4 4L13 2"
                          stroke="currentColor"
                          strokeWidth="1.8"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        />
                        <path
                          d="M4 6l4 4 8-8"
                          stroke="currentColor"
                          strokeWidth="1.8"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          opacity="0.5"
                        />
                      </svg>
                    )}
                  </div>
                )}
              </div>
            </motion.div>
          )
        })}

        {/* Error banner */}
        <AnimatePresence>
          {errorMsg && (
            <motion.div
              initial={{ opacity: 0, y: 4 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 4 }}
              className="flex justify-center py-1"
            >
              <div className="flex items-center gap-2 bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/30 text-red-600 dark:text-red-400 text-xs font-medium rounded-xl px-4 py-2">
                <svg className="w-3.5 h-3.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {errorMsg}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <div ref={bottomRef} />
      </div>

      {/* ── Recording banner ── */}
      <AnimatePresence>
        {recording && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="flex-shrink-0 overflow-hidden"
          >
            <div className="flex items-center justify-center gap-2.5 py-2 bg-red-50 dark:bg-red-500/10 border-t border-red-200 dark:border-red-500/20">
              <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
              <span className="text-xs font-semibold text-red-600 dark:text-red-400">
                {t("chat_recording")}
              </span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── Input bar ── */}
      <div className="flex-shrink-0 bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-white/8 px-3 sm:px-5 py-3">
        <div className="max-w-3xl mx-auto flex items-end gap-2">

          {/* Text field */}
          <div className="flex-1 flex items-center bg-slate-100 dark:bg-slate-800 rounded-2xl px-4 min-h-[48px]">
            <input
              ref={inputRef}
              type="text"
              value={inputText}
              onChange={(e) => {
                setInputText(e.target.value)
                setErrorMsg(null)
              }}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault()
                  sendText()
                }
              }}
              placeholder={t("chat_input_placeholder")}
              disabled={recording || sending}
              className="flex-1 bg-transparent text-sm text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-gray-500 outline-none py-3 disabled:opacity-60"
            />
          </div>

          {/* Send / Record button */}
          <AnimatePresence mode="wait" initial={false}>
            {inputText.trim() ? (
              <motion.button
                key="send"
                initial={{ scale: 0.7, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.7, opacity: 0 }}
                transition={{ duration: 0.12 }}
                whileHover={{ scale: 1.06 }}
                whileTap={{ scale: 0.92 }}
                onClick={sendText}
                disabled={sending}
                aria-label="Send"
                className="w-12 h-12 rounded-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 flex items-center justify-center shadow-md shadow-indigo-500/30 transition-colors flex-shrink-0"
              >
                <svg
                  className="w-5 h-5 text-white translate-x-0.5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                  />
                </svg>
              </motion.button>
            ) : (
              <motion.button
                key="mic"
                initial={{ scale: 0.7, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.7, opacity: 0 }}
                transition={{ duration: 0.12 }}
                whileHover={!recording ? { scale: 1.06 } : {}}
                whileTap={{ scale: 0.9 }}
                onMouseDown={startRecording}
                onMouseUp={stopRecording}
                onMouseLeave={stopRecording}
                onTouchStart={(e) => {
                  e.preventDefault()
                  startRecording()
                }}
                onTouchEnd={(e) => {
                  e.preventDefault()
                  stopRecording()
                }}
                disabled={sending}
                aria-label={recording ? "Stop recording" : "Hold to record"}
                className={`w-12 h-12 rounded-full flex items-center justify-center shadow-md transition-all duration-150 flex-shrink-0 ${
                  recording
                    ? "bg-red-500 shadow-red-500/40 scale-110"
                    : "bg-indigo-600 hover:bg-indigo-500 shadow-indigo-500/30 disabled:opacity-50"
                }`}
              >
                {recording ? (
                  <span className="w-4 h-4 rounded-sm bg-white" />
                ) : (
                  <svg
                    className="w-5 h-5 text-white"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
                    />
                  </svg>
                )}
              </motion.button>
            )}
          </AnimatePresence>
        </div>

        <p className="text-center text-[10px] text-slate-400 dark:text-gray-600 mt-1.5 leading-none">
          {t("chat_hold_hint")}
        </p>
      </div>
    </div>
  )
}
