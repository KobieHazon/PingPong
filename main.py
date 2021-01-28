"""
    Name: main.py
    Usage: python3 main.py
    Description: This program is responsible for creating a PingPong server as described in the assignment.
    Creation Date: 28/1/21
    Author: Kobie Hazon
"""
import select
import socket
import logging
from typing import List

LOGGING_LEVEL = logging.INFO
SERVER_IP = '0.0.0.0'
SERVER_PORT = 1337
SERVER_LISTEN_SIZE = 5
MAX_MESSAGE_LEN = 1024

CLIENT_TIMEOUT_TIME = 5
PING_MSG = "ping"
PONG_MSG = "pong"


def handle_connections(inputs: List[socket.socket], outputs: List[socket.socket], server_sock: socket.socket):
    """
    Function to handle the connections with clients using the select system call
    :param inputs: Sockets we want to read from
    :param outputs: Sockets we want to write to
    :param server_sock: the socket we are using to listen on the server
    :return: None
    """
    while inputs:
        readable_sockets, writable_sockets, excepted_sockets = \
            select.select(inputs, outputs, inputs, CLIENT_TIMEOUT_TIME)
        for readable_sock in readable_sockets:
            if readable_sock is server_sock:
                client_sock, client_addr = readable_sock.accept()
                logging.info(f"Got connection from client in address {client_addr}.")
                client_sock.setblocking(False)
                inputs.append(client_sock)
            else:
                client_msg = readable_sock.recv(MAX_MESSAGE_LEN).decode()
                logging.info(f"Got \"{client_msg}\" from {readable_sock.getpeername()}")
                inputs.remove(readable_sock)
                if client_msg == PING_MSG and readable_sock not in outputs:
                    outputs.append(readable_sock)
                else:
                    excepted_sockets.append(readable_sock)

        for writable_sock in writable_sockets:
            writable_sock.send(PONG_MSG.encode())
            logging.info(f"Sent \"{PONG_MSG}\" to client in address {writable_sock.getpeername()}.")
            outputs.remove(writable_sock)
            if writable_sock in inputs:
                inputs.remove(writable_sock)
            excepted_sockets.append(writable_sock)

        for excepted_sock in excepted_sockets:
            if excepted_sock is not server_sock:
                logging.info(f"Closing connection with client in address {excepted_sock.getpeername()}.")
                excepted_sock.close()
                if excepted_sock in inputs:
                    inputs.remove(excepted_sock)
                if excepted_sock in outputs:
                    outputs.remove(excepted_sock)


def main():
    """
    Main function for the loggic of the Ping Pong server
    :return: None
    """
    logging.basicConfig(filename='ping_pong_server.log', level=LOGGING_LEVEL,
                        format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    logging.info(f'Started Ping Pong server on port {SERVER_PORT}')
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
            server_sock.setblocking(False)
            server_sock.bind((SERVER_IP, SERVER_PORT))
            logging.debug(f"Ping Pong server bound to ({SERVER_IP}, {SERVER_PORT})")
            server_sock.listen(SERVER_LISTEN_SIZE)
            logging.debug(f"Listening to connection. At most {SERVER_LISTEN_SIZE} clients.")
            inputs = [server_sock]
            outputs = []
            logging.debug(f"Starting to serve clients")
            handle_connections(inputs, outputs, server_sock)
    except KeyboardInterrupt:
        logging.info('Closed Ping Pong server')


if __name__ == "__main__":
    main()
