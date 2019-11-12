import socket
import threading
import socketserver
from queue import Full
from pyeasysocket.base import BaseSocket, BaseQueue


class ThreadingUDPServer(
    socketserver.ThreadingMixIn, BaseQueue, socketserver.UDPServer
):
    def __init__(
        self, server_address, handler_class, maxsize, timeout,
    ):
        BaseQueue.__init__(self, maxsize, timeout)
        socketserver.TCPServer.__init__(self, server_address, handler_class)

    daemon_threads = True


class UdpServer(threading.Thread, BaseSocket, ThreadingUDPServer):
    def __init__(
        self,
        host,
        port,
        request_handler,
        maxsize=100,
        timeout=None,
        daemon=True,
        buffersize=4096,
        encoding="ascii",
    ):
        threading.Thread.__init__(self)
        BaseSocket.__init__(self, host, port, buffersize, encoding)
        ThreadingUDPServer.__init__(
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


class UDPClient(BaseSocket):
    def __init__(self, ip, port, buffersize=4096, encoding="ascii"):
        BaseSocket.__init__(self, ip, port, buffersize, encoding)
        self._ip = ip
        self._port = port

    def send(self, message):
        if not isinstance(message, bytes):
            message = str.encode(message)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sent = sock.sendto(message, self.address)
        return sent

    def receive(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            data_byte = sock.recv(self.buffersize)
            return (str(data_byte, self.encoding), self.address)


class UDPeceiverRequestHandler(socketserver.DatagramRequestHandler):
    def handle(self):
        while not self.server.is_closing:
            try:
                data_byte = self.rfile.readline().strip()
                try:
                    data = str(data_byte, self.server.encoding)
                    if len(data) > 0:
                        self.server.data = (data, self.client_address)
                except Full:
                    pass
            except ConnectionError:
                break


class UDPReceiver(UdpServer):
    def __init__(
        self,
        host,
        port,
        request_handler=UDPeceiverRequestHandler,
        max_queue_size=100,
        timeout=None,
        daemon=True,
        buffersize=4096,
        encoding="ascii",
    ):
        super().__init__(
            host,
            port,
            request_handler,
            max_queue_size,
            timeout,
            daemon,
            buffersize,
            encoding,
        )
