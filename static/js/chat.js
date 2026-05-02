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

        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.style.backgroundColor = msg.sender.avatar_color;
        avatar.textContent = msg.sender.avatar_initials;
        avatar.setAttribute('aria-hidden', 'true');

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        const headerDiv = document.createElement('div');
        headerDiv.className = 'message-header';

        const authorSpan = document.createElement('span');
        authorSpan.className = 'message-author';
        authorSpan.textContent = msg.sender.display_name;

        const timeEl = document.createElement('time');
        timeEl.className = 'message-time';
        timeEl.setAttribute('datetime', msg.created_at);
        timeEl.textContent = new Date(msg.created_at).toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'});

        headerDiv.appendChild(authorSpan);
        headerDiv.appendChild(timeEl);

        const textDiv = document.createElement('div');
        textDiv.className = 'message-text';
        textDiv.textContent = msg.content;

        contentDiv.appendChild(headerDiv);
        contentDiv.appendChild(textDiv);

        div.appendChild(avatar);
        div.appendChild(contentDiv);
        chatContainer.appendChild(div);
    }

    function scrollToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    scrollToBottom(); // on load
});
