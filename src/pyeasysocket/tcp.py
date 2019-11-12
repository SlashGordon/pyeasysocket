import threading
import socket
import socketserver
from pyeasysocket.base import BaseSocket, BaseQueue
from queue import Full, Empty


class ThreadingTCPServer(
    socketserver.ThreadingMixIn, socketserver.TCPServer, BaseQueue
):
    def __init__(
        self, server_address, handler_class, maxsize=100, timeout=None
    ):
        BaseQueue.__init__(self, maxsize, timeout)
        socketserver.TCPServer.__init__(self, server_address, handler_class)

    daemon_threads = True


class TCPServer(threading.Thread, BaseSocket, ThreadingTCPServer):
    def __init__(
        self,
        host,
        port,
        request_handler,
        maxsize=100,
        timeout=None,
        daemon=True,
        buffersize=4096,
        encoding="ascii"
    ):
        threading.Thread.__init__(self)
        BaseSocket.__init__(self, host, port, buffersize, encoding)
        ThreadingTCPServer.__init__(
            self, (host, port), request_handler, maxsize, timeout
        )

        self.daemon = daemon
        self.is_closing = False

    def join(self):
        self.is_closing = True
        self.shutdown()
        return super().join()

    def run(self):
        self.serve_forever()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.join()


class TCPStreamingRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        while not self.server.is_closing:
            try:
                data = self.server.data_wait
                if not isinstance(data, bytes):
                    data = str.encode(data, self.server.encoding)
                self.request.sendall(data)
            except (ConnectionError, Empty):
                break


class TCPStreamingServer(TCPServer):
    def __init__(
        self,
        host,
        port,
        request_handler=TCPStreamingRequestHandler,
        max_queue_size=100,
        timeout=None,
        daemon=True,
        buffersize=4096,
        encoding="ascii"
    ):
        super().__init__(
            host,
            port,
            request_handler,
            max_queue_size,
            timeout,
            daemon,
            buffersize,
            encoding
        )


class TCPReceiverRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        while not self.server.is_closing:
            try:
                data_byte = self.request.recv(self.server.buffersize).strip()
                try:
                    data = str(data_byte, self.server.encoding)
                    if len(data) > 0:
                        self.server.data = (data, self.client_address)
                except Full:
                    pass
            except ConnectionError:
                break


class TCPReceiver(TCPServer):
    def __init__(
        self,
        host,
        port,
        request_handler=TCPReceiverRequestHandler,
        max_queue_size=100,
        timeout=None,
        daemon=True,
        buffersize=4096,
        encoding="ascii"
    ):
        super().__init__(
            host,
            port,
            request_handler,
            max_queue_size,
            timeout,
            daemon,
            buffersize,
            encoding
        )


class TCPClient(BaseSocket):
    def __init__(self, ip, port, buffersize=4096, encoding="ascii"):
        BaseSocket.__init__(self, ip, port, buffersize, encoding)
        self._ip = ip
        self._port = port

    def send(self, message):
        if not isinstance(message, bytes):
            message = str.encode(message, self.encoding)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(self.address)
            sent = sock.sendall(message)
        return sent

    def receive(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(self.address)
            data_byte = sock.recv(self.buffersize)
            return (str(data_byte, self.encoding), self.address)
