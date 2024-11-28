import random
import time
import zlib
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
colors = [(207, 23, 23), (6, 47, 196), (8, 161, 54), (201, 114, 26), (163, 148, 34), (38, 153, 171), (181, 27, 117), (92, 11, 191), (120, 120, 120), (94, 55, 16)]
one, two, three = [pygame.transform.scale(pygame.image.load(f'{n}.png'), (200, 200)) for n in ['one', 'two', 'three']]

# Change for player
code = 1
origx = 2000
origy = 2000
color = colors[code-1]
color2 = (0, 0, 0)

speed = 1.5
size = 4000
darts = []
since = 2
tx = origx
ty = origy
rl_ud = [False, False]
run = True
invis = False
power = 'invisibility'
select = 1
powers = {'homing': (800, 550), 'speed': (800, 500), 'invisibility': (900, 450), 'rapid': (650, 350),
          'teleport': (500, 1)}
ptime = 0
name = ''
use_power = [False, 0]
state = 'start'
win = ['Well played, champion! Victory achieved!', 'Incredible! You’re the ultimate winner!',
       'Victory is yours! Enjoy the glory!', 'Amazing! You’ve earned this victory!']
choice = random.choice(win)
end = ''
place = ''
started = 0

gamedata = []

HOST_IP = "192.168.15.167"
HOST_PORT = 1234
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

SELF_IP = socket.gethostbyname(socket.gethostname())
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
    global state, end, place, gamedata, started, darts
    while run:
        info, address = sock.recvfrom(4096)
        info = zlib.decompress(info)
        info = info.decode('utf-8')
        if info[:5] == 'DEATH':
            end, place = info[5:].split('=')
            state = 'end'
        elif info[:3] == 'WIN':
            state = 'win'
            place = 'first'
            time.sleep(1)
        elif info[:4] == 'DATA':
            gamedata = fix(info[4:])
        elif info == 'START' and state == 'wait':
            state = 'game'
            started = 0
            gamedata = []
            darts = []


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


