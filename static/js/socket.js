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