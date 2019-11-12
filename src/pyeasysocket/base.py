from queue import Queue, Full, Empty


class BaseSocket:
    def __init__(self, ip, port, buffersize, encoding):
        self._ip = ip
        self._port = port
        self._buffersize = buffersize
        self._encoding = encoding

    @property
    def encoding(self):
        return self._encoding

    @property
    def buffersize(self):
        return self._buffersize

    @buffersize.setter
    def buffersize(self, val):
        self._buffersize = val

    @property
    def ip(self):
        return self._ip

    @property
    def port(self):
        return self._port

    @property
    def address(self):
        return (self._ip, self._port)


class BaseQueue(Queue):

    def __init__(self, maxsize, timeout=None):
        """ Queue helper class

        Args:
            maxsize (int): Create a queue object with a given maximum size.
            0 means infinite.
            time_out (int, optional): timeout of waiting block in seconds.
            Defaults to None.
        """
        Queue.__init__(self, maxsize)
        self._timeout = timeout

    @property
    def data(self):
        """ Remove and return an item from the queue without blocking.

        Returns:
            object: if empty None otherwise last item
        """
        try:
            return self.get_nowait()
        except Empty:
            return None

    @data.setter
    def data(self, data):
        """ Add an item to the queue without blocking.

        Args:
            data (object): The data is added to the Queue.
            When the queue is full, the data is ignored.
        """
        try:
            self.put_nowait(data)
        except Full:
            pass

    @property
    def data_raise(self):
        """ Remove and return an item from the queue without blocking.

        Only get an item if one is immediately available. Otherwise
        raise the Empty exception.

        Returns:
            object: if empty raises Empty exception otherwise last item
        """
        return self.get_nowait()

    @data_raise.setter
    def data_raise(self, data):
        """ Add an item to the queue without blocking.

        Only enqueue the item if a free slot is immediately available.
        Otherwise raise the Full exception.

        Args:
            data (object): The data is added to the Queue.
            When the queue is full, the data is ignored.
        """
        self.put_nowait(data)

    @property
    def data_wait(self):
        """ Returns first item of Queue

        Returns:
            object: The first object of queue.
            Function blocks if necessary until an item is available.
        """
        return self.get(timeout=self._timeout)

    @data_wait.setter
    def data_wait(self, data):
        """ Add an item to the queue with blocking.

        Args:
            data (object): The data is added to the Queue.
            Function blocks if necessary until an space in Queue is available.
        """
        return self.put(data, timeout=self._timeout)
