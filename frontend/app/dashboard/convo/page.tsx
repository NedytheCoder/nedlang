"use client"

import { useCallback, useEffect, useRef, useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { motion, AnimatePresence } from "framer-motion"
import { GiEarthAfricaEurope } from "react-icons/gi"
import { useTranslation } from "../../../i18n/LanguageProvider"

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
const WS_URL      = BACKEND_URL.replace(/^http/, "ws")

const SAMPLE_RATE_IN  = 24000   // OpenAI Realtime API requires 24 kHz PCM16 input
const SAMPLE_RATE_OUT = 24000   // OpenAI sends 24 kHz PCM16 output

// ── Audio helpers ─────────────────────────────────────────────────────────────

function float32ToBase64Pcm16(f32: Float32Array): string {
  const i16 = new Int16Array(f32.length)
  for (let i = 0; i < f32.length; i++) {
    const s = Math.max(-1, Math.min(1, f32[i]))
    i16[i] = s < 0 ? s * 0x8000 : s * 0x7fff
  }
  const bytes = new Uint8Array(i16.buffer)
  let bin = ""
  for (let i = 0; i < bytes.byteLength; i++) bin += String.fromCharCode(bytes[i])
  return btoa(bin)
}

function base64Pcm16ToFloat32(b64: string): Float32Array {
  const bin    = atob(b64)
  const bytes  = new Uint8Array(bin.length)
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i)
  const i16    = new Int16Array(bytes.buffer)
  const buffer = new ArrayBuffer(i16.length * Float32Array.BYTES_PER_ELEMENT)
  const f32    = new Float32Array(buffer)
  for (let i = 0; i < i16.length; i++) f32[i] = i16[i] / 0x8000
  return f32
}

// ── Types ─────────────────────────────────────────────────────────────────────

type Status = "idle" | "connecting" | "listening" | "ai_speaking" | "thinking" | "ended" | "error"

interface Message {
  id: string
  role: "user" | "assistant"
  text: string
}

interface SessionInfo {
  level: string
  target_language: string
  native_language: string
}

// ── Component ─────────────────────────────────────────────────────────────────

