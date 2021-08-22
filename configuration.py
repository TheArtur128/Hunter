import pygame
from random import randint as random

import os
import json
from win32api import GetSystemMetrics as win


#Парсим все картинки из папки в словарь под их имена
def get_image(way):
    way = "material/graphix/" + way
    with os.scandir(way) as listOfEntries:
        image_list = {}
        for entry in listOfEntries:
            if entry.is_file():
                image = pygame.image.load(f"{way}/{entry.name}")
                image.set_colorkey((255, 255, 255))
                image_list[entry.name.split(".")[0]] = image
        return image_list


#Загружаем материалы
cricle_image = get_image("cricle")
fone_image = get_image("fone")
icon = pygame.image.load("material/icon.ico")


#Возврощает рандомный знак
def random_pole():
    if random(0, 1) == 1:
        return 1
    else:
        return -1


theme = "dark"

#Получаем цвета из заданной темы
with open(f"theme\{theme}-theme.json", "r") as file:
    color = json.loads(file.read())["color"]

FPS = 30

#Глобальные состояния
time = True

window_dimensions = (600, 400)
