import socket
from threading import Thread

HOST_IP = "IP_ADDRESS"
HOST_PORT = 1234
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST_IP, HOST_PORT))

players = {1: ('IP_ADDRESS', 1234)}
left = len(players)
info = []
num = {1: 'first', 2: 'second', 3: 'third', 4: 'fourth', 5:'fifth', 6:'sixth', 7:'seventh', 8:'eighth', 9:'ninth', 10:'tenth'}


def start():
    while True:
        if input('Command: ') == 'START':
            for pl in players:
                sock.sendto(bytes('START', 'utf-8'), players[pl])
            global left
            left = len(players)


s = Thread(target=start)
s.start()

while True:
    data, address = sock.recvfrom(1024)
    data = data.decode('utf-8')
    if len(info) == 1:
        sock.sendto(bytes(f'WIN', 'utf-8'), players[int(info[0][6])])
        info = []
    if data[:5] == 'DEATH':
        stuff = data[5:].split('=')
        p1 = stuff[0].split('+')
        p2 = stuff[1].split('+')
        if stuff[-1] == 'crash':
            left -= 2
            sock.sendto(bytes(f'DEATHYou crashed into {p1[0]}={num[left + 1]}', 'utf-8'), players[int(p1[1])])
            sock.sendto(bytes(f'DEATHYou crashed into {p2[0]}={num[left + 1]}', 'utf-8'), players[int(p2[1])])
            new_info = []
            for i in info:
                if i[6] != int(p1[1]) and i[6] != int(p2[1]):
                    new_info.append(stuff)
            info = new_info[:]
        elif stuff[-1] == 'kill':
            left -= 1
            sock.sendto(bytes(f'DEATHYou were popped by {p1[0]}={num[left + 1]}', 'utf-8'), players[int(p2[1])])
            new_info = []
            for i in info:
                if i[6] != int(p2[1]):
                    new_info.append(stuff)
            info = new_info[:]
    else:
        stuff = eval(data)
        new_info = [stuff]
        for i in info:
            if i[6] != stuff[6]:
                new_info.append(stuff)
        info = new_info[:]
        for p in players:
            sock.sendto(bytes(str(info), 'utf-8'), players[p])
