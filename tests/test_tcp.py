import unittest
import time
from pyeasysocket.tcp import TCPClient, TCPReceiver, TCPStreamingServer
from queue import Full, Empty


class TestTCPServer(unittest.TestCase):
    address = ("localhost", 8788)

    def test_queue(self):
        test = TCPStreamingServer(
            *TestTCPServer.address, max_queue_size=2, timeout=0.1
        )
        test.data_raise = "test1"
        test.data_raise = "test2"
        with self.assertRaises(Full):
            test.data_raise = "test3"

        self.assertEqual(test.data_raise, "test1")
        self.assertEqual(test.data_raise, "test2")
        with self.assertRaises(Empty):
            val = test.data_raise
            print(val)

        with self.assertRaises(Empty):
            print(test.data_wait)

        test.data_wait = "test3"
        test.data_wait = "test3"
        with self.assertRaises(Full):
            test.data_wait = "test3"

    def test_receiver(self):
        client = TCPClient(*TestTCPServer.address)
        with TCPReceiver(*TestTCPServer.address) as receiver:
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

    def test_streamer(self):
        with TCPStreamingServer(*TestTCPServer.address, timeout=0.1) as streamer:
            streamer.data = "test1"
            client = TCPClient(*TestTCPServer.address)
            test_data = client.receive()
            time.sleep(0.5)
            self.assertEqual(len(test_data), 2)
            self.assertEqual(test_data[0], "test1")
            streamer.data = "test2"
            test_data = client.receive()
            time.sleep(0.5)
            self.assertEqual(len(test_data), 2)
            self.assertEqual(test_data[0], "test2")
            streamer.data = b"test3"
            test_data = client.receive()
            time.sleep(0.5)
            self.assertEqual(len(test_data), 2)
            self.assertEqual(test_data[0], "test3")
