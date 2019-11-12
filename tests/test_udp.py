import unittest
from pyeasysocket.udp import UDPClient, UDPReceiver
import time


class TestUDPServer(unittest.TestCase):
    address = ("localhost", 8788)

    def test_receiver(self):
        client = UDPClient(*TestUDPServer.address)
        with UDPReceiver(*TestUDPServer.address) as receiver:
            self.assertIsNotNone(receiver)
            self.assertIsNotNone(client)
            self.assertTrue(receiver.is_alive())
            send_msgs = ["test msg 1", "test msg 2", "test msg 3"]
            send_msgs_byte = [b"test msg 1", b"test msg 2", b"test msg 3"]

            def send(x):
                client.send(x)
                # wait for receive
                time.sleep(1)

            list(map(send, send_msgs))
            list(map(send, send_msgs_byte))
            check_data = send_msgs + send_msgs
            for dat in check_data:
                self.assertEqual(receiver.data[0], dat)
