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

document.addEventListener("DOMContentLoaded", function() {
    var socket = io({
        withCredentials: true
    });
    
    socket.on('connect', function() {
        console.log('Connected to server');
    });
    
    socket.on('redirect', function (data) {
        const targetUrl = data.url;
        console.log(`Redirecting to: ${targetUrl}`);
        window.location.href = targetUrl;
    });

    socket.on('update-rooms', function() {
        console.log('Received update-rooms event');

        socket.emit
        fetchChats();
    })
    
    window.socket = socket;

    fetchChats();

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
            console.log(data);
            if (data) {
                for (const key in data) {
                    const array = data[key]
                    addChatToList(array[0], array[1][0], array[1][1]);
                }
            }
        })
        .catch(error => {
            console.error('Error fetching chats:', error);
        });
    }

});
