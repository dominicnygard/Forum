function openChat(chatId) {
    console.log(`Opening chat: ${chatId}`);
    window.location.href = `/chat/${chatId}`;
}

function addChatToList(roomId, userId, username) {
    const chatList = document.getElementById('chat-list');
    
    if (document.getElementById(`chat-${roomId}`)) {
        const element = document.getElementById(`chat-${roomId}`);
        element.remove();
    }
    
    const chatElement = document.createElement('div');
    chatElement.id = `chat-${roomId}`;
    chatElement.className = 'chat-item';
    
    chatElement.innerHTML = `
    <p><strong>Chat with:</strong> ${username}</p>
    <button onclick="openChat('${roomId}')">Open Chat</button>
    `;
    
    chatList.appendChild(chatElement);
}

function fetchChats() {
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
                return fetch('/refresh', {
                    method: 'GET',
                    credentials: 'include'
                }).then(refreshResponse => {
                    if (refreshResponse.ok) {
                        return fetch('/get-chats', {
                            method: 'GET',
                            credentials: 'include',
                            headers: {
                                'Content-Type': 'application/json'
                            }
                        });
                    } else {
                        //window.location.href = '/login';
                        throw new Error('Token refresh failed');
                    }
            });
        }
    }
    return response.json();
    })
    .then(data => {
        if (data) {
            for (const key in data) {
                const array = data[key]
                addChatToList(array[0], array[1][0], array[1][1]);
            }
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
    .then(response => response.json())
    .then(data => {
        if (data.msg) {
            location.reload();
        } else {
            alert('An error occured while deleting content');
        }
    })
    .catch(error => console.error('Error:', error));
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
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
