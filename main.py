#sniper zoom, full screen
#position allocation, message stack

import pygame
import mysql.connector
import time
import math
import random
import socket
import threading
import json
from CopterData import Data

cnx = mysql.connector.connect(user='---', password='---', host='---', autocommit=True)

cursor = cnx.cursor()
cursor.execute("USE copterroyale;")

pygame.init()
pygame.font.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Copter Royale 2.0")

font_large = pygame.font.SysFont('Courier New', 60)
font_medium = pygame.font.SysFont('Courier New', 36)
font_small = pygame.font.SysFont('Courier New', 24)
font_mini = pygame.font.SysFont('Courier New', 20)
font_ultramini = pygame.font.SysFont('Courier New', 15)

logo = pygame.image.load("title.png")
logo = pygame.transform.smoothscale(logo, (300, 300))

clock = pygame.time.Clock()
FPS = 60

IP = "255.255.255.255"
PORT = 2456

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.bind(('', PORT))

state = Data()


def listening(state):
    while True:
        try:
            data, addr = sock.recvfrom(32768)
            message = json.loads(data.decode('utf-8'))
            if message['type'] == 'data':
                if message['user'] != state.user:
                    state.enemies[message['user']] = message['data']
                    
            elif message['type'] == 'hit':
                if message['shooter'] == state.user:
                    newbullets = []
                    for bullet in state.bullets:
                        if bullet['bid'] != message['bid']:
                            newbullets.append(bullet)
                    state.bullets = newbullets
                else:
                    newbullets = []
                    for bullet in state.enemies[message['shooter']][2]:
                        if bullet['bid'] != message['bid']:
                            newbullets.append(bullet)
                    state.enemies[message['shooter']][2] = newbullets
                    
            elif message['type'] == 'death':
                if message['shooter'] == state.user:
                    state.killcount += 1
                state.enemies.pop(message['user'], None)
        except:
            pass

def send(state):
    message = {
        'type': 'data',
        'user': state.user,
        'data': [
            (state.x, state.y),
            state.angle,
            state.bullets,
            state.pcolor[:3],
            state.power,
            state.name,
            state.health
        ]
    }
    sock.sendto(json.dumps(message).encode('utf-8'), (IP, PORT))
    
def draw_button(rect, text, font, mouse_pos, color, colorclick, textcolor):
    background_rect = rect.move(-2, 2)
    if rect.collidepoint(mouse_pos):
        current_color = colorclick
        pygame.draw.rect(screen, current_color, background_rect, border_radius=4)
        
        text_surf = font.render(text, True, textcolor)
        text_rect = text_surf.get_rect(center=background_rect.center)
        screen.blit(text_surf, text_rect)
    else:
        pygame.draw.rect(screen, colorclick, background_rect, border_radius=4)
        current_color = color
        pygame.draw.rect(screen, current_color, rect, border_radius=4)
        
        text_surf = font.render(text, True, textcolor)
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)

def draw_input_box(rect, text, is_active, coloractive, colorinactive, is_password=False):
    pygame.draw.rect(screen, coloractive if is_active else colorinactive, rect, 2)
    display_text = '*' * len(text) if is_password else text
    txt_surface = font_small.render(display_text, True, (0, 0, 0))
    screen.blit(txt_surface, (rect.x + 10, rect.y + 8))

def create_hue_slider(width, height, saturation=0.8, value=0.95):
    slider = pygame.Surface((width, height))
    for x in range(width):
        color = pygame.Color(0)
        h = x / width * 360
        s = saturation
        v = value
        color.hsva = (h, s * 100, v * 100, 100)
        for y in range(height):
            slider.set_at((x, y), color)
    return slider

def draw_shield_glow(surf, x, y, radius, color, layers=10):
    x = x - state.x + WIDTH // 2
    y = y - state.y + HEIGHT // 2
    for i in range(layers):
        alpha = max(0, 255 - i * 25)
        glow_color = (*color, alpha)
        pygame.draw.circle(surf, glow_color, (x, y), radius + i, width=2)

def draw_player(name, color, x, y, angle, health):
    x = x - state.x + WIDTH // 2
    y = y - state.y + HEIGHT // 2
    pygame.draw.circle(screen, color, (x, y), 15)

    gun_length = 20
    gun_width = 10
    end_x = x + math.cos(angle) * gun_length
    end_y = y + math.sin(angle) * gun_length

    dx = end_x - x
    dy = end_y - y

    length = math.hypot(dx, dy)
    if length == 0:
        length = 1
    dx /= length
    dy /= length

    px = -dy
    py = dx

    half_w = gun_width / 2
    points = [
        (x + px * half_w, y + py * half_w),
        (x - px * half_w, y - py * half_w),
        (end_x - px * half_w, end_y - py * half_w),
        (end_x + px * half_w, end_y + py * half_w)
    ]

    pygame.draw.polygon(screen, color, points)
    
    health = max(0, min(100, health))
    pygame.draw.rect(screen, color, pygame.Rect(x - 25, y - 35, 50 * (health / 100), 6))
    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(x - 25, y - 35, 50.5, 6.5), 1)


    text = font_ultramini.render(name, True, (0, 0, 0))
    text_rect = text.get_rect(center=(x, y - 50))
    screen.blit(text, text_rect)

def draw_grid(mapwidth, mapheight, gridsize=20, color=(170, 170, 170)):
    pygame.draw.rect(screen, (230, 230, 230), pygame.Rect(-state.x-mapwidth/2+400, -state.y-mapheight/2+300, mapwidth, mapheight))
    for i in range(int(mapwidth/gridsize)+1):
        pygame.draw.line(screen, color, (-state.x+i*gridsize-mapwidth/2+400, 300-state.y-mapheight/2), (-state.x+i*gridsize-mapwidth/2+400, 300-state.y+mapheight/2))
    for i in range(int(mapheight/gridsize)+1):
        pygame.draw.line(screen, color, (400-state.x-mapwidth/2, -state.y+i*gridsize-mapheight/2+300), (400-state.x+mapwidth/2, -state.y+i*gridsize-mapheight/2+300))
    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(-state.x-mapwidth/2+400, -state.y-mapheight/2+300, mapwidth+1, mapheight+1), 3)

