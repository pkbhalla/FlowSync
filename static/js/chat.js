// flowsync/static/js/chat.js

document.addEventListener('DOMContentLoaded', () => {
    const chatContainer = document.querySelector('.chat-messages');
    if (!chatContainer) return;

    const currentChannelId = chatContainer.getAttribute('data-channel-id');
    const evtSource = new EventSource('/messages/stream');

    evtSource.onmessage = function(event) {
        const data = JSON.parse(event.data);
        if (data.channel_id == currentChannelId) {
            appendMessage(data);
            scrollToBottom();
        }
        // Update sidebar unread badge if it's another channel
        const channelItem = document.querySelector(`.channel-item[data-id="${data.channel_id}"]`);
        if (channelItem && data.channel_id != currentChannelId) {
            const badge = channelItem.querySelector('.unread-badge');
            if (badge) {
                badge.textContent = parseInt(badge.textContent || 0) + 1;
                badge.style.display = 'inline-block';
            }
        }
    };

    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');

    if (chatForm && chatInput) {
        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const content = chatInput.value.trim();
            if (!content) return;
            
            chatInput.value = ''; // clear immediately
            try {
                await window.apiFetch(`/messages/${currentChannelId}/send`, {
                    method: 'POST',
                    body: JSON.stringify({ content: content })
                });
            } catch (err) {
                chatInput.value = content; // restore on error
            }
        });
    }

    function appendMessage(msg) {
        const div = document.createElement('div');
        div.className = 'message-item';
        div.innerHTML = `
            <div class="avatar" style="background-color: ${msg.sender.avatar_color}">
                ${msg.sender.avatar_initials}
            </div>
            <div class="message-content">
                <div class="message-header">
                    <span class="message-author">${msg.sender.display_name}</span>
                    <span class="message-time">${new Date(msg.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                </div>
                <div class="message-text">${msg.content}</div>
            </div>
        `;
        chatContainer.appendChild(div);
    }

    function scrollToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    scrollToBottom(); // on load
});