export default function ConvoPage() {
  const router = useRouter()
  const { t }  = useTranslation()

  const [sessionInfo, setSessionInfo] = useState<SessionInfo | null>(null)
  const [status,      setStatus]      = useState<Status>("idle")
  const [messages,    setMessages]    = useState<Message[]>([])
  const [muted,       setMuted]       = useState(false)
  const [errorMsg,    setErrorMsg]    = useState<string | null>(null)

  // refs — survive re-renders, safe inside audio/ws callbacks
  const wsRef            = useRef<WebSocket | null>(null)
  const micStreamRef     = useRef<MediaStream | null>(null)
  const captureCtxRef    = useRef<AudioContext | null>(null)
  const playCtxRef       = useRef<AudioContext | null>(null)
  const processorRef     = useRef<ScriptProcessorNode | null>(null)
  const nextPlayTimeRef  = useRef(0)
  const assistantIdRef   = useRef<string | null>(null)
  const mutedRef         = useRef(false)
  const statusRef        = useRef<Status>("idle")
  const transcriptEndRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => { mutedRef.current = muted },   [muted])
  useEffect(() => { statusRef.current = status },  [status])

  // ── Auth + session info ──────────────────────────────────────────────────

  useEffect(() => {
    const userId = localStorage.getItem("nedlang_user_id")
    if (!userId) { router.replace("/auth/signup"); return }

    fetch(`${BACKEND_URL}/convo/session?user_id=${encodeURIComponent(userId)}`)
      .then(r => { if (!r.ok) throw new Error(); return r.json() })
      .then(setSessionInfo)
      .catch(() => setErrorMsg(t("convo_error_connect")))
  }, [])

  useEffect(() => {
    transcriptEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  useEffect(() => () => { teardown() }, [])

  // ── Teardown ─────────────────────────────────────────────────────────────

  function teardown() {
    processorRef.current?.disconnect()
    processorRef.current = null
    micStreamRef.current?.getTracks().forEach(t => t.stop())
    micStreamRef.current = null
    if (captureCtxRef.current && captureCtxRef.current.state !== "closed") {
      captureCtxRef.current.close()
    }
    captureCtxRef.current = null
    if (playCtxRef.current && playCtxRef.current.state !== "closed") {
      playCtxRef.current.close()
    }
    playCtxRef.current = null
    wsRef.current?.close()
    wsRef.current = null
  }

  // ── Audio playback ────────────────────────────────────────────────────────

  function scheduleChunk(b64: string) {
    if (!playCtxRef.current || playCtxRef.current.state === "closed") {
      playCtxRef.current      = new AudioContext({ sampleRate: SAMPLE_RATE_OUT })
      nextPlayTimeRef.current = 0
    }
    const ctx   = playCtxRef.current
    const f32   = base64Pcm16ToFloat32(b64)
    const buf   = ctx.createBuffer(1, f32.length, SAMPLE_RATE_OUT)
    buf.copyToChannel(f32, 0)
    const src   = ctx.createBufferSource()
    src.buffer  = buf
    src.connect(ctx.destination)
    const start = Math.max(nextPlayTimeRef.current, ctx.currentTime + 0.01)
    src.start(start)
    nextPlayTimeRef.current = start + buf.duration
  }

  // ── OAI event router ──────────────────────────────────────────────────────

  function handleEvent(msg: Record<string, unknown>) {
    switch (msg.type) {
      case "session.created":
      case "session.updated":
        setStatus("listening")
        break

      case "input_audio_buffer.speech_started":
        setStatus("listening")
        break

      case "input_audio_buffer.speech_stopped":
        setStatus("thinking")
        break

      case "conversation.item.input_audio_transcription.completed": {
        const text = (msg.transcript as string | undefined)?.trim()
        if (text) {
          setMessages(prev => [...prev, { id: `u-${Date.now()}`, role: "user", text }])
        }
        break
      }

      case "response.created":
        setStatus("thinking")
        assistantIdRef.current = `a-${Date.now()}`
        setMessages(prev => [...prev, { id: assistantIdRef.current!, role: "assistant", text: "" }])
        break

      case "response.output_audio.delta":
        setStatus("ai_speaking")
        if (msg.delta) scheduleChunk(msg.delta as string)
        break

      case "response.output_audio_transcript.delta": {
        const delta = msg.delta as string | undefined
        const id    = assistantIdRef.current
        if (delta && id) {
          setMessages(prev => prev.map(m => m.id === id ? { ...m, text: m.text + delta } : m))
        }
        break
      }

      case "response.output_audio.done":
      case "response.output_audio_transcript.done":
      case "response.done":
        setStatus("listening")
        assistantIdRef.current = null
        break

      case "error": {
        const errData = (msg.error as Record<string, unknown> | undefined)
        const errMsg  = (errData?.message as string | undefined) ?? (msg.message as string | undefined) ?? t("convo_error_connect")
        setStatus("error")
        setErrorMsg(errMsg)
        break
      }
    }
  }

  // ── Start session ─────────────────────────────────────────────────────────

  const startSession = useCallback(async () => {
    const userId = localStorage.getItem("nedlang_user_id")
    if (!userId || !sessionInfo) return

    setStatus("connecting")
    setMessages([])
    setErrorMsg(null)
    teardown()

    let stream: MediaStream
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        audio: { echoCancellation: true, noiseSuppression: true, sampleRate: SAMPLE_RATE_IN },
      })
    } catch {
      setStatus("error")
      setErrorMsg(t("convo_error_mic"))
      return
    }
    micStreamRef.current = stream

    const captureCtx       = new AudioContext({ sampleRate: SAMPLE_RATE_IN })
    captureCtxRef.current  = captureCtx
    const source           = captureCtx.createMediaStreamSource(stream)
    // ScriptProcessorNode — widely supported, deprecated but functional
    const processor        = captureCtx.createScriptProcessor(4096, 1, 1)
    processorRef.current   = processor

    processor.onaudioprocess = e => {
      if (wsRef.current?.readyState !== WebSocket.OPEN || mutedRef.current) return
      wsRef.current.send(JSON.stringify({
        type:  "input_audio_buffer.append",
        audio: float32ToBase64Pcm16(e.inputBuffer.getChannelData(0)),
      }))
    }
    source.connect(processor)
    processor.connect(captureCtx.destination)

    const ws      = new WebSocket(`${WS_URL}/convo/ws?user_id=${encodeURIComponent(userId)}`)
    wsRef.current = ws

    ws.onopen    = () => setStatus("listening")
    ws.onmessage = e => { try { handleEvent(JSON.parse(e.data as string)) } catch { /* skip */ } }
    ws.onerror   = () => { setStatus("error"); setErrorMsg(t("convo_error_connect")) }
    ws.onclose   = () => {
      if (statusRef.current !== "ended" && statusRef.current !== "error") setStatus("ended")
    }
  }, [sessionInfo, t])

  // ── End session ───────────────────────────────────────────────────────────

  function endSession() {
    setStatus("ended")
    teardown()
  }

  // ── Status display config ─────────────────────────────────────────────────

  const STATUS_CFG: Record<Status, { label: string; dot: string; pulse: boolean }> = {
    idle:        { label: t("convo_status_idle"),        dot: "bg-slate-400",   pulse: false },
    connecting:  { label: t("convo_status_connecting"),  dot: "bg-yellow-400",  pulse: true  },
    listening:   { label: t("convo_status_listening"),   dot: "bg-emerald-500", pulse: true  },
    ai_speaking: { label: t("convo_status_speaking"),    dot: "bg-indigo-500",  pulse: true  },
    thinking:    { label: t("convo_status_thinking"),    dot: "bg-amber-400",   pulse: true  },
    ended:       { label: t("convo_status_ended"),       dot: "bg-slate-400",   pulse: false },
    error:       { label: t("convo_status_error"),       dot: "bg-red-500",     pulse: false },
  }

  const cfg      = STATUS_CFG[status]
  const isActive = status === "listening" || status === "ai_speaking" || status === "thinking" || status === "connecting"

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex flex-col">

      {/* Header */}
      <header className="sticky top-0 z-50 bg-white/90 dark:bg-slate-900/90 backdrop-blur-md border-b border-slate-200 dark:border-white/8">
        <div className="max-w-2xl mx-auto px-4 sm:px-6">
          <div className="flex items-center justify-between h-16">
            <Link href="/" className="flex items-center gap-2 group flex-shrink-0">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-md shadow-indigo-500/30">
                <GiEarthAfricaEurope className="w-4 h-4 text-white" />
              </div>
              <span className="font-bold text-slate-900 dark:text-white text-lg tracking-tight group-hover:text-indigo-600 dark:group-hover:text-indigo-300 transition-colors">
                NedLang
              </span>
            </Link>

            <Link
              href="/dashboard"
              className="flex items-center gap-1.5 text-sm font-medium text-slate-600 dark:text-gray-400 hover:text-slate-900 dark:hover:text-white transition-colors"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              {t("convo_back")}
            </Link>
          </div>
        </div>
      </header>

      {/* Main */}
      <main className="flex-1 max-w-2xl w-full mx-auto px-4 sm:px-6 py-6 flex flex-col gap-4">

        {/* Session info bar */}
        {sessionInfo && (
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/8 rounded-2xl px-5 py-4 flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-md shadow-indigo-500/20 flex-shrink-0">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-semibold text-slate-900 dark:text-white text-sm truncate">{t("convo_title")}</p>
              <p className="text-xs text-slate-500 dark:text-gray-400">
                {sessionInfo.target_language} · {t("convo_level_label")} {sessionInfo.level}
              </p>
            </div>
            {/* live status pill */}
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-white/8 flex-shrink-0">
              <span className={`w-1.5 h-1.5 rounded-full ${cfg.dot} ${cfg.pulse ? "animate-pulse" : ""}`} />
              <span className="text-xs font-medium text-slate-600 dark:text-gray-400 whitespace-nowrap">{cfg.label}</span>
            </div>
          </div>
        )}

        {/* Transcript area */}
        <div className="flex-1 bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/8 rounded-2xl flex flex-col overflow-hidden min-h-[380px] sm:min-h-[460px]">
          <div className="flex-1 overflow-y-auto p-4 sm:p-5 space-y-3">
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full gap-3 text-center py-16">
                <motion.div
                  animate={isActive ? { scale: [1, 1.1, 1] } : {}}
                  transition={{ repeat: Infinity, duration: 2.2, ease: "easeInOut" }}
                  className="w-14 h-14 rounded-full bg-indigo-50 dark:bg-indigo-500/10 border border-indigo-100 dark:border-indigo-500/20 flex items-center justify-center"
                >
                  <svg className="w-7 h-7 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                </motion.div>
                <p className="text-sm text-slate-500 dark:text-gray-400 max-w-xs leading-relaxed">
                  {isActive
                    ? t("convo_empty_active")
                    : sessionInfo
                      ? `Press Start to begin your live ${sessionInfo.target_language} conversation.`
                      : "…"
                  }
                </p>
              </div>
            ) : (
              messages.map(msg => (
                <motion.div
                  key={msg.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.18 }}
                  className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div className="max-w-[82%] sm:max-w-[75%]">
                    <p className={`text-xs font-medium mb-1 ${
                      msg.role === "user"
                        ? "text-right text-slate-400 dark:text-gray-500"
                        : "text-left text-indigo-500 dark:text-indigo-400"
                    }`}>
                      {msg.role === "user" ? t("convo_you") : t("convo_tutor")}
                    </p>
                    <div className={`px-4 py-2.5 rounded-2xl text-sm leading-relaxed ${
                      msg.role === "user"
                        ? "bg-indigo-600 text-white rounded-br-sm"
                        : "bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-gray-100 rounded-bl-sm"
                    }`}>
                      {msg.text ? msg.text : (
                        <span className="flex gap-1 items-center py-0.5">
                          {[0, 150, 300].map(delay => (
                            <span
                              key={delay}
                              className="w-1.5 h-1.5 rounded-full bg-current opacity-60 animate-bounce"
                              style={{ animationDelay: `${delay}ms` }}
                            />
                          ))}
                        </span>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))
            )}
            <div ref={transcriptEndRef} />
          </div>
        </div>

        {/* Error banner */}
        <AnimatePresence>
          {errorMsg && (
            <motion.div
              initial={{ opacity: 0, y: -6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/30 text-red-700 dark:text-red-400 text-sm rounded-xl px-4 py-3 text-center"
            >
              {errorMsg}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Controls */}
        {status === "ended" ? (
          /* Session ended card */
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white dark:bg-slate-900 border border-emerald-200 dark:border-emerald-500/30 rounded-2xl p-5 sm:p-6 text-center"
          >
            <div className="w-11 h-11 rounded-2xl bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-100 dark:border-emerald-500/20 flex items-center justify-center mx-auto mb-3">
              <svg className="w-5 h-5 text-emerald-600 dark:text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <p className="text-sm font-semibold text-slate-900 dark:text-white mb-4">{t("convo_session_done")}</p>
            <div className="flex flex-col sm:flex-row gap-2 justify-center">
              <motion.button
                whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
                onClick={() => { setStatus("idle"); setMessages([]); setErrorMsg(null) }}
                className="px-5 py-2.5 text-sm font-semibold bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl transition-colors"
              >
                {t("convo_new_session")}
              </motion.button>
              <Link
                href="/dashboard"
                className="px-5 py-2.5 text-sm font-semibold bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-gray-300 rounded-xl transition-colors text-center"
              >
                {t("convo_back_dashboard")}
              </Link>
            </div>
          </motion.div>

        ) : !isActive ? (
          /* Start button */
          <motion.button
            whileHover={{ scale: 1.01 }} whileTap={{ scale: 0.99 }}
            onClick={startSession}
            disabled={!sessionInfo || status === "error"}
            className="w-full py-4 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 disabled:opacity-50 text-white font-semibold rounded-2xl shadow-lg shadow-indigo-500/20 transition-all flex items-center justify-center gap-2 text-sm sm:text-base"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
            {t("convo_start")}
          </motion.button>

        ) : (
          /* Live controls: mute + status + end */
          <div className="flex items-stretch gap-3">
            <motion.button
              whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.96 }}
              onClick={() => setMuted(m => !m)}
              aria-label={muted ? t("convo_mic_unmute") : t("convo_mic_mute")}
              className={`relative w-16 flex-shrink-0 rounded-2xl flex items-center justify-center transition-all shadow-md ${
                muted
                  ? "bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/30 text-red-500"
                  : "bg-indigo-600 text-white shadow-indigo-500/30"
              }`}
            >
              {!muted && status === "listening" && (
                <span className="absolute inset-0 rounded-2xl bg-indigo-400 opacity-25 animate-ping" />
              )}
              {muted ? (
                <svg className="w-6 h-6 relative z-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15zM17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2" />
                </svg>
              ) : (
                <svg className="w-6 h-6 relative z-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                </svg>
              )}
            </motion.button>

            <div className="flex-1 flex flex-col gap-2">
              <div className="flex items-center gap-2 px-4 py-2.5 bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-white/8 rounded-xl min-h-[44px]">
                <span className={`w-2 h-2 rounded-full flex-shrink-0 ${cfg.dot} ${cfg.pulse ? "animate-pulse" : ""}`} />
                <span className="text-sm font-medium text-slate-700 dark:text-gray-300 truncate">{cfg.label}</span>
                {muted && (
                  <span className="ml-auto text-xs font-semibold text-red-500 flex-shrink-0">{t("convo_muted")}</span>
                )}
              </div>
              <motion.button
                whileHover={{ scale: 1.01 }} whileTap={{ scale: 0.99 }}
                onClick={endSession}
                className="px-4 py-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-600 dark:text-gray-400 text-sm font-medium rounded-xl transition-all"
              >
                {t("convo_end")}
              </motion.button>
            </div>
          </div>
        )}

      </main>
    </div>
  )
}
