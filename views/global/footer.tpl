<footer class="footer">
    <div class="container">
        <p class="text-muted">&copy; 2015 count.re</p>
    </div>
</footer>

<script src="/static/js/jquery.min.js"></script>
<script src="/static/js/bootstrap.min.js"></script>
% if defined('id'):
<script>
    $(document).ready(function() {
        if (!window.WebSocket) {
            if (window.MozWebSocket) {
                window.WebSocket = window.MozWebSocket;
            } else {
                console.log('Your client does not support websockets. Disabled.')
            }
        }
        ws = new WebSocket('wss://' + location.host + '/websocket');
        ws.onopen = function(evt) {
            console.log('Established websockets connection to wss://' + location.host + '/websocket')
        }
        ws.onmessage = function(evt) {
            $('p#counterVal').text(evt.data);
        }
        ws.onclose = function(evt) {
            console.log('Closed websockets connection to wss://' + location.host + '/websocket')
        }
        window.setInterval(function() {
			ws.send("{{id}}");
		}, 1000);
    });
</script>
% end
</body>
</html>