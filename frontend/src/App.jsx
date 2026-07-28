import ChatWidget from "./components/ChatWidget.jsx";

export default function App() {
  return (
    <div className="demo-page">
      <h1>Demo Store</h1>
      <p>
        This page stands in for a real e-commerce site. The chat bubble in
        the bottom-right corner is the AI support widget - click it to try
        product questions or order lookups.
      </p>
      <div className="demo-hint">
        Try asking: <br />
        <code>"What's the price of the Aurora headphones?"</code>
        <br />
        <code>"Where's my order ord-1001?"</code>
        <br />
        <code>"Do you have the Pulse water bottle in stock?"</code>
      </div>
      <ChatWidget />
    </div>
  );
}
