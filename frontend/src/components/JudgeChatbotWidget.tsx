'use client';

import { useState, useRef, useEffect } from 'react';
import {
  X,
  Send,
  Sparkles,
  RefreshCw,
  Bot,
  User,
  Trash2,
} from 'lucide-react';
import clsx from 'clsx';
import { streamJudgeChatbot, askJudgeChatbot, ChatMessage } from '@/lib/api';

// ... (renderMarkdown and renderInline remain the same)

// ─── Minimal Markdown Renderer ────────────────────────────────────────────────
// Converts **bold**, *italic*, `code`, bullet lists, and numbered lists
// to React elements without any external dependency.
function renderMarkdown(text: string): React.ReactNode {
  const lines = text.split('\n');
  const elements: React.ReactNode[] = [];
  let listItems: string[] = [];
  let listType: 'ul' | 'ol' | null = null;

  const flushList = (key: string) => {
    if (listItems.length === 0) return;
    if (listType === 'ul') {
      elements.push(
        <ul key={key} className="list-disc list-inside space-y-1 my-2 pl-1">
          {listItems.map((li, i) => (
            <li key={i} className="text-slate-700 leading-relaxed">
              {renderInline(li)}
            </li>
          ))}
        </ul>
      );
    } else {
      elements.push(
        <ol key={key} className="list-decimal list-inside space-y-1 my-2 pl-1">
          {listItems.map((li, i) => (
            <li key={i} className="text-slate-700 leading-relaxed">
              {renderInline(li)}
            </li>
          ))}
        </ol>
      );
    }
    listItems = [];
    listType = null;
  };

  lines.forEach((line, idx) => {
    const trimmed = line.trim();

    // Heading levels  (### ## #)
    const h3 = trimmed.match(/^### (.+)/);
    const h2 = trimmed.match(/^## (.+)/);
    const h1 = trimmed.match(/^# (.+)/);

    if (h3 || h2 || h1) {
      flushList(`list-${idx}`);
      const content = (h3 || h2 || h1)![1];
      elements.push(
        <p key={idx} className="font-semibold text-slate-800 mt-3 mb-1 text-[12px] uppercase tracking-wide">
          {renderInline(content)}
        </p>
      );
      return;
    }

    // Dividers
    if (trimmed === '---' || trimmed === '***') {
      flushList(`list-${idx}`);
      elements.push(<hr key={idx} className="border-slate-200 my-2" />);
      return;
    }

    // Unordered list bullets: * item / - item / • item
    const ulMatch = trimmed.match(/^[\*\-•] (.+)/);
    if (ulMatch) {
      if (listType !== 'ul') {
        flushList(`list-${idx}`);
        listType = 'ul';
      }
      listItems.push(ulMatch[1]);
      return;
    }

    // Ordered list: 1. item
    const olMatch = trimmed.match(/^\d+[\.\)] (.+)/);
    if (olMatch) {
      if (listType !== 'ol') {
        flushList(`list-${idx}`);
        listType = 'ol';
      }
      listItems.push(olMatch[1]);
      return;
    }

    // Empty line
    if (trimmed === '') {
      flushList(`list-${idx}`);
      if (elements.length > 0) {
        elements.push(<div key={idx} className="h-1.5" />);
      }
      return;
    }

    flushList(`list-${idx}`);
    elements.push(
      <p key={idx} className="leading-relaxed text-slate-700">
        {renderInline(trimmed)}
      </p>
    );
  });

  flushList('final-list');
  return <>{elements}</>;
}

function renderInline(text: string): React.ReactNode {
  // Pattern matches: **bold**, *italic*, `code`, and plain text between them
  const parts = text.split(/(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/g);
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={i} className="font-semibold text-slate-900">{part.slice(2, -2)}</strong>;
    }
    if (part.startsWith('*') && part.endsWith('*')) {
      return <em key={i} className="italic">{part.slice(1, -1)}</em>;
    }
    if (part.startsWith('`') && part.endsWith('`')) {
      return (
        <code key={i} className="bg-slate-100 text-indigo-700 rounded px-1 py-0.5 text-[10px] font-mono">
          {part.slice(1, -1)}
        </code>
      );
    }
    return part;
  });
}
// ──────────────────────────────────────────────────────────────────────────────

