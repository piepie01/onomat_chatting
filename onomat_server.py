#!/usr/bin/env python3
import socket
import json
import select
import sys
import time
def check_argument():
    if len(sys.argv) != 2:
        print('You need to assign port.')
        print('Usage: ./onomat_server.py [port]')
        sys.exit(0)

def sock_init():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((socket.gethostname(),int(sys.argv[1])))
        sock.listen(100)
        return sock
    except:
        print('The port you assigned has already be used.')
        sys.exit(0)

def new_client(sock_fd):
    client_socket, address = sock_fd.accept()
    print('new connection from',address)
    #print(client_socket.fileno())
    return client_socket

def select_start(sock_fd):
    print('server starts.')
    print('waiting for connecting......')
    user_data = [{'status':0,'name':None,'match_name':None} for i in range(200)]
    fd_list = [sock_fd,sys.stdin]
    while True:
        readable, writable, errored = select.select(fd_list, [], [])
        for fd in readable:
            if fd is sock_fd:
                client_fd = new_client(sock_fd)
                fd_list.append(client_fd)
                user_data[client_fd.fileno()]['status'] = 1
            elif fd is sys.stdin:
                s = sys.stdin.readline()
                if s == "quit\n":
                    return 0
            else:
                s = fd.recv(4096).decode('utf8')
                if s == '':
                    fd_list.remove(fd)
                    print('------close------')
                    print('fd :',fd.fileno())
                    print(user_data[fd.fileno()])
                    print('------')
                    user_data[fd.fileno()] = {'status':0,'name':None,'match_name':None}
                    fd.close()


if __name__ == "__main__":
    check_argument()
    sock_fd = sock_init()
    select_start(sock_fd)
    print('server close.')
    sock_fd.close()