def draw_minimap(map_width, map_height, minimap_size=120, margin=10):
    minimap_surface = pygame.Surface((minimap_size, minimap_size), pygame.SRCALPHA)

    minimap_surface.fill((50, 50, 50, 230))

    scale_x = minimap_size / map_width
    scale_y = minimap_size / map_height

    player_x = (state.x + map_width // 2) * scale_x
    player_y = (state.y + map_height // 2) * scale_y

    for player in state.enemies:
        dat = state.enemies[player]
        player_x = (dat[0][0] + map_width // 2) * scale_x
        player_y = (dat[0][1] + map_height // 2) * scale_y
        if dat[4] != 'invis':
            pygame.draw.circle(minimap_surface, dat[3], (player_x, player_y), 2)

    player_x = (state.x + map_width // 2) * scale_x
    player_y = (state.y + map_height // 2) * scale_y
    
    pygame.draw.circle(minimap_surface, state.pcolor, (player_x, player_y), 2)
    screen.blit(minimap_surface, (WIDTH - minimap_size - margin, HEIGHT - minimap_size - margin))

def fire_bullet():
    bullet_speed = 4.2

    bx = state.x + math.cos(state.angle) * 20
    by = state.y + math.sin(state.angle) * 20

    if state.power == 'sniper':    
        bullet = {
            "x": bx,
            "y": by,
            "velocity": bullet_speed*2,
            "angle": state.angle,
            "damage": 40,
            "lifetime": 2.2,
            "starttime": time.time(),
            "color": state.pcolor[:3],
            "alpha": 255,
            "type": 5,
            "bid": state.bidval
        }
        state.bidval += 1
        state.bullets.append(bullet)
    elif state.power == 'backshot':
        bullet1 = {
            "x": bx,
            "y": by,
            "velocity": bullet_speed,
            "angle": state.angle,
            "damage": 20,
            "lifetime": 1.5,
            "starttime": time.time(),
            "color": state.pcolor[:3],
            "alpha": 255,
            "type": 5,
            "bid": state.bidval
        }
        state.bidval += 1
        bullet2 = {
            "x": bx,
            "y": by,
            "velocity": bullet_speed,
            "angle": state.angle+math.pi,
            "damage": 20,
            "lifetime": 1.5,
            "starttime": time.time(),
            "color": state.pcolor[:3],
            "alpha": 255,
            "type": 5,
            "bid": state.bidval
        }
        state.bidval += 1
        state.bullets.append(bullet1)
        state.bullets.append(bullet2)
    elif state.power == 'double':
        dx = math.cos(state.angle + math.pi / 2) * 8
        dy = math.sin(state.angle + math.pi / 2) * 8
        bullet1 = {
            "x": bx+dx,
            "y": by+dy,
            "velocity": bullet_speed,
            "angle": state.angle,
            "damage": 20,
            "lifetime": 1.5,
            "starttime": time.time(),
            "color": state.pcolor[:3],
            "alpha": 255,
            "type": 5,
            "bid": state.bidval
        }
        state.bidval += 1
        bullet2 = {
            "x": bx-dx,
            "y": by-dy,
            "velocity": bullet_speed,
            "angle": state.angle,
            "damage": 20,
            "lifetime": 1.5,
            "starttime": time.time(),
            "color": state.pcolor[:3],
            "alpha": 255,
            "type": 5,
            "bid": state.bidval
        }
        state.bidval += 1
        state.bullets.append(bullet1)
        state.bullets.append(bullet2)
    elif state.power == 'shotgun':
        for i in range(5):
            bullet = {
                "x": bx,
                "y": by,
                "velocity": bullet_speed,
                "angle": state.angle+(math.pi/15)*(i-2),
                "damage": 7,
                "lifetime": 1.5,
                "starttime": time.time(),
                "color": state.pcolor[:3],
                "alpha": 255,
                "type": 5,
                "bid": state.bidval
            }
            state.bidval += 1
            state.bullets.append(bullet)
    elif state.power == 'blast':
        for i in range(24):
            bullet = {
                "x": state.x,
                "y": state.y,
                "velocity": bullet_speed*0.8,
                "angle": state.angle+(math.pi/12)*i,
                "damage": 20,
                "lifetime": 1,
                "starttime": time.time(),
                "color": state.pcolor[:3],
                "alpha": 255,
                "type": 5,
                "bid": state.bidval
            }
            state.bidval += 1
            state.bullets.append(bullet)
    elif state.power == 'charge':
        bullet = {
            "x": bx,
            "y": by,
            "velocity": bullet_speed*1.25,
            "angle": state.angle,
            "damage": 20,
            "lifetime": 1.75,
            "starttime": time.time(),
            "color": state.pcolor[:3],
            "alpha": 255,
            "type": 5,
            "bid": state.bidval
        }
        state.bidval += 1
        state.bullets.append(bullet)
    elif state.power == 'homing':
        bullet = {
            "x": bx,
            "y": by,
            "velocity": bullet_speed,
            "angle": state.angle,
            "damage": 20,
            "lifetime": 3,
            "starttime": time.time(),
            "color": state.pcolor[:3],
            "alpha": 255,
            "type": 5,
            "bid": state.bidval
        }
        state.bidval += 1
        state.bullets.append(bullet)
    else:
        bullet = {
            "x": bx,
            "y": by,
            "velocity": bullet_speed,
            "angle": state.angle,
            "damage": 20,
            "lifetime": 1.25,
            "starttime": time.time(),
            "color": state.pcolor[:3],
            "alpha": 255,
            "type": 5,
            "bid": state.bidval
        }
        state.bidval += 1
        state.bullets.append(bullet)

def update_bullets():
    new_bullets = []
    mouse_x, mouse_y = pygame.mouse.get_pos()
    world_mouse_x = state.x + (mouse_x - WIDTH // 2)
    world_mouse_y = state.y + (mouse_y - HEIGHT // 2)
    
    for bullet in state.bullets:
        if state.power == "homing":
            dx = world_mouse_x - bullet["x"]
            dy = world_mouse_y - bullet["y"]
            target_angle = math.atan2(dy, dx)

            current_angle = bullet["angle"]
            turn_speed = 0.2
            angle_diff = (target_angle - current_angle + math.pi) % (2 * math.pi) - math.pi
            bullet["angle"] += max(-turn_speed, min(turn_speed, angle_diff))
            
        bullet["x"] += math.cos(bullet["angle"]) * bullet["velocity"]
        bullet["y"] += math.sin(bullet["angle"]) * bullet["velocity"]
        if time.time()-bullet["starttime"] > bullet["lifetime"]*0.7:
            fade = (bullet["lifetime"]-time.time()+bullet["starttime"]) / (bullet["lifetime"]*0.7)
            bullet["alpha"] = int(255 * fade)
        if state.power == 'charge':
            inx = state.bullets.index(bullet)
            state.bullets[inx]['damage'] += 0.2
            state.bullets[inx]['type'] += 0.12
        if time.time()-bullet["starttime"] < bullet["lifetime"]:
            new_bullets.append(bullet)
    state.bullets = new_bullets

def draw_bullets():
    for bullet in state.bullets:        
        screen_x = bullet["x"] - state.x + WIDTH // 2
        screen_y = bullet["y"] - state.y + HEIGHT // 2

        if bullet["alpha"] <= 0:
            continue
        
        r, g, b = bullet["color"][:3]
            
        bullet_surf = pygame.Surface((2*bullet['type'], 2*bullet['type']), pygame.SRCALPHA)
        pygame.draw.circle(bullet_surf, (r, g, b, bullet["alpha"]), (bullet['type'], bullet['type']), bullet['type'])
        screen.blit(bullet_surf, (screen_x - bullet['type'], screen_y - bullet['type']))

def draw_enemy_bullets():
    for player in state.enemies:
        dat = state.enemies[player]
        for bullet in dat[2]:        
            screen_x = bullet["x"] - state.x + WIDTH // 2
            screen_y = bullet["y"] - state.y + HEIGHT // 2

            if bullet["alpha"] <= 0:
                continue
            
            r, g, b = bullet["color"][:3]
                
            bullet_surf = pygame.Surface((2*bullet['type'], 2*bullet['type']), pygame.SRCALPHA)
            pygame.draw.circle(bullet_surf, (r, g, b, bullet["alpha"]), (bullet['type'], bullet['type']), bullet['type'])
            screen.blit(bullet_surf, (screen_x - bullet['type'], screen_y - bullet['type']))

def login(state):
    mouse_pos = pygame.mouse.get_pos()

    login_button = pygame.Rect(WIDTH/2 - 225, 440, 200, 50)
    new_user_button = pygame.Rect(WIDTH/2 + 25, 440, 200, 50)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            state.running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if login_button.collidepoint(event.pos):
                state.username_text, state.password_text, state.loginerror = "", "", ""
                state.frame = "logging"
            elif new_user_button.collidepoint(event.pos):
                state.username_text, state.password_text, state.loginerror = "", "", ""
                state.frame = "newuser"

    screen.fill((200, 200, 200))
    logo_rect = logo.get_rect(center=(WIDTH/2, 170))
    screen.blit(logo, logo_rect)

    draw_button(login_button, "Login", font_medium, mouse_pos, (0, 95, 187), (0, 125, 222), (0, 0, 0))
    draw_button(new_user_button, "New User", font_medium, mouse_pos, (0, 95, 187), (0, 125, 222), (0, 0, 0))

def logging(typeval, state):
    mouse_pos = pygame.mouse.get_pos()

    back_button = pygame.Rect(20, HEIGHT-70, 200, 50)
    enter_button = pygame.Rect(WIDTH - 220, HEIGHT-70, 200, 50)
    input_box_user = pygame.Rect(WIDTH/2 - 150, 350, 300, 40)
    input_box_pass = pygame.Rect(WIDTH/2 - 150, 430, 300, 40)
    

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            state.running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if back_button.collidepoint(event.pos):
                state.frame = "login"
            elif enter_button.collidepoint(event.pos):
                if typeval == 'old':
                    query = f"SELECT password FROM users WHERE BINARY username = '{state.username_text}';"
                    cursor.execute(query)
                    data = cursor.fetchone()
                    query = f"SELECT state FROM status WHERE BINARY user = '{state.username_text}';"
                    cursor.execute(query)
                    data2 = cursor.fetchone()
                    if data is None or len(state.username_text) < 1 or len(state.password_text) < 1:
                        state.loginerror = "Invalid username/password"
                    else:
                        if data[0] == state.password_text:
                            if data2[0] == 'i':
                                state.user = state.username_text
                                state.frame = "home"
                                query = f"SELECT r, g, b FROM player WHERE BINARY user = '{state.user}';"
                                cursor.execute(query)
                                state.pcolor = cursor.fetchone()

                                query = f"SELECT name FROM player WHERE BINARY user = '{state.user}';"
                                cursor.execute(query)
                                state.name = cursor.fetchone()[0]
                                query = f"UPDATE status SET state = 'a' WHERE BINARY user = '{state.user}';"
                                cursor.execute(query)
                                if state.name is None:
                                    state.name = ""
                                    query = f"UPDATE player SET name = '' WHERE BINARY user = '{state.user}';"
                                    cursor.execute(query)
                            else:
                                state.loginerror = "Logged in elsewhere"
                        else:
                            state.loginerror = "Invalid username/password"
                else:
                    query = f"SELECT password FROM users WHERE BINARY username = '{state.username_text}';"
                    cursor.execute(query)
                    data = cursor.fetchone()
                    if data is not None:
                        state.loginerror = "Username taken"
                    else:
                        if len(state.username_text) < 1 or len(state.password_text) < 1:
                            state.loginerror = "Invalid username/password"
                        else:
                            query = f"INSERT INTO users VALUES ('{state.username_text}', '{state.password_text}');"
                            cursor.execute(query)
                            query = f"INSERT INTO player VALUES ('{state.username_text}', '', 242, 53, 48);"
                            cursor.execute(query)
                            state.user = state.username_text
                            query = f"INSERT INTO stats (user) VALUES ('{state.user}');"
                            cursor.execute(query)
                            query = f"INSERT INTO status VALUES ('{state.user}', 'a');"
                            cursor.execute(query)
                            state.pcolor = (242, 53, 48)
                            state.name = ""
                            state.frame = "home"
            if input_box_user.collidepoint(event.pos):
                state.active_box = "user"
            elif input_box_pass.collidepoint(event.pos):
                state.active_box = "pass"
            else:
                state.active_box = None

        elif event.type == pygame.KEYDOWN:
            if state.active_box == "user":
                if event.key == pygame.K_BACKSPACE:
                    state.username_text = state.username_text[:-1]
                    state.username_text = state.username_text.strip()
                elif event.key == pygame.K_TAB:
                    state.active_box = "pass"
                elif event.key <= 127 and event.unicode.isprintable() and len(state.username_text) < 20:
                    state.username_text += event.unicode
                    state.username_text = state.username_text.strip()
            elif state.active_box == "pass":
                if event.key == pygame.K_BACKSPACE:
                    state.password_text = state.password_text[:-1]
                    state.password_text = state.password_text.strip()
                elif event.key == pygame.K_TAB:
                    state.active_box = "user"
                elif event.key <= 127 and event.unicode.isprintable() and len(state.password_text) < 20:
                    state.password_text += event.unicode
                    state.password_text = state.password_text.strip()
 

    screen.fill((200, 200, 200))
    logo_rect = logo.get_rect(center=(WIDTH/2, 170))

    draw_input_box(input_box_user, state.username_text, state.active_box == "user", (0, 125, 222), (0, 95, 187), is_password=False)
    draw_input_box(input_box_pass, state.password_text, state.active_box == "pass", (0, 125, 222), (0, 95, 187), is_password=True)

    label_user = font_small.render("Username:", True, (0, 0, 0))
    label_pass = font_small.render("Password:", True, (0, 0, 0))
    screen.blit(label_user, (input_box_user.x, input_box_user.y - 25))
    screen.blit(label_pass, (input_box_pass.x, input_box_pass.y - 25))
    
    screen.blit(logo, logo_rect)
    text_surface = font_small.render(state.loginerror, True, (239, 37, 35))
    text_rect = text_surface.get_rect(center=(WIDTH/2, 500))
    screen.blit(text_surface, text_rect)

    draw_button(back_button, "Back", font_medium, mouse_pos, (0, 95, 187), (0, 125, 222), (0, 0, 0))
    draw_button(enter_button, "Enter", font_medium, mouse_pos, (0, 95, 187), (0, 125, 222), (0, 0, 0))

def home(state):
    mouse_pos = pygame.mouse.get_pos()

    out_button = pygame.Rect(20, HEIGHT-70, 200, 50)
    stats_button = pygame.Rect(WIDTH - 220, HEIGHT-70, 200, 50)
    play_button = pygame.Rect(300, HEIGHT-70, 200, 50)
    color_button = pygame.Rect(WIDTH/2-100, 425, 50, 50)
    input_box_name = pygame.Rect(WIDTH/2 - 110, 350, 300, 40)

    slider_width = 220
    slider_height = 20
    slider_x = WIDTH//2 - slider_width//2 + 80
    slider_y = 440

    slider_surface = create_hue_slider(slider_width, slider_height)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            state.running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if color_button.collidepoint(event.pos):
                state.changecolor = not state.changecolor
            if slider_x <= event.pos[0] <= slider_x + slider_width and slider_y <= event.pos[1] <= slider_y + slider_height and state.changecolor:
                hue = (event.pos[0] - slider_x) / slider_width * 360
                color = pygame.Color(0)
                color.hsva = (hue, 80, 95, 100)
                state.pcolor = color

                query = f"UPDATE player SET r = {state.pcolor.r}, g = {state.pcolor.g}, b = {state.pcolor.b} WHERE BINARY user = '{state.user}';"
                cursor.execute(query)
            elif stats_button.collidepoint(event.pos):
                state.frame = 'stats'
                state.changecolor = False

                query = f"SELECT won, topthree, kills, kills/games, maxkills FROM stats WHERE BINARY user = '{state.user}';"
                cursor.execute(query)
                stat = cursor.fetchone()

                state.user_stats["Games Won"] = stat[0];
                state.user_stats["Top 3 Finishes"] = stat[1];
                state.user_stats["Total Kills"] = stat[2];
                state.user_stats["Average Kills"] = stat[3];
                state.user_stats["Max Kills"] = stat[4];        
                
            elif out_button.collidepoint(event.pos):
                state.frame = 'login'
                query = f"UPDATE status SET state = 'i' WHERE BINARY user = '{state.user}';"
                cursor.execute(query)
                state.user = None
                state.user_stats = {
                    "Games Won": None,
                    "Top 3 Finishes": None,
                    "Total Kills": None,
                    "Average Kills": None,
                    "Max Kills": None
                }
                state.active_box = None
                state.changecolor = False            

            elif play_button.collidepoint(event.pos):
                state.barsize = 0
                state.bargoal = 0
                query = f"SELECT mode FROM game;"
                cursor.execute(query)
                val = cursor.fetchone()[0]
                if val in ('ffa', 'team', 'choose'):
                    state.frame = 'power'
                elif val == 'off':
                    state.frame = 'power'
                
            if input_box_name.collidepoint(event.pos):
                state.active_box = "name"
            else:
                state.active_box = None

        elif event.type == pygame.MOUSEMOTION and pygame.mouse.get_pressed()[0]:
            if slider_x <= event.pos[0] <= slider_x + slider_width and slider_y <= event.pos[1] <= slider_y + slider_height and state.changecolor:
                hue = (event.pos[0] - slider_x) / slider_width * 360
                color = pygame.Color(0)
                color.hsva = (hue, 80, 95, 100)
                state.pcolor = color

                query = f"UPDATE player SET r = {state.pcolor.r}, g = {state.pcolor.g}, b = {state.pcolor.b} WHERE BINARY user = '{state.user}';"
                cursor.execute(query)

        elif event.type == pygame.KEYDOWN:                
            if state.active_box == "name":
                if event.key == pygame.K_BACKSPACE:
                    state.name = state.name[:-1]
                    state.name = state.name.strip()
                    query = f"UPDATE player SET name = '{state.name}' WHERE BINARY user = '{state.user}';"
                    cursor.execute(query)
                elif event.key <= 127 and event.unicode.isprintable() and len(state.name) < 20:
                    state.name += event.unicode
                    state.name = state.name.strip()
                    query = f"UPDATE player SET name = '{state.name}' WHERE BINARY user = '{state.user}';"
                    cursor.execute(query)
 

    screen.fill((200, 200, 200))
    logo_rect = logo.get_rect(center=(WIDTH/2, 170))
    screen.blit(logo, logo_rect)
    
    text_surface = font_small.render("Color: ", True, (0, 0, 0))
    text_rect = text_surface.get_rect(center=(WIDTH/2-150, 450))
    screen.blit(text_surface, text_rect)

    draw_button(color_button, "", font_medium, mouse_pos, state.pcolor, tuple(map(lambda x: x-40, state.pcolor)), (0, 0, 0))
    
    text_surface = font_small.render("Name: ", True, (0, 0, 0))
    text_rect = text_surface.get_rect(center=(WIDTH/2-155, 370))
    screen.blit(text_surface, text_rect)
    
    draw_input_box(input_box_name, state.name, state.active_box == "name", (0, 125, 222), (0, 95, 187), is_password=False)

    draw_button(stats_button, "Stats", font_medium, mouse_pos, (0, 95, 187), (0, 125, 222), (0, 0, 0))
    draw_button(out_button, "Log Out", font_medium, mouse_pos, (0, 95, 187), (0, 125, 222), (0, 0, 0))
    draw_button(play_button, "Play", font_medium, mouse_pos, (0, 95, 187), (0, 125, 222), (0, 0, 0))

    if state.changecolor:
        screen.blit(slider_surface, (slider_x, slider_y))
        pygame.draw.rect(screen, (0, 0, 0), (slider_x, slider_y, slider_width, slider_height), 2)

        color_obj = pygame.Color(*state.pcolor)
        hue_pos = int((color_obj.hsva[0] / 360) * slider_width)
        pygame.draw.line(screen, (0, 0, 0), (slider_x + hue_pos, slider_y), (slider_x + hue_pos, slider_y + slider_height-2), 2)

def stats(state):
    mouse_pos = pygame.mouse.get_pos()

    back_button = pygame.Rect(20, HEIGHT-70, 200, 50)
    leader_button = pygame.Rect(WIDTH - 220, HEIGHT-70, 200, 50)
    

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            state.running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if back_button.collidepoint(event.pos):
                state.frame = "home"
            elif leader_button.collidepoint(event.pos):
                state.frame = "leader"
                state.selected_tab = "Games Won"
                state.leaderboard_data = {
                    "Games Won": [],
                    "Top 3 Finishes": [],
                    "Total Kills": [],
                    "Average Kills": [],
                    "Max Kills": []
                }
                query = f"SELECT user, won FROM stats ORDER BY won DESC;"
                cursor.execute(query)
                dat = cursor.fetchall()
                for i in range(min(5, len(dat))):
                    state.leaderboard_data["Games Won"].append(dat[i])

                query = f"SELECT user, topthree FROM stats ORDER BY topthree DESC;"
                cursor.execute(query)
                dat = cursor.fetchall()
                for i in range(min(5, len(dat))):
                    state.leaderboard_data["Top 3 Finishes"].append(dat[i])

                query = f"SELECT user, kills FROM stats ORDER BY kills DESC;"
                cursor.execute(query)
                dat = cursor.fetchall()
                for i in range(min(5, len(dat))):
                    state.leaderboard_data["Total Kills"].append(dat[i])

                query = f"SELECT user, kills/games FROM stats ORDER BY kills/games DESC;"
                cursor.execute(query)
                dat = cursor.fetchall()
                for i in range(min(5, len(dat))):
                    state.leaderboard_data["Average Kills"].append(dat[i])

                query = f"SELECT user, maxkills FROM stats ORDER BY maxkills DESC;"
                cursor.execute(query)
                dat = cursor.fetchall()
                for i in range(min(5, len(dat))):
                    state.leaderboard_data["Max Kills"].append(dat[i])
 

    screen.fill((200, 200, 200))
    logo_rect = logo.get_rect(center=(WIDTH/2, 170))
    screen.blit(logo, logo_rect)

    draw_button(back_button, "Back", font_medium, mouse_pos, (0, 95, 187), (0, 125, 222), (0, 0, 0))
    draw_button(leader_button, "Ranks", font_medium, mouse_pos, (0, 95, 187), (0, 125, 222), (0, 0, 0))

    row_height = 30
    col_width = 250
    num_rows = len(state.user_stats)
    num_cols = 2
    padding = 10

    table_width = num_cols * col_width
    table_height = num_rows * row_height

    stat_x = (WIDTH - table_width) // 2
    stat_y_start = (HEIGHT - table_height) // 2 + 110

    for i in range(num_rows + 1):
        y = stat_y_start + i * row_height
        pygame.draw.line(screen, (120, 120, 120), (stat_x, y), (stat_x + table_width, y), 1)

    pygame.draw.line(screen, (120, 120, 120), (stat_x + col_width, stat_y_start), (stat_x + col_width, stat_y_start + table_height), 1)
    pygame.draw.line(screen, (120, 120, 120), (stat_x, stat_y_start), (stat_x, stat_y_start + table_height), 1)
    pygame.draw.line(screen, (120, 120, 120), (stat_x + 2*col_width, stat_y_start), (stat_x + 2*col_width, stat_y_start + table_height), 1)

    for i, (label, value) in enumerate(state.user_stats.items()):
        label_surface = font_mini.render(label, True, (0, 0, 0))
        value_surface = font_mini.render(str(value), True, (0, 0, 0))

        label_pos = label_surface.get_rect(midleft=(stat_x + 10, stat_y_start + i * row_height + row_height // 2))
        value_pos = value_surface.get_rect(midleft=(stat_x + col_width + 10, stat_y_start + i * row_height + row_height // 2))

        screen.blit(label_surface, label_pos)
        screen.blit(value_surface, value_pos)

def leader(state):
    mouse_pos = pygame.mouse.get_pos()

    back_button = pygame.Rect(20, HEIGHT - 70, 200, 50)

    pad = 20
    tabs = list(state.leaderboard_data.keys())
    tab_width = 200
    tab_height = 35
    tab_padding = 2

    max_tab_area = HEIGHT - 30
    max_visible_tabs = (HEIGHT - 100) // (tab_height + tab_padding)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            state.running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if back_button.collidepoint(event.pos):
                state.frame = "stats"

            else:
                for i, tab in enumerate(tabs):
                    y = 330 + i * (tab_height + tab_padding)
                    if y + tab_height > HEIGHT - 80:
                        break
                    rect = pygame.Rect(pad, y, tab_width, tab_height)
                    if rect.collidepoint(event.pos):
                        state.selected_tab = tab

    screen.fill((200, 200, 200))
    logo_rect = logo.get_rect(center=(WIDTH/2, 170))
    screen.blit(logo, logo_rect)

    for i, tab in enumerate(tabs):
        y = 330 + i * (tab_height + tab_padding)
        if y + tab_height > HEIGHT - 80:
            break
        rect = pygame.Rect(pad, y, tab_width, tab_height)
        is_selected = (tab == state.selected_tab)
        is_hovered = rect.collidepoint(mouse_pos)

        color = (0, 95, 187) if is_selected else (0, 125, 222) if is_hovered else (100, 100, 100)

        tab_surface = pygame.Surface((tab_width, tab_height), pygame.SRCALPHA)
        pygame.draw.rect(tab_surface, color, (0, 0, tab_width, tab_height),border_top_left_radius=5, border_bottom_left_radius=5)
        screen.blit(tab_surface, (rect.x, rect.y))

        label = font_mini.render(tab, True, (255, 255, 255))
        screen.blit(label, (rect.x + 10, rect.y + (tab_height - label.get_height()) // 2))

    stat_x = 250
    stat_y_start = 330
    row_height = 36.2
    num_rows = len(tabs)
    num_cols = 3
    col_width = [70, 350, 100]
    table_width = sum(col_width)
    table_height = row_height * num_rows

    for i in range(num_rows + 1):
        y = stat_y_start + i * row_height
        pygame.draw.line(screen, (120, 120, 120), (stat_x, y), (stat_x + table_width, y), 1)

    for i in range(num_cols + 1):
        x = stat_x + sum(col_width[:i])
        pygame.draw.line(screen, (120, 120, 120), (x, stat_y_start), (x, stat_y_start + table_height), 1)

    for i, (user_id, score) in enumerate(state.leaderboard_data[state.selected_tab]):
        rank = str(i + 1)+"."

        rank_surface = font_mini.render(rank, True, (0, 0, 0))
        user_surface = font_mini.render(user_id, True, (0, 0, 0))
        user_surface_same = font_mini.render(user_id + " (You)", True, (0, 95, 187))
        score_surface = font_mini.render(str(score), True, (0, 0, 0))

        rank_pos = rank_surface.get_rect(midleft=(stat_x + 10, 2+stat_y_start + i * row_height + row_height // 2))
        user_pos = user_surface.get_rect(midleft=(stat_x + col_width[0] + 10, 2+stat_y_start + i * row_height + row_height // 2))
        score_pos = score_surface.get_rect(midleft=(stat_x + col_width[0]+col_width[1] + 10, 2+stat_y_start + i * row_height + row_height // 2))

        screen.blit(rank_surface, rank_pos)
        if user_id != state.user:
            screen.blit(user_surface, user_pos)
        else:
            screen.blit(user_surface_same, user_pos)
        screen.blit(score_surface, score_pos)

    draw_button(back_button, "Back", font_medium, mouse_pos, (0, 95, 187), (0, 125, 222), (0, 0, 0))
    
def waiting(state):
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            state.running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            pass
        
    screen.fill((200, 200, 200))
    logo_rect = logo.get_rect(center=(WIDTH/2, 170))
    screen.blit(logo, logo_rect)

    text_surface = font_medium.render("Loading...", True, (0, 0, 0))
    text_rect = text_surface.get_rect(center=(WIDTH/2, 420))
    screen.blit(text_surface, text_rect)

    now = time.time()
    if now > state.lastcheck + 1:
        state.lastcheck = now
        query = f"SELECT count(*) FROM status WHERE state = 'j';"
        cursor.execute(query)
        joined = cursor.fetchone()[0]
        query = f"SELECT count(*) FROM status WHERE state = 'a';"
        cursor.execute(query)
        active = cursor.fetchone()[0]
        state.bargoal = 400*joined/(joined+active)
        
        
    speed = 400
    state.barsize += min(speed, abs(state.bargoal - state.barsize)) * (1 if state.bargoal > state.barsize else -1)

    pygame.draw.rect(screen,(0, 125, 222), (200, 465, state.barsize, 30))
    pygame.draw.rect(screen,(0, 95, 187), (200, 465, 400, 30), 5)

    if 399 < state.barsize < 401:
        state.frame = 'game'
        state.starttime = time.time()
        state.lasttime = time.time()
        query = f"SELECT mode FROM game;"
        cursor.execute(query)
        val = cursor.fetchone()[0]
        if val in ('ffa', 'team') and state.host:
            query = f"UPDATE game SET mode = '{val}play';"
            cursor.execute(query)

def mode(state):
    mouse_pos = pygame.mouse.get_pos()

    ffa_button = pygame.Rect(WIDTH/2 - 225, 440, 200, 50)
    team_button = pygame.Rect(WIDTH/2 + 25, 440, 200, 50)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            state.running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if ffa_button.collidepoint(event.pos):
                query = f"UPDATE game SET mode = 'ffa';"
                cursor.execute(query)
                state.frame = 'wait'
                query = f"UPDATE status SET state = 'j' WHERE BINARY user = '{state.user}';"
                cursor.execute(query)
                state.mode = 'ffa'
                
            elif team_button.collidepoint(event.pos):
                query = f"UPDATE game SET mode = 'team';"
                cursor.execute(query)
                state.frame = 'wait'
                query = f"UPDATE status SET state = 'j' WHERE BINARY user = '{state.user}';"
                cursor.execute(query)
                state.mode = 'team'

    screen.fill((200, 200, 200))
    logo_rect = logo.get_rect(center=(WIDTH/2, 170))
    screen.blit(logo, logo_rect)

    text_surface = font_medium.render("Mode:", True, (0, 0, 0))
    text_rect = text_surface.get_rect(center=(WIDTH/2, 390))
    screen.blit(text_surface, text_rect)

    draw_button(ffa_button, "FFA", font_medium, mouse_pos, (0, 95, 187), (0, 125, 222), (0, 0, 0))
    draw_button(team_button, "Team", font_medium, mouse_pos, (0, 95, 187), (0, 125, 222), (0, 0, 0))

def power(state):
    mouse_pos = pygame.mouse.get_pos()

    con_button = pygame.Rect(WIDTH - 220, HEIGHT - 70, 200, 50)
    prev_button = pygame.Rect(20, 400+20, 60, 50)
    next_button = pygame.Rect(WIDTH-80, 400+20, 60, 50)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            state.running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if con_button.collidepoint(event.pos):
                query = f"SELECT mode FROM game;"
                cursor.execute(query)
                val = cursor.fetchone()[0]
                if val in ('ffa', 'team', 'choose'):
                    state.mode = val
                    state.frame = 'wait'
                    query = f"UPDATE status SET state = 'j' WHERE BINARY user = '{state.user}';"
                    cursor.execute(query)
                elif val == 'off':
                    state.frame = 'choose'
                    state.host = True
                    query = f"UPDATE game SET mode = 'choose';"
                    cursor.execute(query)
            elif next_button.collidepoint(event.pos):
                state.choosing = min(4, state.choosing+1)
            elif prev_button.collidepoint(event.pos):
                state.choosing = max(0, state.choosing-1)
            elif 421 < mouse_pos[1] < 471:
                if 90 < mouse_pos[0] < 290:
                    state.chosen = Data.powernames[3*state.choosing]
                if 300 < mouse_pos[0] < 500:
                    state.chosen = Data.powernames[3*state.choosing+1]
                if 510 < mouse_pos[0] < 710:
                    state.chosen = Data.powernames[3*state.choosing+2]
           
    screen.fill((200, 200, 200))
    logo_rect = logo.get_rect(center=(WIDTH/2, 170))
    screen.blit(logo, logo_rect)

    text_surface = font_medium.render("Power:", True, (0, 0, 0))
    text_rect = text_surface.get_rect(center=(WIDTH/2, 360))
    screen.blit(text_surface, text_rect)

    if state.choosing != 0:
        draw_button(prev_button, "<", font_medium, mouse_pos, (0, 95, 187), (0, 125, 222), (0, 0, 0))
    else:
        draw_button(prev_button, "<", font_medium, mouse_pos, (120, 120, 120), (100, 100, 100), (0, 0, 0))
        
    if state.choosing != 4:
        draw_button(next_button, ">", font_medium, mouse_pos, (0, 95, 187), (0, 125, 222), (0, 0, 0))
    else:
        draw_button(next_button, ">", font_medium, mouse_pos, (120, 120, 120), (100, 100, 100), (0, 0, 0))
    
    if state.chosen == Data.powernames[3*state.choosing]:
        pygame.draw.rect(screen,(0, 95, 187), (80+10, 421, 200, 50))
    else:
        pygame.draw.rect(screen,(120, 120, 120), (80+10, 421, 200, 50))
    text_surf = font_small.render(Data.powernames[3*state.choosing], True, (0, 0, 0))
    text_rect = text_surf.get_rect(center=(190, 446))
    screen.blit(text_surf, text_rect)

    if state.chosen == Data.powernames[3*state.choosing+1]:
        pygame.draw.rect(screen,(0, 95, 187), (80+20+200, 421, 200, 50))
    else:
        pygame.draw.rect(screen,(120, 120, 120), (80+20+200, 421, 200, 50))
    text_surf = font_small.render(Data.powernames[3*state.choosing+1], True, (0, 0, 0))
    text_rect = text_surf.get_rect(center=(400, 446))
    screen.blit(text_surf, text_rect)

    if state.chosen == Data.powernames[3*state.choosing+2]:
        pygame.draw.rect(screen,(0, 95, 187), (80+30+200+200, 421, 200, 50))
    else:
        pygame.draw.rect(screen,(120, 120, 120), (80+30+400, 421, 200, 50))
    text_surf = font_small.render(Data.powernames[3*state.choosing+2], True, (0, 0, 0))
    text_rect = text_surf.get_rect(center=(610, 446))
    screen.blit(text_surf, text_rect)
        
    draw_button(con_button, "Continue", font_medium, mouse_pos, (0, 95, 187), (0, 125, 222), (0, 0, 0))

def end(state):
    mouse_pos = pygame.mouse.get_pos()

    home_button = pygame.Rect(20, HEIGHT - 70, 200, 50)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            state.running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if home_button.collidepoint(event.pos):
                state.frame = 'home'
                query = f"SELECT mode FROM game;"
                cursor.execute(query)
                val = cursor.fetchone()[0]
                if 'play' in val:
                    query = f"UPDATE game SET mode = 'off';"
                    cursor.execute(query)
                    state.mode = 'off'
                    
                state.killcount = 0
                state.place = 0
                state.message = ''
                state.changecolor = False
           

    screen.fill((200, 200, 200))
    logo_rect = logo.get_rect(center=(WIDTH/2, 170))
    screen.blit(logo, logo_rect)

    text_surf = font_small.render(state.message, True, (0, 0, 0))
    text_rect = text_surf.get_rect(center=(400, 370))
    screen.blit(text_surf, text_rect)

    text_surf = font_small.render(f'Kills: {state.killcount}', True, (0, 0, 0))
    text_rect = text_surf.get_rect(center=(400-150, 446))
    screen.blit(text_surf, text_rect)

    text_surf = font_small.render(f'Place: {state.place}', True, (0, 0, 0))
    text_rect = text_surf.get_rect(center=(400+150, 446))
    screen.blit(text_surf, text_rect)

    draw_button(home_button, "Home", font_medium, mouse_pos, (0, 95, 187), (0, 125, 222), (0, 0, 0))

def reset(state):
    query = f"UPDATE stats SET games = games + 1 WHERE BINARY user = '{state.user}';"
    cursor.execute(query)
    if state.place == 1:
        query = f"UPDATE stats SET won = won + 1 WHERE BINARY user = '{state.user}';"
        cursor.execute(query)
    if state.place <= 3:
        query = f"UPDATE stats SET topthree = topthree + 1 WHERE BINARY user = '{state.user}';"
        cursor.execute(query)
    query = f"UPDATE stats SET kills = kills + {state.killcount} WHERE BINARY user = '{state.user}';"
    cursor.execute(query)
    query = f"UPDATE stats SET maxkills = GREATEST(maxkills, {state.killcount}) WHERE BINARY user = '{state.user}';"
    cursor.execute(query)
    
    state.host = False
    state.mode = 'off'
    state.lasttime = 0
    state.choosing = 0
    state.power = ''
    state.health = 100
    state.x = 0
    state.y = 0
    state.angle = 0
    state.bullets = []
    state.lastbullet = -1
    state.bidval = 0
    state.enemies = {}

    query = f"UPDATE status SET state = 'a' WHERE BINARY user = '{state.user}';"
    cursor.execute(query)

def collide(state):
    for player in state.enemies:
        dat = state.enemies[player]
        for bullet in dat[2]:
            if math.dist((state.x, state.y), (bullet['x'], bullet['y'])) < bullet['type']+15 and state.power != 'shield':
                state.health -= bullet['damage']
                if state.health <= 0:
                    state.frame = 'end'
                    state.place = len(state.enemies)+1
                    state.message = f'You were killed by {dat[5]}'
                    message = {
                        'type': 'death',
                        'user': state.user,
                        'shooter': player
                    }
                    reset(state)
                    sock.sendto(json.dumps(message).encode('utf-8'), (IP, PORT))
                return True, bullet['bid'], player
    return False, 0, 0

def game(state):
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            state.running = False
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_f, pygame.K_SPACE) and state.power == '' and time.time() - state.lasttime > Data.powerdata[Data.powermap[state.chosen]][1]:
                if state.chosen != 'Teleport':
                    state.power = Data.powermap[state.chosen]
                    state.lasttime = time.time()
                    if state.power == 'random':
                        options = ["Speed", "Sniper", "Invisibility", "Rapid Fire", "Homing Shots", "Regeneration", "Blast", "Shield", "Shotgun",
                                   "Backshots", "Dual Fire", "Surge Shot"]
                        state.power = Data.powermap[random.choice(options)]
                    if state.power == 'blast':
                        fire_bullet()
                        state.power = ''
                        state.lasttime = time.time()
                elif -1000 < state.x + mouse_pos[0]-400 < 1000 and -1000 < state.y + mouse_pos[1]-300 < 1000:
                    state.power = Data.powermap[state.chosen]
                    state.lasttime = time.time()        

    keys = pygame.key.get_pressed()
    dx = 0
    dy = 0
    wait = 0.5
    speed = 1.5
    if state.power == 'speed':
        speed = 3.5
    elif state.power == 'dash':
        speed = 15
    elif state.power == 'regen':
        state.health = min(state.health + 0.25, 100)
    elif state.power == 'rapid fire':
        wait = 0.15
    elif state.power == 'sniper':
        wait = 0.9
    elif state.power == 'teleport':
        if -1000 < state.x + mouse_pos[0]-400 < 1000 and -1000 < state.y + mouse_pos[1]-300 < 1000:
            state.x += mouse_pos[0]-400
            state.y += mouse_pos[1]-300
        state.power = ''
        state.lasttime = time.time()

    if time.time() - state.starttime > 3:
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1

        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071
    
        state.x = max(-1000, min(state.x + dx * speed, 1000))
        state.y = max(-1000, min(state.y + dy * speed, 1000))
           
    screen.fill((170, 170, 170))
    draw_grid(2000, 2000)
    state.angle = math.atan2(mouse_pos[1]-300, mouse_pos[0]-400)
    update_bullets()
    draw_bullets()
    draw_enemy_bullets()

    for player in state.enemies:
        dat = state.enemies[player]
        if dat[4] != 'invis':
            if dat[4] == 'shield':
                glow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                draw_shield_glow(glow_surface, dat[0][0], dat[0][1], 12, dat[3][:3], layers=10)
                screen.blit(glow_surface, (0, 0))
            draw_player(dat[5], dat[3], dat[0][0], dat[0][1], dat[1], dat[6])
        

    if state.power == 'shield':
        glow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        draw_shield_glow(glow_surface, state.x, state.y, 12, state.pcolor[:3], layers=10)
        screen.blit(glow_surface, (0, 0))
            
    draw_player(state.name, state.pcolor, state.x, state.y, state.angle, state.health)
    
    draw_minimap(2000, 2000)

    mouse_buttons = pygame.mouse.get_pressed()
    if mouse_buttons[0] and time.time() > state.lastbullet+wait and time.time() - state.starttime > 3:
        fire_bullet()
        state.lastbullet = time.time()
        
    val = Data.powerdata[Data.powermap[state.chosen]][0]
    if state.power == '':
        pygame.draw.rect(screen, state.pcolor, (180, 562, 440*min(1, (time.time() - state.lasttime)/Data.powerdata[Data.powermap[state.chosen]][1]), 20), border_radius=3)
    else:
        pygame.draw.rect(screen, state.pcolor, (180, 562, 440*max(0, (val+state.lasttime-time.time())/val), 20), border_radius=3)

    if val+state.lasttime-time.time() < 0 and state.power != '':
        state.power = ''
        state.lasttime = time.time()

    
    pygame.draw.rect(screen,(0, 0, 0), (180, 562, 440, 20), 1, border_radius=3)
    if state.power == '':
        if time.time() - state.lasttime > Data.powerdata[Data.powermap[state.chosen]][1]:
            stuff = 'Superpower ready. Press F or SPACE to activate.'
        else:
            stuff = f'Superpower recharging...'
    else:
        stuff = 'Superpower active.'
    text_surface = font_ultramini.render(stuff, True, (0, 0, 0))
    text_rect = text_surface.get_rect(center=(400, 570.5))
    screen.blit(text_surface, text_rect)
    send(state)
    hitcheck = collide(state)
    if hitcheck[0] and time.time() - state.starttime > 3:
        message = {
            'type': 'hit',
            'shooter': hitcheck[2],
            'bid': hitcheck[1]
        }
        sock.sendto(json.dumps(message).encode('utf-8'), (IP, PORT))

    if len(state.enemies) == 0 and time.time() - state.starttime > 3:
        message = {
            'type': 'death',
            'user': state.user,
            'shooter': None
        }
        sock.sendto(json.dumps(message).encode('utf-8'), (IP, PORT))
        state.message = 'You won!'
        state.place = 1
        state.frame = 'end'
        reset(state)

    if time.time() - state.starttime < 3:
        text_surf = font_large.render(str(3-int(time.time() - state.starttime)), True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=(400, 300))
        screen.blit(text_surf, text_rect)
        

threading.Thread(target=listening, args=(state,), daemon=True).start()

while state.running:
    if state.frame == "login":
        login(state)
    elif state.frame == 'logging':
        logging('old', state)
    elif state.frame == 'newuser':
        logging('new', state)
    elif state.frame == 'home':
        home(state)
    elif state.frame == 'stats':
        stats(state)
    elif state.frame == 'leader':
        leader(state)
    elif state.frame == 'wait':
        waiting(state)
    elif state.frame == 'power':
        power(state)
    elif state.frame == 'choose':
        mode(state)
    elif state.frame == 'end':
        end(state)
    elif state.frame == 'game':
        game(state)
        

    pygame.display.flip()
    clock.tick(FPS)


if state.user is not None:
    query = f"UPDATE status SET state = 'i' WHERE BINARY user = '{state.user}';"
    cursor.execute(query)
    
query = f"SELECT count(*) FROM status WHERE state in ('a', 'j');"
cursor.execute(query)
active = cursor.fetchone()[0]

if active == 0:
    query = f"UPDATE game SET mode = 'off';"
    cursor.execute(query)

message = {
    'type': 'death',
    'user': state.user,
    'shooter': None
}
sock.sendto(json.dumps(message).encode('utf-8'), (IP, PORT))
    
pygame.quit()
cnx.close()
