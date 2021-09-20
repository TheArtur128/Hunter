import json
import os

import pygame
from random import randint as random

pygame.init()

folder_root = os.path.dirname(os.path.abspath(__file__))


#Парсим все файлы из папки в словарь под их имена
def get_images(directory):
    directory = f"{folder_root}/material/" + directory
    with os.scandir(directory) as listOfEntries:
        files = {}
        for entry in listOfEntries:
            if entry.is_file():
                file = pygame.image.load(f"{directory}/{entry.name}")
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


def round(vaule, number_after_point=1):
    if isinstance(vaule, float):
        return float(str(int(vaule))+ "." + str(vaule).split(".")[1][:number_after_point])


def presence_in_inheritance(class_, atribut=None):
    classes = [class_]
    while True:
        free_classes = False
        for our_class in classes:
            for subclass in our_class.__subclasses__():
                if not subclass in classes:
                    classes.append(subclass)
                    free_classes = True

        if not free_classes:
            if atribut is not None:
                clear_classes = []
                for class_ in classes:
                    try:
                        class_.__dict__[atribut]
                        clear_classes.append(class_)
                    except KeyError:
                        pass
                return clear_classes

            return classes


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

with open(f"{folder_root}/configuration.json", "r") as file:
    j_soup = json.loads(file.read())
    color = j_soup["color"]
    settings = j_soup["settings"]

#Глобальные состояния
game = True
exit = False
debug_mode = settings["debug_mode"]


FPS = 30

time_to_exit = FPS * settings["seconds_to_exit"]

app_win = settings["window"]

plays_area = [app_win[0]*settings["factor_plays_area"], app_win[1]*settings["factor_plays_area"]]

tithe_win = [app_win[0]//10, app_win[1]//10]

camera_area = {
    "width": app_win[0] - tithe_win[0]*settings["factor_of_camera_width"]*2,
    "height": app_win[1] - tithe_win[1]*settings["factor_of_camera_height"]*2
}
