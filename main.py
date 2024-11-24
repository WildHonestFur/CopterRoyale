import random
import time
import pygame
import math
import socket
from threading import Thread

pygame.init()
clock = pygame.time.Clock()
game = pygame.display.set_mode((900, 700))
font = pygame.font.Font('freesansbold.ttf', 15)
font2 = pygame.font.Font('freesansbold.ttf', 30)
font3 = pygame.font.Font('freesansbold.ttf', 45)
img = pygame.image.load('trophy.png')
img = pygame.transform.scale(img, (200, 200))


# To change
code = 1
tx = 0
ty = 0
color = (250, 0, 0)
color2 = (200, 50, 50)

speed = 1.5
size = 1225
darts = []
since = 1.2
rl_ud = [False, False]
run = True
invis = False
power = 'invisibility'
select = 1
powers = {'speed': (800, 500), 'invisibility': (900, 400), 'turret': (800, 500), 'teleport': (500, 1)}
ptime = 0
name = 'TEST'
use_power = [False, 0]
state = 'game'
win = ['Well played, champion! Victory achieved!', 'Incredible! You’re the ultimate winner!',
       'Victory is yours! Enjoy the glory!', 'Amazing! You’ve earned this victory!']
choice = random.choice(win)
end = 'You were popped by player 3'
place = 'first'

gamedata = []

HOST_IP = "192.168.109.1"
HOST_PORT = 1234
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

SELF_IP = '192.168.109.1'
SELF_PORT = 1234
sock.bind((SELF_IP, SELF_PORT))


def fix(s):
    receive = eval(s)
    new = []
    for i in receive:
        if i[6] != code:
            new.append(i)
    return new[:]


def listen():
    global state, end, place, gamedata
    while run:
        info, address = sock.recvfrom(1024)
        info = info.decode('utf-8')
        if info[:5] == 'DEATH':
            end, place = info[5:].split('=')
            state = 'end'
        elif info[:3] == 'WIN':
            state = 'win'
            place = 'first'
        elif info[:4] == 'DATA':
            gamedata = fix(info[4:])
        elif info == 'START' and state == 'wait':
            state = 'game'


def draw_rectangle(s, x, y, width, height, c, t_x, t_y, rotation):
    points = []
    radius = math.sqrt((height / 2) ** 2 + (width / 2) ** 2)
    angle = math.atan2(height / 2, width / 2)
    angles = [angle, -angle + math.pi, angle + math.pi, -angle]
    rot_radians = rotation
    for angle in angles:
        y_offset = -1 * radius * math.sin(angle + rot_radians)
        x_offset = radius * math.cos(angle + rot_radians)
        points.append((x + x_offset + t_x, y + y_offset + t_y))
    pygame.draw.polygon(s, c, points)


def draw_player(pos, a, c):
    cos0 = -math.cos(a)
    sin0 = -math.sin(a)
    pygame.draw.circle(screen, c, (450 - tx + pos[0], 350 - ty + pos[1]), 15)
    draw_rectangle(screen, 450 - tx + pos[0], 350 - ty + pos[1], 20, 10, c, -cos0 * 10, sin0 * 10,
                   -math.asin(sin0) + (2 * math.asin(sin0) + math.pi) * (cos0 > 0))


listening = Thread(target=listen)
listening.start()

