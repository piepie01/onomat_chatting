import socket
import json
import select
import sys
def receive(fd):
    s = fd.recv(6000)
    while 1:
        if 10 not in s:
            s = s + fd.recv(6000)
        else:
            break
    return json.loads(s.decode('utf8'))

def receive_from_input():
    if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
        s = sys.stdin.readline()
        d = {'cmd':'text','content':s[:len(s)-1]}
        return d
    else:
        return None

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.connect(('140.112.30.43',44445))
except:
    sock.close()
    print('socket fail.')
    exit()
name_dic = {'cmd':'matching','name':'James','target':'Isabella'}
sock.send((json.dumps(name_dic)+'\n').encode('utf8'))
recv_dict = receive(sock)
sock.settimeout(0.1)
print(recv_dict)
while True:
    s_dict = receive_from_input()
    if s_dict:
        sock.send((json.dumps(s_dict)+'\n').encode('utf8'))
    get = None
    try:
        get = sock.recv(6000)
    except:
        a = 0
    if get:
        get_dict = json.loads(get.decode('utf8'))
        print(get_dict)
        if get_dict['cmd'] == 'error':
            print(get_dict['message'])
            break
        print(json.loads(get.decode('utf8'))['content'])
sock.close()
