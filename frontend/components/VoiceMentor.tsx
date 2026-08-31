"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { api, getStoredProfileId } from "@/lib/api";
import { EmptyState } from "@/components/ui";

type Msg = { role: "user" | "assistant"; content: string };
type MicState = "idle" | "listening" | "error";
type SpeakState = "idle" | "speaking";

// Web Speech API types (not in default TS lib)
declare global {
  interface Window {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    SpeechRecognition: any;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    webkitSpeechRecognition: any;
  }
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function getSpeechRecognition(): any | null {
  if (typeof window === "undefined") return null;
  return window.SpeechRecognition || window.webkitSpeechRecognition || null;
}

export default function VoiceMentor() {
  const [profileId, setProfileId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Msg[]>([
    {
      role: "assistant",
      content:
        "Hi — I'm your AI Mentor. I know your profile, skill gaps, and roadmap. Speak or type to ask me anything.",
    },
  ]);
  const [input, setInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [micState, setMicState] = useState<MicState>("idle");
  const [micError, setMicError] = useState<string | null>(null);
  const [speakState, setSpeakState] = useState<SpeakState>("idle");
  const [lastReply, setLastReply] = useState<string | null>(null);
  const [speechSupported] = useState<boolean>(() => !!getSpeechRecognition());

  const endRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    setProfileId(getStoredProfileId());
  }, []);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, chatLoading]);

  // Clean up recognition and synthesis on unmount
  useEffect(() => {
    return () => {
      recognitionRef.current?.abort();
      window.speechSynthesis?.cancel();
    };
  }, []);

  /* ── Send message ─────────────────────────────────────────────────────── */
  async function send(text: string) {
    const trimmed = text.trim();
    if (!profileId || !trimmed || chatLoading) return;

    setMessages((m) => [...m, { role: "user", content: trimmed }]);
    setInput("");
    setChatLoading(true);
    setMicError(null);

    try {
      const res = await api.chat(profileId, trimmed);
      setMessages((m) => [...m, { role: "assistant", content: res.reply }]);
      setLastReply(res.reply);
    } catch {
      const errMsg = "Sorry, I couldn't reach the server. Please try again.";
      setMessages((m) => [...m, { role: "assistant", content: errMsg }]);
      setLastReply(null);
    } finally {
      setChatLoading(false);
    }
  }

  /* ── Microphone ───────────────────────────────────────────────────────── */
  function startListening() {
    if (!speechSupported) {
      setMicError("Voice input is not supported in this browser. Please use Chrome or Edge.");
      return;
    }
    if (micState === "listening") {
      stopListening();
      return;
    }

    setMicError(null);
    const SR = getSpeechRecognition()!;
    const recognition = new SR();
    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    recognitionRef.current = recognition;

    recognition.onstart = () => setMicState("listening");

    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      setInput(transcript);
      setMicState("idle");
    };

    recognition.onerror = (event: any) => {
      setMicState("error");
      if (event.error === "not-allowed" || event.error === "permission-denied") {
        setMicError("Microphone access denied. Please allow microphone permission in your browser.");
      } else if (event.error === "no-speech") {
        setMicError("No speech detected. Please try again.");
      } else if (event.error === "network") {
        setMicError("Network error during speech recognition. Please check your connection.");
      } else {
        setMicError("Speech recognition failed. Please try again.");
      }
      setTimeout(() => setMicState("idle"), 100);
    };

    recognition.onend = () => {
      // Only reset if we didn't already handle it in onresult/onerror
      setMicState((s) => (s === "listening" ? "idle" : s));
    };

    try {
      recognition.start();
    } catch {
      setMicError("Could not start microphone. Please try again.");
      setMicState("idle");
    }
  }

  function stopListening() {
    recognitionRef.current?.stop();
    setMicState("idle");
  }

  /* ── Speaker ──────────────────────────────────────────────────────────── */
  function toggleSpeak(text: string) {
    if (!window.speechSynthesis) {
      setMicError("Text-to-speech is not supported in this browser.");
      return;
    }

    if (speakState === "speaking") {
      window.speechSynthesis.cancel();
      setSpeakState("idle");
      return;
    }

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "en-US";
    utterance.rate = 0.95;
    utterance.pitch = 1;

    utterance.onstart = () => setSpeakState("speaking");
    utterance.onend = () => setSpeakState("idle");
    utterance.onerror = () => setSpeakState("idle");

    window.speechSynthesis.cancel(); // cancel any previous
    window.speechSynthesis.speak(utterance);
  }

  /* ── No profile ───────────────────────────────────────────────────────── */
  if (!profileId) {
    return (
      <EmptyState
        title="No profile yet"
        body="Build a learning path first — the mentor answers using your real profile and roadmap."
        action={
          <Link href="/" className="rounded-md bg-capability px-4 py-2 text-sm font-medium text-ink">
            Get started
          </Link>
        }
      />
    );
  }

  /* ── Render ───────────────────────────────────────────────────────────── */
  const isListening = micState === "listening";
  const isSpeaking = speakState === "speaking";

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-3">
      {/* Chat window */}
      <div className="card flex h-[52vh] min-h-[320px] flex-col overflow-hidden">
        {/* Messages */}
        <div className="flex-1 space-y-3 overflow-y-auto p-4 pr-3">
          {messages.map((m, i) => (
            <div
              key={i}
              className={`flex gap-2 ${m.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[82%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
                  m.role === "user"
                    ? "bg-gradient-to-br from-signal-coral to-signal-amber text-ink"
                    : "bg-ink-softer text-ivory"
                }`}
              >
                {m.content}
              </div>
            </div>
          ))}

          {chatLoading && (
            <div className="flex justify-start">
              <div className="flex items-center gap-1.5 rounded-2xl bg-ink-softer px-4 py-3">
                <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-muted [animation-delay:0ms]" />
                <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-muted [animation-delay:150ms]" />
                <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-muted [animation-delay:300ms]" />
              </div>
            </div>
          )}
          <div ref={endRef} />
        </div>

        {/* Status bar */}
        {(isListening || isSpeaking || micError) && (
          <div
            className={`border-t border-ink-softer px-4 py-2 text-xs ${
              micError
                ? "text-signal-coral"
                : isListening
                ? "text-signal-amber"
                : "text-capability"
            }`}
          >
            {micError
              ? micError
              : isListening
              ? "🎙 Listening… speak now"
              : "🔊 Speaking…"}
          </div>
        )}

        {/* Input row */}
        <div className="border-t border-ink-softer p-3">
          <div className="flex items-center gap-2">
            {/* Mic button */}
            <button
              onClick={startListening}
              disabled={chatLoading}
              aria-label={isListening ? "Stop listening" : "Start voice input"}
              title={
                !speechSupported
                  ? "Voice input not supported in this browser"
                  : isListening
                  ? "Stop listening"
                  : "Start voice input"
              }
              className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-full border transition-all ${
                isListening
                  ? "animate-pulse border-signal-amber bg-signal-amber/20 text-signal-amber"
                  : !speechSupported
                  ? "cursor-not-allowed border-ink-softer text-muted opacity-40"
                  : "border-ink-softer text-muted hover:border-signal-coral/60 hover:text-signal-coral"
              }`}
            >
              <MicIcon />
            </button>

            {/* Text input */}
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  send(input);
                }
              }}
              placeholder={
                isListening
                  ? "Listening…"
                  : chatLoading
                  ? "Thinking…"
                  : "Ask your mentor…"
              }
              disabled={chatLoading}
              className="flex-1 rounded-full border border-ink-softer bg-ink-soft px-4 py-2 text-sm text-ivory placeholder:text-muted focus:border-capability focus:outline-none disabled:opacity-60"
            />

            {/* Speaker button — only shown when there's a reply */}
            {lastReply && (
              <button
                onClick={() => toggleSpeak(lastReply)}
                aria-label={isSpeaking ? "Stop speaking" : "Read last reply aloud"}
                title={isSpeaking ? "Stop speaking" : "Read last reply aloud"}
                className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-full border transition-all ${
                  isSpeaking
                    ? "border-capability bg-capability/20 text-capability"
                    : "border-ink-softer text-muted hover:border-capability/60 hover:text-capability"
                }`}
              >
                <SpeakerIcon active={isSpeaking} />
              </button>
            )}

            {/* Send button */}
            <button
              onClick={() => send(input)}
              disabled={chatLoading || !input.trim()}
              aria-label="Send message"
              className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-signal-coral to-signal-amber text-ink transition-opacity disabled:opacity-40"
            >
              <SendIcon />
            </button>
          </div>
        </div>
      </div>

      {/* Quick suggestions */}
      <div className="flex flex-wrap gap-2">
        {SUGGESTIONS.map((s) => (
          <button
            key={s}
            onClick={() => send(s)}
            disabled={chatLoading}
            className="rounded-full border border-ink-softer px-3 py-1 text-xs text-muted transition-colors hover:border-signal-coral/40 hover:text-ivory disabled:opacity-40"
          >
            {s}
          </button>
        ))}
      </div>
    </div>
  );
}

/* ── Suggestions ──────────────────────────────────────────────────────────── */
const SUGGESTIONS = [
  "What should I learn next?",
  "Which skill is my biggest gap?",
  "Why was this recommended?",
  "Can I skip SQL?",
  "What am I good at?",
];

/* ── Icons (inline SVG — no extra dependency) ─────────────────────────────── */
function MicIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="9" y="2" width="6" height="12" rx="3" />
      <path d="M5 10a7 7 0 0 0 14 0" />
      <line x1="12" y1="19" x2="12" y2="22" />
      <line x1="9" y1="22" x2="15" y2="22" />
    </svg>
  );
}

function SpeakerIcon({ active }: { active: boolean }) {
  return active ? (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
      <path d="M15.54 8.46a5 5 0 0 1 0 7.07" />
      <path d="M19.07 4.93a10 10 0 0 1 0 14.14" />
    </svg>
  ) : (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
      <path d="M15.54 8.46a5 5 0 0 1 0 7.07" />
    </svg>
  );
}

function SendIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <line x1="22" y1="2" x2="11" y2="13" />
      <polygon points="22 2 15 22 11 13 2 9 22 2" />
    </svg>
  );
}
