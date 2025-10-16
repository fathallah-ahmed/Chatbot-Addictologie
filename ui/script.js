const sendBtn = document.getElementById('send');
const questionInput = document.getElementById('question');
const messages = document.getElementById('messages');

sendBtn.onclick = async () => {
  const q = questionInput.value.trim();
  if (!q) return;
  appendMessage('user', q);
  questionInput.value = '';

  try {
    const res = await fetch('http://127.0.0.1:5000/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: q })
    });
    const data = await res.json();
    if (data.error) appendMessage('bot', `Erreur: ${data.error}`);
    else appendMessage('bot', data.answer);
  } catch (e) {
    appendMessage('bot', 'Erreur réseau: impossible joindre le backend.');
  }
};

function appendMessage(who, text) {
  const el = document.createElement('div');
  el.className = 'msg ' + who;
  el.innerText = (who === 'user' ? 'Vous: ' : 'Bot: ') + text;
  messages.appendChild(el);
  messages.scrollTop = messages.scrollHeight;
}
