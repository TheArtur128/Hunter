import json
import os

import pygame
from random import randint as random

pygame.init()

folder_root = os.path.dirname(os.path.abspath(__file__))


#Парсим все файлы из папки в словарь под их имена
def get_files(directory):
    directory = f"{folder_root}/material/" + directory
    with os.scandir(directory) as listOfEntries:
        files = {}
        for entry in listOfEntries:
            if entry.is_file():
                file = pygame.image.load(f"{directory}/{entry.name}")
                #Проверки для нужных форматов
                if entry.name.split(".")[1] in ["png", "img", "ico"]:
                    file.set_colorkey((255, 255, 255))
                files[entry.name.split(".")[0]] = file
        if len(files) == 1:
            files = files[list(files.keys())[0]]
        return files

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


#Загружаем глобальные файлы
soundtrack = pygame.mixer.music.load(f"{folder_root}/material/general/soundtracks/theme.mp3")
icon = pygame.image.load(f"{folder_root}\material\general\graphix\icon.ico")

#Получаем цвета из заданной темы
theme = "dark"
with open(f"{folder_root}/theme/{theme}-theme.json", "r") as file:
    color = json.loads(file.read())["color"]

#Группы кнопок которые в контесте приводят к одному результату
key = {
    "moving player": {
        "LEFT": [pygame.K_LEFT, pygame.K_a],
        "RIGHT": [pygame.K_RIGHT, pygame.K_d],
        "UP": [pygame.K_UP, pygame.K_w],
        "DOWN": [pygame.K_DOWN, pygame.K_s]
    }
}

#Глобальные состояния
game = True
debug_mode = True
time = True

#Константы и системная информация
FPS = 30

app_win = (640, 430)
tithe_win = [app_win[0]//10, app_win[1]//10]

camera_walls = {
    "x": {"left": tithe_win[0]*3, "right": app_win[0] - tithe_win[0]*3},
    "y": {"up": tithe_win[1]*3, "down": app_win[1] - tithe_win[1]*3}
}
