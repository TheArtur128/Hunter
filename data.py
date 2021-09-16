import json
import os

import pygame
from random import randint as random

pygame.init()

folder_root = os.path.dirname(os.path.abspath(__file__))


#Парсим все файлы из папки в словарь под их имена
def get_files(directory, characteristic=False):
    directory = f"{folder_root}/material/" + directory
    with os.scandir(directory) as listOfEntries:
        files = {}
        for entry in listOfEntries:
            if entry.is_file():
                #Работа для разных форматов
                if entry.name.split(".")[1] in ["png", "img", "ico"]:
                    if not characteristic:
                        file = pygame.image.load(f"{directory}/{entry.name}")
                        file.set_colorkey((255, 255, 255))
                    #test
                    elif characteristic:
                        file_inside = Image.open(f"{directory}/{entry.name}")
                        file = {
                            "original": file_inside,
                            "size": file_inside.size
                        }

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


def round(vaule, number_after_point=1):
    if isinstance(vaule, float):
        return float(str(int(vaule))+ "." + str(vaule).split(".")[1][:number_after_point])


#Загружаем глобальные файлы
soundtrack = pygame.mixer.music.load(f"{folder_root}/material/general/soundtracks/theme.mp3")
icon = pygame.image.load(f"{folder_root}\material\general\graphix\icon.ico")

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
exit = False
debug_mode = False

#Константы и системная информация
with open(f"{folder_root}/configuration.json", "r") as file:
    j_soup = json.loads(file.read())
    color = j_soup["color"]
    settings = j_soup["settings"]

FPS = 30

time_to_exit = FPS * settings["seconds_to_exit"]

app_win = settings["window"]
tithe_win = [app_win[0]//10, app_win[1]//10]

camera_walls = {
    "x": {
        "left": tithe_win[0]*settings["factor_of_camera_walls"],
        "right": app_win[0] - tithe_win[0]*settings["factor_of_camera_walls"]
    },

    "y": {
        "up": tithe_win[1]*settings["factor_of_camera_walls"],
        "down": app_win[1] - tithe_win[1]*settings["factor_of_camera_walls"]
    }
}
