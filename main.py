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
SERVER_PORT = 1340
SERVER_LISTEN_SIZE = 5
MAX_MESSAGE_LEN = 1024

CLIENT_TIMEOUT_TIME = 5
PING_MSG = "ping"
PONG_MSG = "pong"


def close_connection(polling_object: select.poll, socket_to_close: socket.socket):
    """
    Closes a connection and cleans up the polling objects
    :param polling_object: The object that uses the poll system call
    :param socket_to_close: The socket we need to close
    :return: None
    """
    logging.info(f"Closing connection with client in address {socket_to_close.getpeername()}.")
    polling_object.unregister(socket_to_close)
    socket_to_close.close()


def handle_connections(server_sock: socket.socket):
    """
    Function to handle the connections with clients using the select system call
    :param inputs: Sockets we want to read from
    :param outputs: Sockets we want to write to
    :param server_sock: the socket we are using to listen on the server
    :return: None
    """
    sockets = {server_sock.fileno(): server_sock}
    polling_object = select.poll()
    polling_object.register(server_sock, select.POLLIN | select.POLLHUP | select.POLLERR)
    while True:
        event_list = polling_object.poll()
        for event_socket_fd, event_type in event_list:
            if sockets[event_socket_fd] is server_sock:
                client_sock, client_addr = server_sock.accept()
                logging.info(f"Got connection from client in address {client_addr}.")
                client_sock.setblocking(False)
                polling_object.register(client_sock, select.POLLIN | select.POLLHUP | select.POLLERR)
                sockets[client_sock.fileno()] = client_sock
            else:
                if event_type is select.POLLERR or event_type is select.POLLHUP:
                    close_connection(polling_object, sockets[event_socket_fd])
                    sockets.pop(event_socket_fd, None)
                elif event_type is select.POLLIN:
                    event_socket = sockets[event_socket_fd]
                    client_msg = event_socket.recv(MAX_MESSAGE_LEN).decode()
                    logging.info(f"Got \"{client_msg}\" from {event_socket.getpeername()}")
                    if client_msg != PING_MSG:
                        close_connection(polling_object, event_socket)
                        sockets.pop(event_socket_fd, None)
                    else:
                        polling_object.modify(event_socket,
                                              select.POLLIN | select.POLLHUP | select.POLLERR | select.POLLOUT)
                elif event_type is select.POLLOUT:
                    event_socket = sockets[event_socket_fd]
                    event_socket.send(PONG_MSG.encode())
                    logging.info(f"Sent \"{PONG_MSG}\" to client in address {event_socket.getpeername()}.")
                    polling_object.modify(event_socket, select.POLLIN | select.POLLHUP | select.POLLERR)


def main():
    """
    Main function for the logic of the Ping Pong server
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
            handle_connections(server_sock)
    except KeyboardInterrupt:
        logging.info('Closed Ping Pong server')


if __name__ == "__main__":
    main()