export function JudgeChatbotWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content:
        "Hi! I'm the **Aegis AI Assistant**. Ask me anything about how this risk engine works — what the metrics mean, how decisions are made, how the system learns over time, or how we keep false positives low. I can explain everything you see on the dashboard in plain terms.",
    },
  ]);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const tokenQueueRef = useRef<string[]>([]);
  const isDrainingRef = useRef<boolean>(false);
  const streamFinishedRef = useRef<boolean>(false);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  // Progressive Typewriter Drain Loop
  const startDrainingQueue = () => {
    if (isDrainingRef.current) return;
    isDrainingRef.current = true;
    setIsTyping(true);

    const intervalId = setInterval(() => {
      if (tokenQueueRef.current.length > 0) {
        // Take next word/token chunk
        const nextChunk = tokenQueueRef.current.shift()!;
        setMessages((prev) => {
          const updated = [...prev];
          const lastIdx = updated.length - 1;
          if (lastIdx >= 0 && updated[lastIdx].role === 'assistant') {
            updated[lastIdx] = {
              ...updated[lastIdx],
              content: updated[lastIdx].content + nextChunk,
            };
          }
          return updated;
        });
      } else if (streamFinishedRef.current) {
        // Queue is completely empty and backend stream finished
        clearInterval(intervalId);
        isDrainingRef.current = false;
        setIsTyping(false);
        setLoading(false);
      }
    }, 20); // 20ms per token for smooth realistic typewriter flow
  };

  const quickPrompts = [
    'What does the risk score mean?',
    'How does the system learn new fraud patterns?',
    'What is auto-block vs manual review?',
    'How are net savings calculated?',
  ];

  const handleSend = async (textToSend?: string) => {
    const text = (textToSend || inputMessage).trim();
    if (!text || loading || isTyping) return;

    const userMsg: ChatMessage = { role: 'user', content: text };
    const newHistory = [...messages, userMsg];
    // Add user message + placeholder assistant message immediately
    setMessages([...newHistory, { role: 'assistant', content: '' }]);
    setInputMessage('');
    setLoading(true);
    setIsTyping(true);
    tokenQueueRef.current = [];
    isDrainingRef.current = false;
    streamFinishedRef.current = false;

    try {
      await streamJudgeChatbot(
        {
          message: text,
          history: newHistory,
        },
        (token: string) => {
          // Break token into smaller words/chunks if needed for ultra-smooth typing
          const words = token.split(/(\s+)/);
          for (const w of words) {
            if (w) tokenQueueRef.current.push(w);
          }
          startDrainingQueue();
        },
        () => {
          streamFinishedRef.current = true;
          startDrainingQueue();
        },
        (err: any) => {
          console.error('Chatbot streaming failed:', err);
          streamFinishedRef.current = true;
          setLoading(false);
          setIsTyping(false);
          setMessages((prev) => {
            const updated = [...prev];
            const lastIdx = updated.length - 1;
            if (lastIdx >= 0 && updated[lastIdx].role === 'assistant' && !updated[lastIdx].content) {
              updated[lastIdx] = {
                role: 'assistant',
                content:
                  '⚠️ Sorry, I hit a temporary connection issue. Please make sure the backend server is running.',
              };
            }
            return updated;
          });
        }
      );
    } catch (err: any) {
      console.error('Chatbot request failed:', err);
      streamFinishedRef.current = true;
      setLoading(false);
      setIsTyping(false);
      setMessages((prev) => {
        const updated = [...prev];
        const lastIdx = updated.length - 1;
        if (lastIdx >= 0 && updated[lastIdx].role === 'assistant' && !updated[lastIdx].content) {
          updated[lastIdx] = {
            role: 'assistant',
            content:
              '⚠️ Sorry, I hit a temporary connection issue. Please make sure the backend server is running.',
          };
        }
        return updated;
      });
    }
  };

  const handleClear = () => {
    tokenQueueRef.current = [];
    streamFinishedRef.current = true;
    setIsTyping(false);
    setLoading(false);
    setMessages([
      {
        role: 'assistant',
        content:
          'Chat cleared! Ask me anything about how Aegis-RTO works, what the dashboard numbers mean, or how the system adapts to new fraud patterns.',
      },
    ]);
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 font-sans">
      {/* Floating Trigger Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="group flex items-center gap-2.5 px-4 py-3 rounded-2xl bg-gradient-to-r from-indigo-600 via-indigo-700 to-purple-700 text-white shadow-xl shadow-indigo-600/30 hover:shadow-indigo-600/40 hover:scale-105 active:scale-95 transition-all duration-200 border border-indigo-400/30"
          title="Ask Aegis AI Assistant"
        >
          <div className="relative">
            <Sparkles className="w-5 h-5 text-indigo-200 animate-pulse" />
          </div>
          <div className="text-left">
            <span className="block text-xs font-black tracking-wide leading-none">
              Aegis AI Assistant
            </span>
            <span className="block text-[10px] text-indigo-200/90 font-mono mt-0.5">
              Ask me anything about this dashboard
            </span>
          </div>
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className="w-[420px] max-w-[calc(100vw-32px)] h-[580px] max-h-[calc(100vh-80px)] bg-white rounded-3xl border border-slate-200 shadow-2xl flex flex-col overflow-hidden animate-fade-in">
          {/* Header */}
          <div className="p-4 bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white flex items-center justify-between border-b border-slate-800">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-indigo-600/30 border border-indigo-400/40 flex items-center justify-center">
                <Bot className="w-4 h-4 text-indigo-300" />
              </div>
              <div>
                <h3 className="text-xs font-bold text-white flex items-center gap-1.5">
                  Aegis AI Assistant
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 inline-block animate-ping" />
                </h3>
                <p className="text-[10px] text-indigo-300 font-mono">
                  Grounded · Honest · Defense-Only
                </p>
              </div>
            </div>

            <div className="flex items-center gap-1">
              <button
                onClick={handleClear}
                className="p-1.5 rounded-lg hover:bg-white/10 text-slate-400 hover:text-white transition"
                title="Clear Chat"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1.5 rounded-lg hover:bg-white/10 text-slate-400 hover:text-white transition"
                title="Close"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Quick Prompts */}
          <div className="p-2.5 bg-slate-50 border-b border-slate-100 flex items-center gap-2 overflow-x-auto no-scrollbar">
            {quickPrompts.map((prompt, idx) => (
              <button
                key={idx}
                onClick={() => handleSend(prompt)}
                disabled={loading || isTyping}
                className="shrink-0 px-2.5 py-1 rounded-full bg-white hover:bg-indigo-50 border border-slate-200 hover:border-indigo-200 text-[11px] font-medium text-slate-700 hover:text-indigo-700 transition shadow-2xs truncate max-w-[200px]"
              >
                {prompt}
              </button>
            ))}
          </div>

          {/* Messages */}
          <div className="flex-1 p-4 overflow-y-auto space-y-4 bg-slate-50/40">
            {messages.map((msg, index) => {
              const isAssistant = msg.role === 'assistant';
              // If assistant message is empty, don't show empty bubble
              if (isAssistant && !msg.content) return null;

              const isStreamingLast =
                isAssistant && index === messages.length - 1 && (loading || isTyping);

              return (
                <div
                  key={index}
                  className={clsx(
                    'flex gap-2.5 text-xs',
                    isAssistant ? 'justify-start' : 'justify-end'
                  )}
                >
                  {isAssistant && (
                    <div className="w-7 h-7 rounded-lg bg-indigo-100 border border-indigo-200 flex items-center justify-center text-indigo-700 shrink-0 mt-0.5">
                      <Bot className="w-3.5 h-3.5" />
                    </div>
                  )}

                  <div
                    className={clsx(
                      'p-3.5 rounded-2xl max-w-[85%] shadow-2xs text-xs',
                      isAssistant
                        ? 'bg-white border border-slate-200 text-slate-800'
                        : 'bg-indigo-600 text-white font-medium'
                    )}
                  >
                    {isAssistant ? (
                      <div className="space-y-0.5">
                        {renderMarkdown(msg.content)}
                        {isStreamingLast && (
                          <span className="inline-block w-1.5 h-3.5 bg-indigo-500 ml-1 animate-pulse align-middle rounded-xs" />
                        )}
                      </div>
                    ) : (
                      <span className="leading-relaxed">{msg.content}</span>
                    )}
                  </div>

                  {!isAssistant && (
                    <div className="w-7 h-7 rounded-lg bg-slate-800 flex items-center justify-center text-white shrink-0 mt-0.5">
                      <User className="w-3.5 h-3.5" />
                    </div>
                  )}
                </div>
              );
            })}

            {loading && !messages[messages.length - 1]?.content && (
              <div className="flex gap-2.5 text-xs justify-start items-center text-slate-400">
                <div className="w-7 h-7 rounded-lg bg-indigo-100 border border-indigo-200 flex items-center justify-center text-indigo-700 shrink-0">
                  <Bot className="w-3.5 h-3.5" />
                </div>
                <div className="p-3 rounded-2xl bg-white border border-slate-200 flex items-center gap-2">
                  <RefreshCw className="w-3.5 h-3.5 animate-spin text-indigo-600" />
                  <span className="text-[11px] text-slate-500 font-mono">
                    Thinking...
                  </span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>


          {/* Input */}
          <div className="p-3 bg-white border-t border-slate-100">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSend();
              }}
              className="flex items-center gap-2"
            >
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Ask about the dashboard, metrics, or how it works..."
                disabled={loading || isTyping}
                className="flex-1 px-4 py-2.5 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white text-xs text-slate-900 placeholder:text-slate-400 transition"
              />
              <button
                type="submit"
                disabled={!inputMessage.trim() || loading || isTyping}
                className="p-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 disabled:opacity-40 text-white transition active:scale-95 shadow-xs"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
            <div className="mt-1.5 flex items-center justify-between text-[10px] text-slate-400 font-mono px-1">
              <span>Defense-Only · Grounded Responses</span>
              <span>Aegis AI · Powered by Gemini</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
