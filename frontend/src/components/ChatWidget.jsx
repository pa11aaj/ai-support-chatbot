import { useEffect, useRef, useState } from "react";
import "./ChatWidget.css";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const WELCOME_MESSAGE = {
  role: "assistant",
  content: "Hi! I'm Aria, your support assistant. Ask me about a product or an order.",
};

export default function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([WELCOME_MESSAGE]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, open]);

  async function sendMessage(e) {
    e.preventDefault();
    const text = input.trim();
    if (!text || loading) return;

    const nextMessages = [...messages, { role: "user", content: text }];
    setMessages(nextMessages);
    setInput("");
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_URL}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: nextMessages }),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `Request failed (${res.status})`);
      }

      const data = await res.json();
      setMessages((prev) => [...prev, { role: "assistant", content: data.reply }]);
    } catch (err) {
      setError(err.message || "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="chat-widget">
      {open && (
        <div className="chat-panel">
          <div className="chat-header">
            <span>Aria - Support</span>
            <button onClick={() => setOpen(false)} aria-label="Close chat">
              x
            </button>
          </div>

          <div className="chat-messages" ref={scrollRef}>
            {messages.map((m, i) => (
              <div key={i} className={`chat-bubble ${m.role}`}>
                {m.content}
              </div>
            ))}
            {loading && <div className="chat-bubble assistant typing">Typing...</div>}
            {error && <div className="chat-error">{error}</div>}
          </div>

          <form className="chat-input-row" onSubmit={sendMessage}>
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type a message..."
              disabled={loading}
            />
            <button type="submit" disabled={loading || !input.trim()}>
              Send
            </button>
          </form>
        </div>
      )}

      <button className="chat-toggle" onClick={() => setOpen((v) => !v)}>
        {open ? "Close" : "Chat with us"}
      </button>
    </div>
  );
}
