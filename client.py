import socket

SERVER_IP = '127.0.0.1'
SERVER_PORT = 12345
SUCCESS = "SUCCESS"
EMPTY = "EMPTY"


class Client(object):
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def sendrecv(self, msg):
        self.sock.send(msg)
        return self.sock.recv(4096)

    def connect(self, ip, port):
        self.sock.connect((ip, port))

    def try_name(self, name):
        return self.sendrecv(name)

    def get_clients(self):
        return self.sendrecv("get clients").split('|')

    def send_pm(self, client_name, msg):
        self.sock.send("send to {name} {msg}".format(name=client_name, msg=msg))

    def get_messages(self):
        """
        :return: dict of list of messages from each client
        """
        messages = {}
        response = self.sendrecv("get messages")
        if response == EMPTY:
            return messages
        for msg in response.split('|'):
            sender = msg[:msg.find(" ")]
            content = msg[len(sender) + 1:]
            messages.setdefault(sender, []).append(content)  # this line create list of messages from each client
        return messages

    def disconnect(self):
        if self.sock:
            self.sock.send("bye")
            self.sock.shutdown(socket.SHUT_RDWR)  # releases resources
            self.sock.close()


class ClientUI(object):
    """
    Handle the use of Client
    """
    def __init__(self, client):
        """
        :param client: Client
        """
        self.client = client

    def connect_to_server(self):
        """
        trying to connect to the server
        :return: bool is connected successfully
        """
        try:
            self.client.connect(SERVER_IP, SERVER_PORT)
            print "Welcome to Axon Chat Room!"
            name = raw_input("Please Enter your name: ")
            server_response = self.client.try_name(name)
            while server_response != SUCCESS:
                print "Error:", server_response
                name = raw_input("Please Enter another name: ")
                server_response = self.client.try_name(name)
            print "Hello", name
            return True
        except socket.error as e:
            print "Error:", e
            return False

    @staticmethod
    def print_menu():
        print "[S]end private message"
        print "[R]ead messages"
        print "E[x]it"

    def send_pm(self):
        # Print available clients
        clients = self.client.get_clients()
        for index, client_name in enumerate(clients):
            print "[{i}] {name}".format(i=index, name=client_name)
        index = raw_input("Choose client number: ")

        # Check client index is valid
        if not index.isdigit() or int(index) >= len(clients):
            return

        # Read and send the message
        msg = raw_input("Enter message: ")
        self.client.send_pm(clients[int(index)], msg)

    def print_messages(self):
        """
        Get all messages sent to this client from server and print them
        """
        messages = self.client.get_messages()
        print "You have {} messages".format(len(messages))
        for sender, msgs in messages.items():
            for msg in msgs:
                print "{sender}: {msg}".format(sender=sender, msg=msg.replace("\n", "\n    "))

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Disconnect gracefully
        """
        self.client.disconnect()

    def main_loop(self):
        try:
            self.print_menu()
            cmd = raw_input("Enter your command: ")
            while cmd.lower() != 'x':
                if cmd.lower() == 's':
                    self.send_pm()
                elif cmd.lower() == 'r':
                    self.print_messages()
                self.print_menu()
                cmd = raw_input("Enter your command: ")
        except socket.error as e:
            print "Error:", e


def main():
    client = Client()
    handler = ClientUI(client)
    if handler.connect_to_server():
        handler.main_loop()

if __name__ == '__main__':
    main()
