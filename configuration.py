import pygame
from random import randint as random

import os
import json
from win32api import GetSystemMetrics as win

pygame.init()

folder_root = os.path.dirname(os.path.abspath(__file__))

#Группы кнопок которые в контесте приводят к одному результату
key = {
    "LEFT": [pygame.K_LEFT, pygame.K_a],
    "RIGHT": [pygame.K_RIGHT, pygame.K_d],
    "UP": [pygame.K_UP, pygame.K_w],
    "DOWN": [pygame.K_DOWN, pygame.K_s]
}

#Парсим все картинки из папки в словарь под их имена
def get_image(way):
    way = f"{folder_root}/material/graphix/" + way
    with os.scandir(way) as listOfEntries:
        image_list = {}
        for entry in listOfEntries:
            if entry.is_file():
                image = pygame.image.load(f"{way}/{entry.name}")
                image.set_colorkey((255, 255, 255))
                image_list[entry.name.split(".")[0]] = image
        return image_list


icon = pygame.image.load(f"{folder_root}/material/icon.ico")
#pygame.mixer.music.load(f"{folder_root}/material/sound/Steel-arms-voiced.ogg")

#Вытаскиваем звук из каталога. #TO DO
with open(f"{folder_root}/material/sound/Steel-arms-voiced.ogg", "rb") as file:
    light_hitting_sound = pygame.mixer.Sound(file.read())

#light_hitting_sound = pygame.mixer.Sound(f"{folder_root}/material/sound/Steel-arms-voiced.ogg")

#Загружаем папку fone
fone_image = get_image("fone")

#Загружаем папку effects
attack_image = get_image(f"effects/attack")

#Загружаем папку weapon
katana_image = get_image(f"weapon/katana")

#Загружаем папку person
cricle_image = get_image(f"person/cricle")

#Загружаем звуки
#soundtrack = pg.mixer.music.load('Beethoven.ogg')

#Возврощает рандомный знак
def random_pole():
    if random(0, 1) == 1:
        return 1
    else:
        return -1


#Перебрасываем вектор если перешли границу
def check_vector(arg):
    if int(arg) < 1:
        arg += 8
    elif int(arg) > 8:
        arg -= 8
    return arg


theme = "dark"

#Получаем цвета из заданной темы
with open(f"{folder_root}/theme/{theme}-theme.json", "r") as file:
    color = json.loads(file.read())["color"]

#Глобальные состояния
time = True

#Константы и системная информация
FPS = 30

window_dimensions = (600, 400)
