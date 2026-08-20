(function () {
  const counter = document.getElementById("counter");
  const form = document.getElementById("ticket-form");
  const input = document.getElementById("ticket-input");
  const submitBtn = document.getElementById("ticket-submit");

  const botTemplate = document.getElementById("bot-msg-template");
  const userTemplate = document.getElementById("user-msg-template");
  const typingTemplate = document.getElementById("typing-template");

  const STAMP_LABELS = {
    verified: "verified",
    likely: "likely",
    uncertain: "uncertain",
  };

  function scrollToBottom() {
    counter.scrollTop = counter.scrollHeight;
  }

  function addUserMessage(text) {
    const node = userTemplate.content.cloneNode(true);
    node.querySelector(".msg__bubble p").textContent = text;
    counter.appendChild(node);
    scrollToBottom();
  }

  function addBotMessage({ reply, intent, confidence, tier }) {
    const node = botTemplate.content.cloneNode(true);
    const stamp = node.querySelector(".stamp");
    const label = node.querySelector(".stamp__label");
    const meta = node.querySelector(".stamp__meta");

    stamp.classList.add(`stamp--${tier}`);
    label.textContent = STAMP_LABELS[tier] || tier;
    meta.textContent = `${intent} · ${Math.round(confidence * 100)}%`;

    node.querySelector(".msg__bubble p").textContent = reply;
    counter.appendChild(node);
    scrollToBottom();
  }

  function showTyping() {
    const node = typingTemplate.content.cloneNode(true);
    counter.appendChild(node);
    scrollToBottom();
  }

  function removeTyping() {
    const el = document.getElementById("typing-indicator");
    if (el) el.remove();
  }

  async function sendMessage(message) {
    showTyping();
    submitBtn.disabled = true;

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });

      if (!res.ok) {
        throw new Error(`Request failed: ${res.status}`);
      }

      const data = await res.json();
      removeTyping();
      addBotMessage(data);
    } catch (err) {
      removeTyping();
      addBotMessage({
        reply: "The desk is temporarily unreachable. Please try again in a moment.",
        intent: "error",
        confidence: 0,
        tier: "uncertain",
      });
      console.error(err);
    } finally {
      submitBtn.disabled = false;
      input.focus();
    }
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    const message = input.value.trim();
    if (!message) return;

    addUserMessage(message);
    input.value = "";
    sendMessage(message);
  });
})();
