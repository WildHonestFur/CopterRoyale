import socket
import zlib
from threading import Thread

HOST_IP = "192.168.15.167"
HOST_PORT = 1234
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock2.bind((HOST_IP, HOST_PORT))

players = {1: ('192.168.15.168', 1234), 2: ('192.168.15.169', 1234), 3: ('192.168.15.171', 1234)}
left = len(players)
info = []
dead = []
num = {1: 'first', 2: 'second', 3: 'third', 4: 'fourth', 5: 'fifth', 6: 'sixth', 7: 'seventh', 8: 'eighth', 9: 'ninth',
       10: 'tenth'}
started = False


def start():
    while True:
        if input('Command: ') == 'START':
            for pl in players:
                ts = 'START'.encode('utf-8')
                ts = zlib.compress(ts)
                sock.sendto(ts, players[pl])


s = Thread(target=start)
s.start()

while True:
    data, address = sock2.recvfrom(1024)
    data = data.decode('utf-8')
    if len(info) <= 1 and started:
        try:
            if int(info[0][6]) not in dead:
                 to_send = 'WIN'.encode('utf-8')
                 to_send = zlib.compress(to_send)
                 sock.sendto(to_send, players[int(info[0][6])])
        except IndexError:
            pass
        started = False
    if data[:5] == 'DEATH':
        stuff = data[5:].split('=')
        p1 = stuff[0].split('+')
        p2 = stuff[1].split('+')
        if stuff[-1] == 'crash':
            left -= 2
            to_send = f'DEATHYou crashed into {p1[0]}={num[left + 1]}'.encode('utf-8')
            to_send = zlib.compress(to_send)
            sock.sendto(to_send, players[int(p2[1])])
            to_send = f'DEATHYou crashed into {p2[0]}={num[left + 1]}'.encode('utf-8')
            to_send = zlib.compress(to_send)
            sock.sendto(to_send, players[int(p1[1])])
            new_info = []
            for i in info:
                if i[6] != int(p1[1]) and i[6] != int(p2[1]):
                    new_info.append(i)
            info = new_info[:]
            dead.append(int(p2[1]))
            dead.append(int(p1[1]))

        elif stuff[-1] == 'kill':
            left -= 1
            to_send = f'DEATHYou were popped by {p1[0]}={num[left + 1]}'.encode('utf-8')
            to_send = zlib.compress(to_send)
            sock.sendto(to_send, players[int(p2[1])])
            new_info = []
            for i in info:
                if i[6] != int(p2[1]):
                    new_info.append(i)
            info = new_info[:]
            dead.append(int(p2[1]))
    elif data == 'STARTED':
        started = True
        dead = []
        info = []
        left = len(info)
    else:
        stuff = eval(data)
        new_info = [stuff]
        if stuff[6] not in dead:
            for i in info:
                if i[6] != stuff[6]:
                    new_info.append(i)
            info = new_info[:]
        for p in players:
            to_send = ('DATA' + str(info)).encode('utf-8')
            to_send = zlib.compress(to_send)
            sock.sendto(to_send, players[p])
