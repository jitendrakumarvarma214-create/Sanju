const yearNode = document.getElementById('year');
const leadForm = document.getElementById('leadForm');
const leadFormStatus = document.getElementById('leadFormStatus');
const chatForm = document.getElementById('chatForm');
const chatInput = document.getElementById('chatInput');
const chatLog = document.getElementById('chatLog');

if (yearNode) {
  yearNode.textContent = new Date().getFullYear();
}

function appendChatMessage(role, message) {
  if (!chatLog) {
    return;
  }

  const node = document.createElement('p');
  node.className = role;
  node.textContent = message;
  chatLog.appendChild(node);
  chatLog.scrollTop = chatLog.scrollHeight;
}

async function postJson(url, payload) {
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || 'Request failed');
  }

  return data;
}

if (leadForm) {
  leadForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const payload = Object.fromEntries(new FormData(leadForm).entries());

    leadFormStatus.textContent = 'Sending your request...';
    leadFormStatus.classList.remove('error');

    try {
      await postJson('/api/contact', payload);
      leadForm.reset();
      leadFormStatus.textContent = 'Thanks! Our team will contact you shortly.';
    } catch (error) {
      leadFormStatus.textContent = error.message;
      leadFormStatus.classList.add('error');
    }
  });
}

if (chatForm && chatInput) {
  chatForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const message = chatInput.value.trim();
    if (!message) {
      return;
    }

    appendChatMessage('user', message);
    chatInput.value = '';

    try {
      const response = await postJson('/api/support-bot', { message });
      appendChatMessage('bot', response.reply);
    } catch (error) {
      appendChatMessage('bot', `Sorry, I had an issue: ${error.message}`);
    }
  });
}
