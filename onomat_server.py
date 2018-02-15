#!/usr/bin/env python3
import socket
import json
import select
import sys
import time
import copy
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
def parse_matchlist():
    f = open('match_list','r')
    l = f.read().split('\n')
    d = {}
    for i in l:
        if i == '':
            break
        name = i.split(' ')
        d[name[0]] = name[1]
        d[name[1]] = name[0]
    f.close()
    return d
def receive(fd):
    s = fd.recv(6000)
    if s.decode('utf8') == '':
        return None
    while 1:
        if 10 not in s:
            s = s + fd.recv(6000)
        elif s.decode('utf8') == '':
            return None
        else:
            break
    return json.loads(s.decode('utf8'))

def check_matching(get,match):
    try:
        if match[get['name']] == get['target']:
            return 1
        else:
            return 0
    except:
        return 0

def select_start(sock_fd):
    print('server starts.')
    print('waiting for connecting......')
    match = parse_matchlist()
    user_data = [{'status':0,'name':None,'match_name':None,'match_fd':None} for i in range(200)]
    fd_list = [sock_fd,sys.stdin]
    print(match)
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
                get = receive(fd)
                if get == None:
                    fd_list.remove(fd)
                    print('------close------')
                    print('fd :',fd.fileno())
                    print(user_data[fd.fileno()])
                    print('------')
                    if user_data[fd.fileno()]['status'] == 2:
                        print('send quit')
                        user_data[user_data[fd.fileno()]['match_fd'].fileno()]['status'] = 1
                        err = {'cmd':'error','message':'other side quit'}
                        user_data[fd.fileno()]['match_fd'].send((json.dumps(err)+'\n').encode('utf8'))
                        user_data[user_data[fd.fileno()]['match_fd'].fileno()]['match_fd'] = None
                    user_data[fd.fileno()] = {'status':0,'name':None,'match_name':None,'match_fd':None}
                    fd.close()
                elif get['cmd'] == 'matching':
                    if check_matching(get,match) == 0:
                        continue
                    match_fd = [item for item in range(len(user_data)) if user_data[item]['name'] == get['target']]
                    if len(match_fd) == 0:
                        user_data[fd.fileno()] = {'status':1,'name':copy.copy(get['name']),'match_name':copy.copy(get['target']),'match_fd':0}
                        print(get['name'],'waiting for',get['target'])
                    else:
                        for item in fd_list:
                            if item.fileno() == match_fd[0]:
                                user_data[fd.fileno()] = {'status':2,'name':copy.copy(get['name']),'match_name':copy.copy(get['target']),'match_fd':item}
                                user_data[match_fd[0]]['status'] = 2
                                user_data[match_fd[0]]['match_fd'] = fd
                                print(get['name'],'match',get['target'])
                                message = {'cmd':'matched'}
                                fd.send((json.dumps(message)+'\n').encode('utf8'))
                                item.send((json.dumps(message)+'\n').encode('utf8'))
                                break
                elif get['cmd'] == 'text':
                    if user_data[fd.fileno()]['status'] == 1:
                        err = {'cmd':'error','message':'You have not matched yet.'}
                        fd.send((json.dumps(err)+'\n').encode('utf8'))
                    else:
                        user_data[fd.fileno()]['match_fd'].send((json.dumps(get)+'\n').encode('utf8'))

if __name__ == "__main__":
    check_argument()
    sock_fd = sock_init()
    select_start(sock_fd)
    print('server close.')
    sock_fd.close()
