import socket
import threading

PORT = 12345
SUCCESS = "SUCCESS"
EMPTY = "EMPTY"


class ServerException(Exception):
    pass


class Server(object):
    def __init__(self):
        self.clients = {}
        self.messages = {}
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def get_clients(self):
        """
        :return: list of clients names
        """
        return self.clients.keys()

    def add_client(self, name, sock):
        # Warning: not thread safe
        if len(name) == 0:
            raise ServerException("Name is empty")
        if '|' in name or ' ' in name:
            raise ServerException("Name cannot contains '|' or spaces")
        if name in self.clients:
            raise ServerException("This name is taken")
        self.clients[name] = sock

    def remove_client(self, name):
        # Warning: not thread safe
        self.clients.pop(name)

    def get_messages(self, name):
        return self.messages.get(name)

    def clear_messages(self, name):
        self.messages[name] = {}

    def add_message(self, source, dest, msg):
        if dest not in self.messages:
            self.messages[dest] = {}
        if source not in self.messages[dest]:
            self.messages[dest][source] = []
        self.messages[dest][source].append(msg)

    def start(self, port):
        self.sock.bind(('0.0.0.0', port))
        self.sock.listen(5)  # Max connections
        print "Server is up and listening on port {port}".format(port=port)

        try:
            print "Press Ctrl+C to stop listening for new connections"
            # listen for new connection loop
            while True:
                client_sock, client_address = self.sock.accept()
                print 'New connection from {ip}:{port}'.format(ip=client_address[0], port=client_address[1])
                ClientHandler(client_sock, client_address[0], client_address[1], self).start()
        except KeyboardInterrupt:
            print "Server Stopped listening for new connections"
            print "There is still {} existing connections".format(len(self.clients))


class ClientHandler(threading.Thread):
    def __init__(self, sock, ip, port, server):
        """
        A thread to handle 1 client
        :param sock: socket
        :param ip: string
        :param port: int
        :param server: Server
        """
        threading.Thread.__init__(self)
        self.sock = sock
        self.ip = ip
        self.port = port
        self.server = server
        self.client_name = None

    def run(self):
        try:
            self.client_name = self.pick_name()
            self.main_loop()
        except socket.error as e:
            print "Socket Error: {error}".format(error=e)
        self.cleanup()

    def main_loop(self):
        cmd = self.recv_cmd()
        while cmd and cmd != 'bye':  # make sure cmd isn't empty
            if cmd.startswith("get"):
                if cmd == "get clients":
                    res = self.get_clients()
                elif cmd == "get messages":
                    res = self.get_messages()
                print "{name} request {what}".format(name=self.client_name, what=cmd[4:])
                self.sock.send(res)
            elif cmd.startswith("send to "):
                self.send_pm(cmd)
            cmd = self.recv_cmd()

    def recv_cmd(self):
        cmd = self.sock.recv(4096)
        print '{name} ask: "{cmd}"'.format(name=self.client_name, cmd=cmd)
        return cmd

    def pick_name(self):
        """
        Try get a valid name
        :return: name
        """
        while True:
            name = self.sock.recv(4096)
            print "{ip}:{port} trying using name: {name}".format(ip=self.ip, port=self.port, name=name)
            try:
                self.server.add_client(name, self.sock)
                self.sock.send(SUCCESS)
                print "{ip}:{port} got name: {name}".format(ip=self.ip, port=self.port, name=name)
                return name
            except ServerException as e:
                self.sock.send(e.message)

    def get_clients(self):
        return '|'.join(self.server.get_clients())

    def get_messages(self):
        messages = self.server.get_messages(self.client_name)
        self.server.clear_messages(self.client_name)
        if not messages:  # None or with length 0
            return EMPTY
        messages = ["{sender} {msg}".format(sender=sender, msg=msg) for sender, msgs in messages.items() for msg in msgs]
        return '|'.join(messages)

    def send_pm(self, request):
        name_start = len("send to ")
        name_end = request.find(" ", name_start+1)

        to = request[name_start:name_end]
        msg = request[name_end+1:]

        print "{} -> {}: {}".format(self.client_name, to, msg)
        self.server.add_message(self.client_name, to, msg)

    def cleanup(self):
        if self.client_name:
            self.server.remove_client(self.client_name)
            print "{name} has left".format(name=self.client_name)
        else:
            print "{ip}:{port} has left".format(ip=self.ip, port=self.port)
        self.sock.close()


def main():
    server = Server()
    server.start(PORT)

if __name__ == '__main__':
    main()