while run:
    if state == 'game':
        w, h = pygame.display.get_surface().get_size()
        mx, my = pygame.mouse.get_pos()
        hyp = math.dist((mx, my), (450, 350))
        cos = round((450 - mx) / hyp, 2)
        sin = round((my - 350) / hyp, 2)
        screen = pygame.Surface(game.get_size(), pygame.SRCALPHA)
        game.fill((255, 255, 255))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        if pygame.key.get_pressed()[pygame.K_d] and tx < size / 2:
            tx += speed
            rl_ud[0] = True
        elif pygame.key.get_pressed()[pygame.K_a] and tx > -size / 2:
            tx -= speed
            rl_ud[0] = True
        if pygame.key.get_pressed()[pygame.K_w] and ty > -size / 2:
            ty -= speed
            rl_ud[1] = True
        elif pygame.key.get_pressed()[pygame.K_s] and ty < size / 2:
            ty += speed
            rl_ud[1] = True

        if sum(rl_ud) == 2:
            speed = 1
        else:
            speed = 1.5

        rl_ud = [False, False]

        if pygame.mouse.get_pressed(3)[0] and since > 1.2:
            darts.append(
                [[tx - 20 * cos, ty + 20 * sin], (255,), -math.asin(sin) + (2 * math.asin(sin) + math.pi) * (cos > 0),
                 0])
            since = 0

        screen.fill((121, 135, 130), pygame.Rect(0, 0, w, h))
        pygame.draw.polygon(screen, (188, 204, 198),
                            [(450 - tx - size / 2, 350 - ty - size / 2), (450 - tx - size / 2, 350 - ty + size / 2),
                             (450 - tx + size / 2, 350 - ty + size / 2), (450 - tx + size / 2, 350 - ty - size / 2)])
        for val in range(size // 25 + 1):
            pygame.draw.line(screen, (204, 216, 211), (450 - tx - size / 2, 350 - ty + 25 * val - size / 2),
                             (450 - tx + size / 2, 350 - ty + 25 * val - size / 2), 2)
            pygame.draw.line(screen, (204, 216, 211), (450 - tx + 25 * val - size / 2, 350 - ty - size / 2),
                             (450 - tx + 25 * val - size / 2, 350 - ty + size / 2), 2)

        for d in darts:
            pygame.draw.circle(screen, color + d[1], (450 - tx + d[0][0], 350 - ty + d[0][1]), 5)
        for d in range(len(darts)):
            darts[d][3] += 1
            if darts[d][3] > 90 and darts[d][1][0] >= 20:
                darts[d][1] = (darts[d][1][0] - 20,)
            darts[d][0][0] += math.cos(darts[d][2]) * 3.6
            darts[d][0][1] -= math.sin(darts[d][2]) * 3.6
        newdarts = []
        for d in darts:
            if d[1][0] >= 20:
                newdarts.append(d)
        darts = newdarts[:]

        if pygame.key.get_pressed()[pygame.K_f] and ptime >= powers[power][0] and not use_power[0]:
            use_power[0] = True

        if use_power[0]:
            if power == 'speed':
                if sum(rl_ud) == 2:
                    speed = 1.6
                else:
                    speed = 2.3
            elif power == 'teleport':
                if 450 - tx - size / 2 < mx < 450 - tx + size / 2 and 350 - ty - size / 2 < my < 350 - ty + size / 2:
                    tx += mx - 450
                    ty += my - 350
                    use_power = [False, 0]
                    ptime = 0
                else:
                    use_power = [False, 0]
            elif power == 'invisibility':
                invis = True

        if use_power[0] and use_power[1] > powers[power][1]:
            use_power = [False, 0]
            invis = False
            ptime = 0
        for p in gamedata:
            if not p[3]:
                draw_player(p[1], p[2], p[4])
            for d in p[5]:
                pygame.draw.circle(screen, p[4] + d[1], (450 - tx + d[0][0], 350 - ty + d[0][1]), 5)

        for p in gamedata:
            if math.dist((tx, ty), p[1]) < 30:
                sock.sendto(bytes(f'DEATH{p[0]}+{p[6]}={name}+{code}=crash', 'utf-8'), (HOST_IP, HOST_PORT))
            for d in p[5]:
                if math.dist(d[0], (tx, ty)) < 20:
                    sock.sendto(bytes(f'DEATH{p[0]}+{p[6]}={name}+{code}=kill', 'utf-8'), (HOST_IP, HOST_PORT))

        pygame.draw.circle(screen, color * (not invis) + color2 * invis, (450, 350), 15)
        draw_rectangle(screen, 450, 350, 20, 10, color * (not invis) + color2 * invis, -cos * 10, sin * 10,
                       -math.asin(sin) + (2 * math.asin(sin) + math.pi) * (cos > 0))
        screen.fill((0, 0, 0), pygame.Rect(350, 650, 200, 15))
        if not use_power[0]:
            screen.fill((247, 120, 22), pygame.Rect(350, 650, 200 * (ptime / powers[power][0]), 15))
        else:
            screen.fill((247, 120, 22), pygame.Rect(350, 650, 200 * (1 - use_power[1] / powers[power][1]), 15))
        if not use_power[0] and ptime < powers[power][0]:
            text = font.render('Superpower Recharging...', True, (0, 0, 0))
            textRect = text.get_rect()
            textRect.center = (450, 635)
            screen.blit(text, textRect)
        else:
            text = font.render('Press F To Use', True, (0, 0, 0))
            textRect = text.get_rect()
            textRect.center = (450, 635)
            screen.blit(text, textRect)
        surface = pygame.Surface((130, 130), pygame.SRCALPHA)
        surface.fill((0, 0, 0, 180))
        for p in gamedata:
            pygame.draw.circle(surface, p[4], (65+p[1][0]/size*130, 65+p[1][0]/size*130), 3)
        pygame.draw.circle(surface, color, (65 + tx / size * 130, 65 + ty / size * 130), 3)
        screen.blit(surface, (750, 550))
        game.blit(screen, (0, 0))
        since += 0.1
        ptime += 1 * (ptime < powers[power][0])
        if use_power[0]:
            use_power[1] += 1
        data = ['\'' + name + '\'', str((tx, ty)), str(-math.asin(sin) + (2 * math.asin(sin) + math.pi) * (cos > 0)),
                str(invis),
                str(color), str(darts), str(code)]
        sock.sendto(bytes('[' + ', '.join(data) + ']', 'utf-8'), (HOST_IP, HOST_PORT))

    elif state == 'end' or state == 'win':
        w, h = pygame.display.get_surface().get_size()
        mx, my = pygame.mouse.get_pos()
        screen = pygame.Surface(game.get_size(), pygame.SRCALPHA)
        game.fill((255, 255, 255, 255))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        screen.fill((188, 204, 198), pygame.Rect(0, 0, w, h))
        for val in range(size // 25 + 1):
            pygame.draw.line(screen, (204, 216, 211), (450 - tx - size / 2, 350 - ty + 25 * val - size / 2),
                             (450 - tx + size / 2, 350 - ty + 25 * val - size / 2), 2)
            pygame.draw.line(screen, (204, 216, 211), (450 - tx + 25 * val - size / 2, 350 - ty - size / 2),
                             (450 - tx + 25 * val - size / 2, 350 - ty + size / 2), 2)
        pygame.draw.polygon(screen, (0, 0, 0), [(50, 50), (50, 650), (850, 650), (850, 50)])
        pygame.draw.polygon(screen, (255, 255, 255), [(52, 52), (52, 648), (848, 648), (848, 52)])
        if state == 'end':
            text = font2.render(end, True, (0, 0, 0))
        else:
            text = font2.render(choice, True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (450, 120)
        screen.blit(text, textRect)
        text = font2.render(f'You got {place} place', True, color)
        textRect = text.get_rect()
        textRect.center = (450, 200)
        screen.blit(text, textRect)
        if 320 < mx < 580 and 520 < my < 600:
            pygame.draw.rect(screen, (171, 171, 171), pygame.Rect(320, 520, 260, 80))
        else:
            pygame.draw.rect(screen, color, pygame.Rect(320, 520, 260, 80))
        screen.blit(img, (350, 270))
        text = font2.render('New Game', True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (450, 560)
        screen.blit(text, textRect)
        game.blit(screen, (0, 0))
        if pygame.mouse.get_pressed(3)[0] and 320 < mx < 580 and 520 < my < 600:
            state = 'start'
            choice = random.choice(win)
            tx = 0
            ty = 0
            speed = 1.5
            since = 1.2
            rl_ud = [False, False]
            invis = False
            ptime = 0
            use_power = [False, 0]
            name = ''
            time.sleep(0.2)

    elif state == 'start':
        w, h = pygame.display.get_surface().get_size()
        mx, my = pygame.mouse.get_pos()
        screen = pygame.Surface(game.get_size(), pygame.SRCALPHA)
        game.fill((255, 255, 255, 255))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 40:
                    name += event.unicode
        screen.fill((188, 204, 198), pygame.Rect(0, 0, w, h))
        for val in range(size // 25 + 1):
            pygame.draw.line(screen, (204, 216, 211), (450 - tx - size / 2, 350 - ty + 25 * val - size / 2),
                             (450 - tx + size / 2, 350 - ty + 25 * val - size / 2), 2)
            pygame.draw.line(screen, (204, 216, 211), (450 - tx + 25 * val - size / 2, 350 - ty - size / 2),
                             (450 - tx + 25 * val - size / 2, 350 - ty + size / 2), 2)
        pygame.draw.polygon(screen, (0, 0, 0), [(50, 50), (50, 650), (850, 650), (850, 50)])
        pygame.draw.polygon(screen, (255, 255, 255), [(52, 52), (52, 648), (848, 648), (848, 52)])
        text = font3.render('Battle Royale', True, color)
        textRect = text.get_rect()
        textRect.center = (450, 120)
        screen.blit(text, textRect)
        if 320 < mx < 580 and 520 < my < 600:
            pygame.draw.rect(screen, (171, 171, 171), pygame.Rect(320, 520, 260, 80))
        else:
            pygame.draw.rect(screen, color, pygame.Rect(320, 520, 260, 80))
        text = font2.render('Start', True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (450, 560)
        screen.blit(text, textRect)
        if time.time() // 0.3 % 2 == 0:
            text = font2.render('Name: ' + name, True, (0, 0, 0))
        else:
            text = font2.render('Name: ' + name + '_', True, (0, 0, 0))
        textRect = text.get_rect()
        if time.time() // 0.3 % 2 == 0:
            textRect.center = (450, 250)
        else:
            textRect.center = (459, 250)
        screen.blit(text, textRect)
        text = font2.render('Power:', True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (180, 400)
        screen.blit(text, textRect)
        if select != 1:
            pygame.draw.rect(screen, (171, 171, 171), pygame.Rect(250, 385, 150, 30))
        else:
            pygame.draw.rect(screen, color, pygame.Rect(250, 385, 150, 30))
            power = 'invisibility'
        if select != 2:
            pygame.draw.rect(screen, (171, 171, 171), pygame.Rect(430, 385, 150, 30))
        else:
            pygame.draw.rect(screen, color, pygame.Rect(430, 385, 150, 30))
            power = 'teleport'
        if select != 3:
            pygame.draw.rect(screen, (171, 171, 171), pygame.Rect(610, 385, 150, 30))
        else:
            pygame.draw.rect(screen, color, pygame.Rect(610, 385, 150, 30))
            power = 'speed'
        text = font.render('Invisibility', True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (325, 400)
        screen.blit(text, textRect)
        text = font.render('Teleport', True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (505, 400)
        screen.blit(text, textRect)
        text = font.render('Speed', True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (685, 400)
        screen.blit(text, textRect)
        if pygame.mouse.get_pressed(3)[0]:
            if 320 < mx < 580 and 520 < my < 600:
                state = 'wait'
                time.sleep(0.2)
            if 250 < mx < 400 and 385 < my < 415:
                select = 1
            if 430 < mx < 580 and 385 < my < 415:
                select = 2
            if 610 < mx < 760 and 385 < my < 415:
                select = 3
        game.blit(screen, (0, 0))
    elif state == 'wait':
        w, h = pygame.display.get_surface().get_size()
        mx, my = pygame.mouse.get_pos()
        screen = pygame.Surface(game.get_size(), pygame.SRCALPHA)
        game.fill((255, 255, 255, 255))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        screen.fill((188, 204, 198), pygame.Rect(0, 0, w, h))
        for val in range(size // 25 + 1):
            pygame.draw.line(screen, (204, 216, 211), (450 - tx - size / 2, 350 - ty + 25 * val - size / 2),
                             (450 - tx + size / 2, 350 - ty + 25 * val - size / 2), 2)
            pygame.draw.line(screen, (204, 216, 211), (450 - tx + 25 * val - size / 2, 350 - ty - size / 2),
                             (450 - tx + 25 * val - size / 2, 350 - ty + size / 2), 2)
        pygame.draw.polygon(screen, (0, 0, 0), [(50, 50), (50, 650), (850, 650), (850, 50)])
        pygame.draw.polygon(screen, (255, 255, 255), [(52, 52), (52, 648), (848, 648), (848, 52)])
        text = font3.render('Waiting for players...', True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (450, 350)
        screen.blit(text, textRect)
        game.blit(screen, (0, 0))

    pygame.display.flip()
    clock.tick(60)
