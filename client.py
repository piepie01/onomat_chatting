import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.connect(('140.112.30.43',44444))
except:
    sock.close()
    print('socket fail.')
    exit()

sock.close()
