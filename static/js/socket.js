function openChat(chatId) {
    console.log(`Opening chat: ${chatId}`);
    window.location.href = `/chat/${chatId}`;
}

function addChatToList(roomId, username, last_active, last_message) {
    const chatList = document.getElementById('chat-list');
    
    if (document.getElementById(`chat-${roomId}`)) {
        const element = document.getElementById(`chat-${roomId}`);
        element.remove();
    }
    
    const chatElement = document.createElement('div');
    chatElement.id = `chat-${roomId}`;
    chatElement.className = 'chat-item';
    chatElement.onclick = function() {
        openChat(roomId);
    }
    
    const usernameElem = document.createElement('p');
    usernameElem.className = 'chat-username';
    usernameElem.textContent = username;

    const lastMessageElem = document.createElement('p');
    lastMessageElem.className = 'chat-last-message';
    lastMessageElem.textContent = last_message || 'No messages yet';

    const timestamp = new Date(last_active);
    const timestampElem = document.createElement('p');
    timestampElem.className = 'chat-timestamp';
    if (isToday(timestamp)) {
        timestampElem.textContent = timestamp.toLocaleTimeString();
    } else {
        timestampElem.textContent = timestamp.toLocaleString();
    }

    chatElement.appendChild(usernameElem);
    chatElement.appendChild(lastMessageElem);
    chatElement.appendChild(timestampElem);
    
    chatList.appendChild(chatElement);
}

function fetchChats() {
    const chatList = document.getElementById('chat-list');
    chatList.innerHTML = '';

    fetch('/get-chats', {
        method: 'GET',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            if (response.status === 401) {
                window.socket.emit('redirect', { url: '/login' });
            }
        }
        return response.json();
    })
    .then(data => {
        if (data && Object.keys(data).length > 0) {
            for (const key in data) {
                const array = data[key]
                addChatToList(array[0], array[1][1], array[1][2], array[1][3]);
            }
        } else {
            const noChatsMessage = document.createElement('p');
            noChatsMessage.textContent = 'You haven\'t started any chats yet, start a new chat by clicking a user\'s name';
            noChatsMessage.className = 'no-chats-message';
            chatList.appendChild(noChatsMessage);
        }
    })
    .catch(error => {
        console.error('Error fetching chats:', error);
        alert('An error occured while loading chats');
    });
}

function deleteContent(url) {
    fetch(url, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-TOKEN': getCookie('csrf_access_token')
        }
    })
    .then(async response => {
        const data = await response.json();
        if (response.ok) {
            location.reload();
        } else {
            alert(data.error);
        }
    })
    .catch(error => console.error('Error:', error));
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

function updateCharCounter(textarea, charCounter, maxChars) {
    const currentLength = textarea.value.length;
    charCounter.textContent = `${textarea.value.length}/${maxChars}`;
    if (currentLength > maxChars) {
        charCounter.classList.add('exceeded');
        textarea.classList.add('input-error');
    } else {
        charCounter.classList.remove('exceeded');
        textarea.classList.remove('input-error');
    }
}

function isToday(date) {
    const today = new Date();
    return date.getDate() === today.getDate() &&
           date.getMonth() === today.getMonth() &&
           date.getFullYear() === today.getFullYear();
}

document.addEventListener("DOMContentLoaded", function() {
    var socket = io({
        withCredentials: true
    });
    
    socket.on('connect', function() {
        fetchChats();
        console.log('Connected to server');
    });
    
    socket.on('redirect', function (data) {
        const targetUrl = data.url;
        console.log(`Redirecting to: ${targetUrl}`);
        window.location.href = targetUrl;
    });

    socket.on('update-rooms', function() {
        console.log('Received update-rooms event');

        fetchChats();
    });

    socket.on('error', function(error) {
        alert(error.msg);
    });

    socket.on('refresh-token', function() {
        console.log('Received refresh-token event');
        fetch('/refresh', {
            method: 'GET',
            credentials: 'include'
        })
        .then(response => {
            if (response.ok) {
                socket.emit('refreshed', { token: data.token });
            } else {
                throw new Error('Token refresh failed');
            }
        })
        .catch(error => {
            console.error('Error refreshing token:', error);
        });
    });

    socket.on('join-room', function(data) {
        socket.emit('join', { room_id: data.room});
    });
    
    window.socket = socket;
});
