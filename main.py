import random
import time
import zlib
import pygame
import math
import socket
from threading import Thread

pygame.init()
clock = pygame.time.Clock()
infoObject = pygame.display.Info()
game = pygame.display.set_mode((infoObject.current_w, infoObject.current_h))
w, h = pygame.display.get_surface().get_size()
font = pygame.font.Font('freesansbold.ttf', 15)
font2 = pygame.font.Font('freesansbold.ttf', 30)
font3 = pygame.font.Font('freesansbold.ttf', 45)
img = pygame.image.load('trophy.png')
img = pygame.transform.scale(img, (200, 200))
colors = [(207, 23, 23), (6, 47, 196), (8, 161, 54), (201, 114, 26), (163, 148, 34), (38, 153, 171), (181, 27, 117),
          (92, 11, 191), (120, 120, 120), (94, 55, 16)]
one, two, three = [pygame.transform.scale(pygame.image.load(f'{n}.png'), (200, 200)) for n in ['one', 'two', 'three']]

# Change for player
code = 1
origx = 2000
origy = 2000

color = colors[code - 1]
color2 = (0, 0, 0)
speed = 1.5
size = 5000
darts = []
since = 2
tx = origx
ty = origy
rl_ud = [False, False]
run = True
invis = False
power = 'invisibility'
select = 1
powers = {'homing': (800, 550), 'speed': (800, 500), 'invisibility': (900, 450), 'rapid': (650, 500),
          'teleport': (500, 1), 'sniper': (1200, 400)}
ptime = 0
name = ''
use_power = [False, 0]
messages = []
state = 'start'
win = ['Well played, champion! Victory achieved!', 'Incredible! You’re the ultimate winner!',
       'Victory is yours! Enjoy the glory!', 'Amazing! You’ve earned this victory!']
choice = random.choice(win)
end = ''
place = ''
started = 0
last_time = 0
shrinking = False
scount = 0
scale_factor = 1
sin, cos = 0, 0

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
    global state, end, place, gamedata, started, darts, scount, messages
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
            scount = 500
            gamedata = []
            darts = []
        elif info[:1] == 'M':
            messages.append([info[1:], 200])


def draw_rectangle(s, x, y, width, height, c, t_x, t_y, rotation):
    pts = []
    radius = math.sqrt((height / 2) ** 2 + (width / 2) ** 2)
    angle = math.atan2(height / 2, width / 2)
    angles = [angle, -angle + math.pi, angle + math.pi, -angle]
    rot_radians = rotation
    for angle in angles:
        y_off = -1 * radius * math.sin(angle + rot_radians)
        x_off = radius * math.cos(angle + rot_radians)
        pts.append((x + x_off + t_x, y + y_off + t_y))
    pygame.draw.polygon(s, c, pts)


def draw_player(pos, a, c, n):
    cos0 = -math.cos(a)
    sin0 = -math.sin(a)
    pygame.draw.circle(screen, c, (
        w / 2 - tx * scale_factor + pos[0] * scale_factor, h / 2 - ty * scale_factor + pos[1] * scale_factor),
                       15 * scale_factor)
    draw_rectangle(screen, w / 2 - tx * scale_factor + pos[0] * scale_factor,
                   h / 2 - ty * scale_factor + pos[1] * scale_factor, 20 * scale_factor, 10 * scale_factor, c,
                   -cos0 * 10 * scale_factor, sin0 * 10 * scale_factor,
                   -math.asin(sin0) + (2 * math.asin(sin0) + math.pi) * (cos0 > 0))
    txt = font.render(n, True, color2)
    txtRect = txt.get_rect()
    txtRect.center = (w / 2 - tx * scale_factor + pos[0] * scale_factor,
                      h / 2 - ty * scale_factor + pos[1] * scale_factor - 30 * scale_factor)
    screen.blit(txt, txtRect)


listening = Thread(target=listen)
listening.start()

