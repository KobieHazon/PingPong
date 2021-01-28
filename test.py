import socket, time

sockets = [socket.socket() for i in xrange(2000)]
for sock in sockets:
    sock.connect(("localhost", 1340))

time.sleep(5)
