import zmq

class IPC:
    def __init__(self):
        self.context = zmq.Context()
        self.sockets = {}

    def init_publisher(self, address):
        """
        Initialize the publisher.
        :param address: The address to bind to.
        """
        pub_socket = self.context.socket(zmq.PUB)
        pub_socket.bind(address)
        self.sockets['pub'] = pub_socket

    def init_subscriber(self, name, address, topic=''):
        """
        Initialize the subscriber.
        :param name: The name/ID of the subscriber.
        :param address: The address to connect to.
        :param topic: The topic to subscribe to (default is all topics).
        """
        sub_socket = self.context.socket(zmq.SUB)
        sub_socket.connect(address)
        sub_socket.setsockopt_string(zmq.SUBSCRIBE, topic)
        self.sockets[name] = sub_socket

    def init_requester(self, address):
        """
        Initialize the requester.
        :param name: The name/ID of the requester.
        :param address: The address to connect to.
        """
        req_socket = self.context.socket(zmq.REQ)
        req_socket.connect(address)
        self.sockets['req'] = req_socket

    def init_replier(self, address):
        """
        Initialize the replier.
        :param address: The address to bind to.
        """
        rep_socket = self.context.socket(zmq.REP)
        rep_socket.bind(address)
        self.sockets['rep'] = rep_socket

    def publish(self, message, topic=None):
        """
        Send a message.
        :param message: The message to send.
        :param topic: The topic for PUB mode (optional).
        """
        pub_socket = self.sockets.get('pub')
        if not pub_socket:
            raise ValueError("Publisher socket is not initialized.")
        
        if topic:
            pub_socket.send_string(f"{topic} {message}")
        else:
            pub_socket.send_string(message)

    def receive_published(self, name, timeout=500):
        """
        Receive a message with a timeout.
        :param name: The name/ID of the subscriber.
        :param timeout: Timeout in milliseconds to wait for a message.
        :return: The received message or None if no message is received within the timeout.
        """
        sub_socket = self.sockets.get(name)
        if not sub_socket:
            raise ValueError("Subscriber socket is not initialized.")

        poller = zmq.Poller()
        poller.register(sub_socket, zmq.POLLIN)
        socks = dict(poller.poll(timeout))

        if socks.get(sub_socket) == zmq.POLLIN:
            return sub_socket.recv_string()
        return None

    def send_request(self, name, message, timeout=5000):
        """
        Send a request and wait for a response.
        :param name: The name/ID of the requester.
        :param message: The request message to send.
        :param timeout: Timeout in milliseconds to wait for a response.
        :return: The response message or None if no response is received within the timeout.
        """
        req_socket = self.sockets.get(name)
        if not req_socket:
            raise ValueError("Requester socket is not initialized.")
        
        req_socket.send_string(message)
        
        poller = zmq.Poller()
        poller.register(req_socket, zmq.POLLIN)
        socks = dict(poller.poll(timeout))

        if socks.get(req_socket) == zmq.POLLIN:
            return req_socket.recv_string()
        return None

    def receive_request(self, timeout=5000):
        """
        Receive a request and return it.
        :param timeout: Timeout in milliseconds to wait for a request.
        :return: The request message or None if no request is received within the timeout.
        """
        rep_socket = self.sockets.get('rep')
        if not rep_socket:
            raise ValueError("Replier socket is not initialized.")
        
        poller = zmq.Poller()
        poller.register(rep_socket, zmq.POLLIN)
        socks = dict(poller.poll(timeout))

        if socks.get(rep_socket) == zmq.POLLIN:
            return rep_socket.recv_string()
        return None

    def send_response(self, message):
        """
        Send a response.
        :param message: The response message to send.
        """
        rep_socket = self.sockets.get('rep')
        if not rep_socket:
            raise ValueError("Replier socket is not initialized.")
        
        rep_socket.send_string(message)

    def close(self):
        """
        Close all sockets and terminate the context.
        """
        for socket in self.sockets.values():
            socket.close()
        self.context.term()
        
    def get_free_port(self):
        """
        Get a free port.
        :return: A free port number.
        """
        temp_socket = self.context.socket(zmq.REQ)
        port = temp_socket.bind_to_random_port('tcp://127.0.0.1')
        temp_socket.close()
        return port