while run:
    w, h = pygame.display.get_surface().get_size()
    if state == 'game':
        mx, my = pygame.mouse.get_pos()
        hyp = math.dist((mx, my), (w / 2, h / 2))
        try:
            cos = round((w / 2 - mx) / hyp, 2)
            sin = round((my - h / 2) / hyp, 2)
        except ZeroDivisionError:
            pass
        screen = pygame.Surface(game.get_size(), pygame.SRCALPHA)
        game.fill((255, 255, 255))
        if time.time() / 30 > last_time + 1 and size > 500:
            last_time = time.time() / 30 + 5
            shrinking = True
        if shrinking:
            size -= 1
            scount += 1
            if ['Map shrinking', 1] not in messages:
                messages.insert(0, ['Map Shrinking', 1])
        if scount >= 500:
            shrinking = False
            last_time = time.time() / 30
            scount = 0

        if tx >= size / 2:
            tx = size / 2
        elif tx <= -size / 2:
            tx = -size / 2
        if ty >= size / 2:
            ty = size / 2
        elif ty <= -size / 2:
            ty = -size / 2
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
                gap = 1
            elif use_power[0] and power == 'sniper':
                gap = 4
            if pygame.mouse.get_pressed(3)[0] and since > gap:
                darts.append(
                    [[tx - 20 * cos, ty + 20 * sin], (255,),
                     -math.asin(sin) + (2 * math.asin(sin) + math.pi) * (cos > 0),
                     0, use_power[0] and power == 'sniper'])
                since = 0

        screen.fill((121, 135, 130), pygame.Rect(0, 0, w, h))
        pygame.draw.polygon(screen, (188, 204, 198),
                            [(w / 2 - tx * scale_factor - size * scale_factor / 2,
                              h / 2 - ty * scale_factor - size * scale_factor / 2),
                             (w / 2 - tx * scale_factor - size * scale_factor / 2,
                              h / 2 - ty * scale_factor + size * scale_factor / 2),
                             (w / 2 - tx * scale_factor + size * scale_factor / 2,
                              h / 2 - ty * scale_factor + size * scale_factor / 2),
                             (w / 2 - tx * scale_factor + size * scale_factor / 2,
                              h / 2 - ty * scale_factor - size * scale_factor / 2)])
        for val in range(5000 // 25 + 1):
            pygame.draw.line(screen, (204, 216, 211), (w / 2 - tx * scale_factor - 5000 * scale_factor / 2,
                                                       h / 2 - ty * scale_factor + 25 * val * scale_factor - 5000 / 2 * scale_factor),
                             (w / 2 - tx * scale_factor + 5000 * scale_factor / 2,
                              h / 2 - ty * scale_factor + 25 * val * scale_factor - 5000 * scale_factor / 2), 2)
            pygame.draw.line(screen, (204, 216, 211), (
                w / 2 - tx * scale_factor + 25 * val * scale_factor - 5000 * scale_factor / 2,
                h / 2 - ty * scale_factor - 5000 * scale_factor / 2),
                             (w / 2 - tx * scale_factor + 25 * val * scale_factor - 5000 * scale_factor / 2,
                              h / 2 - ty * scale_factor + 5000 * scale_factor / 2), 2)

        screen.fill((121, 135, 130), pygame.Rect(0, 0, w, h / 2 - ty * scale_factor - size * scale_factor / 2))
        screen.fill((121, 135, 130), pygame.Rect(0, 0, w / 2 - tx * scale_factor - size * scale_factor / 2, h))
        screen.fill((121, 135, 130), pygame.Rect(w / 2 - tx * scale_factor + size * scale_factor / 2, 0,
                                                 w / 2 + tx * scale_factor - size * scale_factor / 2, h))
        screen.fill((121, 135, 130), pygame.Rect(0, h / 2 - ty * scale_factor + size * scale_factor / 2, w,
                                                 h / 2 + ty * scale_factor - size * scale_factor / 2))
        points = [
            (w / 2 - tx * scale_factor - size * scale_factor / 2, h / 2 - ty * scale_factor - size * scale_factor / 2),
            (w / 2 - tx * scale_factor - size * scale_factor / 2, h / 2 - ty * scale_factor + size * scale_factor / 2),
            (w / 2 - tx * scale_factor + size * scale_factor / 2, h / 2 - ty * scale_factor + size * scale_factor / 2),
            (w / 2 - tx * scale_factor + size * scale_factor / 2, h / 2 - ty * scale_factor - size * scale_factor / 2)]
        for j in range(len(points)):
            pygame.draw.line(screen, (0, 0, 0), points[j - 1], points[j], 3)
        for d in darts:
            pygame.draw.circle(screen, color + d[1], (
                w / 2 - tx * scale_factor + d[0][0] * scale_factor, h / 2 - ty * scale_factor + d[0][1] * scale_factor),
                               5 * scale_factor)
        for d in range(len(darts)):
            darts[d][3] += 1
            if darts[d][3] > 80 + 20 * (use_power[0] and (power == 'homing' or power == 'rapid')) + 50 * darts[d][4] and darts[d][1][0] >= 30:
                darts[d][1] = (darts[d][1][0] - 30,)
            if use_power[0] and power == 'homing':
                hp = math.dist(((mx + tx - w / 2), (my + ty - h / 2)), (darts[d][0][0], darts[d][0][1]))
                darts[d][0][0] += 3.6 * ((mx + tx - w / 2) - darts[d][0][0]) / hp
                darts[d][0][1] -= -3.6 * ((my + ty - h / 2) - darts[d][0][1]) / hp
            else:
                darts[d][0][0] += math.cos(darts[d][2]) * (3.6 + 1.4 * darts[d][4])
                darts[d][0][1] -= math.sin(darts[d][2]) * (3.6 + 1.4 * darts[d][4])
        newdarts = []
        for d in darts:
            if d[1][0] >= 30 and (
                    not (use_power[0] and power == 'homing') or math.dist(((mx + tx - w / 2), (my + ty - h / 2)),
                                                                          (d[0][0], d[0][1])) > 3):
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
                if w / 2 - tx - size / 2 < mx < w / 2 - tx + size / 2 and h / 2 - ty - size / 2 < my < h / 2 - ty + size / 2:
                    tx += mx - w / 2
                    ty += my - h / 2
                    use_power = [False, 0]
                    ptime = 0
                else:
                    use_power = [False, 0]
            elif power == 'invisibility':
                invis = True
            elif power == 'sniper':
                scale_factor = 4 / 5

        if use_power[0] and use_power[1] > powers[power][1]:
            use_power = [False, 0]
            invis = False
            ptime = 0
            scale_factor = 1
        for p in gamedata:
            if not p[3]:
                draw_player(p[1], p[2], p[4], p[0])
            for d in p[5]:
                pygame.draw.circle(screen, p[4] + d[1], (
                    w / 2 - tx * scale_factor + d[0][0] * scale_factor,
                    h / 2 - ty * scale_factor + d[0][1] * scale_factor),
                                   5 * scale_factor)

        for p in gamedata:
            if math.dist((tx, ty), p[1]) < 30:
                sock.sendto(bytes(f'DEATH{p[0]}+{p[6]}={name}+{code}=crash', 'utf-8'), (HOST_IP, HOST_PORT))
            for d in p[5]:
                if math.dist(d[0], (tx, ty)) < 20:
                    sock.sendto(bytes(f'DEATH{p[0]}+{p[6]}={name}+{code}=kill', 'utf-8'), (HOST_IP, HOST_PORT))

        pygame.draw.circle(screen, color * (not invis) + color2 * invis, (w / 2, h / 2), 15 * scale_factor)
        draw_rectangle(screen, w / 2, h / 2, 20 * scale_factor, 10 * scale_factor, color * (not invis) + color2 * invis,
                       -cos * 10 * scale_factor, sin * 10 * scale_factor,
                       -math.asin(sin) + (2 * math.asin(sin) + math.pi) * (cos > 0))
        screen.fill((0, 0, 0), pygame.Rect(w / 2 - 100, h - 50, 200, 15))
        if not use_power[0]:
            screen.fill((247, 120, 22), pygame.Rect(w / 2 - 100, h - 50, 200 * (ptime / powers[power][0]), 15))
        else:
            screen.fill((247, 120, 22),
                        pygame.Rect(w / 2 - 100, h - 50, 200 * (1 - use_power[1] / powers[power][1]), 15))
        if not use_power[0] and ptime < powers[power][0]:
            text = font.render('Superpower Recharging...', True, (0, 0, 0))
            textRect = text.get_rect()
            textRect.center = (w / 2, h - 65)
            screen.blit(text, textRect)
        else:
            text = font.render('Press F or Space To Use', True, (0, 0, 0))
            textRect = text.get_rect()
            textRect.center = (w / 2, h - 65)
            screen.blit(text, textRect)
        surface = pygame.Surface((130, 130), pygame.SRCALPHA)
        surface.fill((0, 0, 0, 180))
        for p in gamedata:
            if not p[3]:
                pygame.draw.circle(surface, p[4], (65 + p[1][0] / size * 130, 65 + p[1][1] / size * 130), 3)
        pygame.draw.circle(surface, color, (65 + tx / size * 130, 65 + ty / size * 130), 3)
        screen.blit(surface, (w - 150, h - 150))
        if started == 150:
            sock.sendto(bytes('STARTED', 'utf-8'), (HOST_IP, HOST_PORT))
            started += 1
        if started >= 150:
            since += 0.1
            ptime += 1 * (ptime < powers[power][0])
        else:
            if started < 50:
                screen.blit(three, (w / 2 - 100, h / 2 - 350 + 250))
            elif started < 100:
                screen.blit(two, (w / 2 - 100, h / 2 - 350 + 250))
            else:
                screen.blit(one, (w / 2 - 100, h / 2 - 350 + 250))
            started += 1
        for m in range(len(messages)):
            surface = pygame.Surface((340, 40), pygame.SRCALPHA)
            surface.fill((255, 255, 255, 130))
            screen.blit(surface, (w - 340 - 15, 15 + m * 50))
            if messages[m][0] == 'Map Shrinking':
                text = font.render(messages[m][0], True, color)
            else:
                text = font.render(messages[m][0], True, color2)
            textRect = text.get_rect()
            textRect.center = (w - 340 - 15 + 170, 15 + m * 50 + 20)
            screen.blit(text, textRect)

        new_messages = []
        for m in range(len(messages)):
            messages[m][1] -= 1
            if messages[m][1] > 0:
                new_messages.append(messages[m])
        messages = new_messages[:]
        game.blit(screen, (0, 0))
        if use_power[0]:
            use_power[1] += 1
        data = ['\'' + name + '\'', str((tx, ty)), str(-math.asin(sin) + (2 * math.asin(sin) + math.pi) * (cos > 0)),
                str(invis),
                str(color), str(darts), str(code)]
        sock.sendto(bytes('[' + ', '.join(data) + ']', 'utf-8'), (HOST_IP, HOST_PORT))

    elif state == 'end' or state == 'win':
        mx, my = pygame.mouse.get_pos()
        screen = pygame.Surface(game.get_size(), pygame.SRCALPHA)
        game.fill((255, 255, 255, 255))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
        screen.fill((188, 204, 198), pygame.Rect(0, 0, w, h))
        for val in range(size // 25 + 1):
            pygame.draw.line(screen, (204, 216, 211), (w / 2 - size / 2, h / 2 + 25 * val - size / 2),
                             (w / 2 + size / 2, h / 2 + 25 * val - size / 2), 2)
            pygame.draw.line(screen, (204, 216, 211), (w / 2 + 25 * val - size / 2, h / 2 - size / 2),
                             (w / 2 + 25 * val - size / 2, h / 2 + size / 2), 2)
        pygame.draw.polygon(screen, (0, 0, 0),
                            [(w / 2 - 400, h / 2 - 300), (w / 2 - 400, h / 2 + 300), (w / 2 + 400, h / 2 + 300),
                             (w / 2 + 400, h / 2 - 300)])
        pygame.draw.polygon(screen, (255, 255, 255),
                            [(w / 2 - 398, h / 2 - 298), (w / 2 - 398, h / 2 + 298), (w / 2 + 398, h / 2 + 298),
                             (w / 2 + 398, h / 2 - 298)])
        if state == 'end':
            text = font2.render(end, True, (0, 0, 0))
        else:
            text = font2.render(choice, True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (w / 2, 120 - 350 + h / 2)
        screen.blit(text, textRect)
        text = font2.render(f'You got {place} place', True, color)
        textRect = text.get_rect()
        textRect.center = (w / 2, 200 - 350 + h / 2)
        screen.blit(text, textRect)
        if w / 2 - 130 < mx < w / 2 + 130 and h / 2 + 170 < my < h / 2 + 250:
            pygame.draw.rect(screen, (171, 171, 171), pygame.Rect(w / 2 - 130, h / 2 + 170, 260, 80))
        else:
            pygame.draw.rect(screen, color, pygame.Rect(w / 2 - 130, h / 2 + 170, 260, 80))
        screen.blit(img, (w / 2 - 100, 270 - 350 + h / 2))
        text = font2.render('New Game', True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (w / 2, 560 - 350 + h / 2)
        screen.blit(text, textRect)
        game.blit(screen, (0, 0))
        if pygame.mouse.get_pressed(3)[0] and w / 2 - 130 < mx < w / 2 + 130 and h / 2 + 170 < my < h / 2 + 250:
            state = 'start'
            choice = random.choice(win)
            tx = origx
            ty = origy
            messages = []
            speed = 1.5
            since = 2
            rl_ud = [False, False]
            invis = False
            ptime = 0
            use_power = [False, 0]
            name = ''
            time.sleep(0.3)

    elif state == 'start':
        mx, my = pygame.mouse.get_pos()
        screen = pygame.Surface(game.get_size(), pygame.SRCALPHA)
        game.fill((255, 255, 255, 255))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if len(name) < 15:
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
            pygame.draw.line(screen, (204, 216, 211), (w / 2 - size / 2, h / 2 + 25 * val - size / 2),
                             (w / 2 + size / 2, h / 2 + 25 * val - size / 2), 2)
            pygame.draw.line(screen, (204, 216, 211), (w / 2 + 25 * val - size / 2, h / 2 - size / 2),
                             (w / 2 + 25 * val - size / 2, h / 2 + size / 2), 2)
        pygame.draw.polygon(screen, (0, 0, 0),
                            [(w / 2 - 400, h / 2 - 300), (w / 2 - 400, h / 2 + 300), (w / 2 + 400, h / 2 + 300),
                             (w / 2 + 400, h / 2 - 300)])
        pygame.draw.polygon(screen, (255, 255, 255),
                            [(w / 2 - 398, h / 2 - 298), (w / 2 - 398, h / 2 + 298), (w / 2 + 398, h / 2 + 298),
                             (w / 2 + 398, h / 2 - 298)])
        text = font3.render('Battle Royale', True, color)
        textRect = text.get_rect()
        textRect.center = (w / 2, 120 - 350 + h / 2)
        screen.blit(text, textRect)
        if w / 2 - 130 < mx < w / 2 + 130 and h / 2 + 170 < my < h / 2 + 250:
            pygame.draw.rect(screen, (171, 171, 171), pygame.Rect(w / 2 - 130, h / 2 + 170, 260, 80))
        else:
            pygame.draw.rect(screen, color, pygame.Rect(w / 2 - 130, h / 2 + 170, 260, 80))
        text = font2.render('Start', True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (w / 2, 560 - 350 + h / 2)
        screen.blit(text, textRect)
        if time.time() // 0.3 % 2 == 0:
            text = font2.render('Name: ' + name, True, (0, 0, 0))
        else:
            text = font2.render('Name: ' + name + '_', True, (0, 0, 0))
        textRect = text.get_rect()
        if time.time() // 0.3 % 2 == 0:
            textRect.center = (w / 2, 250 - 350 + h / 2)
        else:
            textRect.center = (w / 2 + 9, 250 - 350 + h / 2)
        screen.blit(text, textRect)
        text = font2.render('Power:', True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (170 - 450 + w / 2, 395 - 350 + h / 2)
        screen.blit(text, textRect)
        x_offset = -450 + w / 2
        y_offset = -350 + h / 2
        if select != 1:
            pygame.draw.rect(screen, (171, 171, 171), pygame.Rect(250 + x_offset, 355 + y_offset, 150, 30))
        else:
            pygame.draw.rect(screen, color, pygame.Rect(250 + x_offset, 355 + y_offset, 150, 30))
            power = 'invisibility'
        if select != 2:
            pygame.draw.rect(screen, (171, 171, 171), pygame.Rect(430 + x_offset, 355 + y_offset, 150, 30))
        else:
            pygame.draw.rect(screen, color, pygame.Rect(430 + x_offset, 355 + y_offset, 150, 30))
            power = 'teleport'
        if select != 3:
            pygame.draw.rect(screen, (171, 171, 171), pygame.Rect(610 + x_offset, 355 + y_offset, 150, 30))
        else:
            pygame.draw.rect(screen, color, pygame.Rect(610 + x_offset, 355 + y_offset, 150, 30))
            power = 'speed'
        if select != 4:
            pygame.draw.rect(screen, (171, 171, 171), pygame.Rect(250 + x_offset, 405 + y_offset, 150, 30))
        else:
            pygame.draw.rect(screen, color, pygame.Rect(250 + x_offset, 405 + y_offset, 150, 30))
            power = 'homing'
        if select != 5:
            pygame.draw.rect(screen, (171, 171, 171), pygame.Rect(430 + x_offset, 405 + y_offset, 150, 30))
        else:
            pygame.draw.rect(screen, color, pygame.Rect(430 + x_offset, 405 + y_offset, 150, 30))
            power = 'rapid'
        if select != 6:
            pygame.draw.rect(screen, (171, 171, 171), pygame.Rect(610 + x_offset, 405 + y_offset, 150, 30))
        else:
            pygame.draw.rect(screen, color, pygame.Rect(610 + x_offset, 405 + y_offset, 150, 30))
            power = 'sniper'
        text = font.render('Invisibility', True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (325 + x_offset, 370 + y_offset)
        screen.blit(text, textRect)
        text = font.render('Teleport', True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (505 + x_offset, 370 + y_offset)
        screen.blit(text, textRect)
        text = font.render('Speed', True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (685 + x_offset, 370 + y_offset)
        screen.blit(text, textRect)
        text = font.render('Homing Shots', True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (325 + x_offset, 420 + y_offset)
        screen.blit(text, textRect)
        text = font.render('Rapid Fire', True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (505 + x_offset, 420 + y_offset)
        screen.blit(text, textRect)
        text = font.render('Sniper', True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (685 + x_offset, 420 + y_offset)
        screen.blit(text, textRect)
        if pygame.mouse.get_pressed(3)[0]:
            if 320 + x_offset < mx < 580 + x_offset and 520 + y_offset < my < 600 + y_offset:
                state = 'wait'
                time.sleep(0.3)
            if 250 + x_offset < mx < 400 + x_offset and 355 + y_offset < my < 385 + y_offset:
                select = 1
            if 430 + x_offset < mx < 580 + x_offset and 355 + y_offset < my < 385 + y_offset:
                select = 2
            if 610 + x_offset < mx < 760 + x_offset and 355 + y_offset < my < 385 + y_offset:
                select = 3
            if 250 + x_offset < mx < 400 + x_offset and 405 + y_offset < my < 435 + y_offset:
                select = 4
            if 430 + x_offset < mx < 580 + x_offset and 405 + y_offset < my < 435 + y_offset:
                select = 5
            if 610 + x_offset < mx < 760 + x_offset and 405 + y_offset < my < 435 + y_offset:
                select = 6
        game.blit(screen, (0, 0))
    elif state == 'wait':
        mx, my = pygame.mouse.get_pos()
        screen = pygame.Surface(game.get_size(), pygame.SRCALPHA)
        game.fill((255, 255, 255, 255))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
        screen.fill((188, 204, 198), pygame.Rect(0, 0, w, h))
        for val in range(size // 25 + 1):
            pygame.draw.line(screen, (204, 216, 211), (w / 2 - size / 2, h / 2 + 25 * val - size / 2),
                             (w / 2 + size / 2, h / 2 + 25 * val - size / 2), 2)
            pygame.draw.line(screen, (204, 216, 211), (w / 2 + 25 * val - size / 2, h / 2 - size / 2),
                             (w / 2 + 25 * val - size / 2, h / 2 + size / 2), 2)
        pygame.draw.polygon(screen, (0, 0, 0),
                            [(w / 2 - 400, h / 2 - 300), (w / 2 - 400, h / 2 + 300), (w / 2 + 400, h / 2 + 300),
                             (w / 2 + 400, h / 2 - 300)])
        pygame.draw.polygon(screen, (255, 255, 255),
                            [(w / 2 - 398, h / 2 - 298), (w / 2 - 398, h / 2 + 298), (w / 2 + 398, h / 2 + 298),
                             (w / 2 + 398, h / 2 - 298)])
        text = font3.render('Waiting for players...', True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (w / 2, h / 2)
        screen.blit(text, textRect)
        game.blit(screen, (0, 0))
    pygame.display.flip()
    clock.tick(60)