def draw_player(pos, a, c, name):
    cos0 = -math.cos(a)
    sin0 = -math.sin(a)
    pygame.draw.circle(screen, c, (450 - tx + pos[0], 350 - ty + pos[1]), 15)
    draw_rectangle(screen, 450 - tx + pos[0], 350 - ty + pos[1], 20, 10, c, -cos0 * 10, sin0 * 10,
                   -math.asin(sin0) + (2 * math.asin(sin0) + math.pi) * (cos0 > 0))
    text = font.render(name, True, color2)
    textRect = text.get_rect()
    textRect.center = (450 - tx + pos[0], 350 - ty + pos[1]-30)
    screen.blit(text, textRect)


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
                pygame.quit()
        if started >= 150:
            if (pygame.key.get_pressed()[pygame.K_d] or pygame.key.get_pressed()[pygame.K_RIGHT]) and tx < size / 2:
                tx += speed
                rl_ud[0] = True
            elif (pygame.key.get_pressed()[pygame.K_a] or pygame.key.get_pressed()[pygame.K_LEFT]) and tx > -size / 2:
                tx -= speed
                rl_ud[0] = True
            if (pygame.key.get_pressed()[pygame.K_w] or pygame.key.get_pressed()[pygame.K_UP]) and ty > -size / 2:
                ty -= speed
                rl_ud[1] = True
            elif (pygame.key.get_pressed()[pygame.K_s] or pygame.key.get_pressed()[pygame.K_DOWN]) and ty < size / 2:
                ty += speed
                rl_ud[1] = True

            if sum(rl_ud) == 2:
                speed = 1
            else:
                speed = 1.5

            rl_ud = [False, False]
            gap = 2.5
            if use_power[0] and power == 'rapid':
                gap = 1.2
            if pygame.mouse.get_pressed(3)[0] and since > gap:
                darts.append(
                    [[tx - 20 * cos, ty + 20 * sin], (255,),
                     -math.asin(sin) + (2 * math.asin(sin) + math.pi) * (cos > 0),
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
            if darts[d][3] > 80 + 20*(use_power[0] and power == 'homing') and darts[d][1][0] >= 30:
                darts[d][1] = (darts[d][1][0] - 30,)
            if use_power[0] and power == 'homing':
                hp = math.dist(((mx + tx - 450), (my + ty - 350)), (darts[d][0][0], darts[d][0][1]))
                darts[d][0][0] += 3.6 * ((mx + tx - 450) - darts[d][0][0]) / hp
                darts[d][0][1] -= -3.6 * ((my + ty - 350) - darts[d][0][1]) / hp
            else:
                darts[d][0][0] += math.cos(darts[d][2]) * 3.6
                darts[d][0][1] -= math.sin(darts[d][2]) * 3.6
        newdarts = []
        for d in darts:
            if d[1][0] >= 30 and (not (use_power[0] and power == 'homing') or math.dist(((mx + tx - 450), (my + ty - 350)), (d[0][0], d[0][1])) > 3):
                newdarts.append(d)
        darts = newdarts[:]

        if started >= 150:
            if (pygame.key.get_pressed()[pygame.K_f] or pygame.key.get_pressed()[pygame.K_SPACE]) and ptime >= \
                    powers[power][0] and not use_power[0]:
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
                draw_player(p[1], p[2], p[4], p[0])
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
            text = font.render('Press F or Space To Use', True, (0, 0, 0))
            textRect = text.get_rect()
            textRect.center = (450, 635)
            screen.blit(text, textRect)
        surface = pygame.Surface((130, 130), pygame.SRCALPHA)
        surface.fill((0, 0, 0, 180))
        for p in gamedata:
            if not p[3]:
                pygame.draw.circle(surface, p[4], (65 + p[1][0] / size * 130, 65 + p[1][1] / size * 130), 3)
        pygame.draw.circle(surface, color, (65 + tx / size * 130, 65 + ty / size * 130), 3)
        screen.blit(surface, (750, 550))
        if started == 150:
            sock.sendto(bytes('STARTED', 'utf-8'), (HOST_IP, HOST_PORT))
            started += 1
        if started >= 150:
            since += 0.1
            ptime += 1 * (ptime < powers[power][0])
        else:
            if started < 50:
                screen.blit(three, (350, 250))
            elif started < 100:
                screen.blit(two, (350, 250))
            else:
                screen.blit(one, (350, 250))
            started += 1
        game.blit(screen, (0, 0))
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
                pygame.quit()
        screen.fill((188, 204, 198), pygame.Rect(0, 0, w, h))
        for val in range(size // 25 + 1):
            pygame.draw.line(screen, (204, 216, 211), (450 - size / 2, 350 + 25 * val - size / 2),
                             (450 + size / 2, 350 + 25 * val - size / 2), 2)
            pygame.draw.line(screen, (204, 216, 211), (450 + 25 * val - size / 2, 350 - size / 2),
                             (450 + 25 * val - size / 2, 350 + size / 2), 2)
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
            tx = origx
            ty = origy
            speed = 1.5
            since = 2
            rl_ud = [False, False]
            invis = False
            ptime = 0
            use_power = [False, 0]
            name = ''
            time.sleep(0.3)

    elif state == 'start':
        w, h = pygame.display.get_surface().get_size()
        mx, my = pygame.mouse.get_pos()
        screen = pygame.Surface(game.get_size(), pygame.SRCALPHA)
        game.fill((255, 255, 255, 255))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if len(name) < 40:
                    try:
                        if ord(event.unicode) == 32 or 48 <= ord(event.unicode) <= 57 or 65 <= ord(
                                event.unicode) <= 90 or 97 <= ord(event.unicode) <= 122:
                            name += event.unicode
                    except TypeError:
                        pass
        if pygame.key.get_pressed()[pygame.K_BACKSPACE]:
            name = name[:-1]
            time.sleep(0.1)
        screen.fill((188, 204, 198), pygame.Rect(0, 0, w, h))
        for val in range(size // 25 + 1):
            pygame.draw.line(screen, (204, 216, 211), (450 - size / 2, 350 + 25 * val - size / 2),
                             (450 + size / 2, 350 + 25 * val - size / 2), 2)
            pygame.draw.line(screen, (204, 216, 211), (450 + 25 * val - size / 2, 350 - size / 2),
                             (450 + 25 * val - size / 2, 350 + size / 2), 2)
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
        textRect.center = (170, 395)
        screen.blit(text, textRect)
        if select != 1:
            pygame.draw.rect(screen, (171, 171, 171), pygame.Rect(250, 355, 150, 30))
        else:
            pygame.draw.rect(screen, color, pygame.Rect(250, 355, 150, 30))
            power = 'invisibility'
        if select != 2:
            pygame.draw.rect(screen, (171, 171, 171), pygame.Rect(430, 355, 150, 30))
        else:
            pygame.draw.rect(screen, color, pygame.Rect(430, 355, 150, 30))
            power = 'teleport'
        if select != 3:
            pygame.draw.rect(screen, (171, 171, 171), pygame.Rect(610, 355, 150, 30))
        else:
            pygame.draw.rect(screen, color, pygame.Rect(610, 355, 150, 30))
            power = 'speed'
        if select != 4:
            pygame.draw.rect(screen, (171, 171, 171), pygame.Rect(250, 405, 150, 30))
        else:
            pygame.draw.rect(screen, color, pygame.Rect(250, 405, 150, 30))
            power = 'homing'
        if select != 5:
            pygame.draw.rect(screen, (171, 171, 171), pygame.Rect(430, 405, 150, 30))
        else:
            pygame.draw.rect(screen, color, pygame.Rect(430, 405, 150, 30))
            power = 'rapid'
        text = font.render('Invisibility', True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (325, 370)
        screen.blit(text, textRect)
        text = font.render('Teleport', True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (505, 370)
        screen.blit(text, textRect)
        text = font.render('Speed', True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (685, 370)
        screen.blit(text, textRect)
        text = font.render('Homing Shots', True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (325, 420)
        screen.blit(text, textRect)
        text = font.render('Rapid Fire', True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (505, 420)
        screen.blit(text, textRect)
        if pygame.mouse.get_pressed(3)[0]:
            if 320 < mx < 580 and 520 < my < 600:
                state = 'wait'
                time.sleep(0.3)
            if 250 < mx < 400 and 355 < my < 385:
                select = 1
            if 430 < mx < 580 and 355 < my < 385:
                select = 2
            if 610 < mx < 760 and 355 < my < 385:
                select = 3
            if 250 < mx < 400 and 405 < my < 435:
                select = 4
            if 430 < mx < 580 and 405 < my < 435:
                select = 5
        game.blit(screen, (0, 0))
    elif state == 'wait':
        w, h = pygame.display.get_surface().get_size()
        mx, my = pygame.mouse.get_pos()
        screen = pygame.Surface(game.get_size(), pygame.SRCALPHA)
        game.fill((255, 255, 255, 255))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
        screen.fill((188, 204, 198), pygame.Rect(0, 0, w, h))
        for val in range(size // 25 + 1):
            pygame.draw.line(screen, (204, 216, 211), (450 - size / 2, 350 + 25 * val - size / 2),
                             (450 + size / 2, 350 + 25 * val - size / 2), 2)
            pygame.draw.line(screen, (204, 216, 211), (450 + 25 * val - size / 2, 350 - size / 2),
                             (450 + 25 * val - size / 2, 350 + size / 2), 2)
        pygame.draw.polygon(screen, (0, 0, 0), [(50, 50), (50, 650), (850, 650), (850, 50)])
        pygame.draw.polygon(screen, (255, 255, 255), [(52, 52), (52, 648), (848, 648), (848, 52)])
        text = font3.render('Waiting for players...', True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (450, 350)
        screen.blit(text, textRect)
        game.blit(screen, (0, 0))
    pygame.display.flip()
    clock.tick(60)
