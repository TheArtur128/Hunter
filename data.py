import json
import os

import pygame
from random import choice
from random import randint as random

pygame.init()

folder_root = os.path.dirname(os.path.abspath(__file__))


def get_image(directory):
    file = pygame.image.load(f"{folder_root}/material/{directory}")
    file.set_colorkey((255, 255, 255))
    return file


#Парсит все в словарь
def get_images(original_directory):
    directory = f"{folder_root}/material/{original_directory}"
    with os.scandir(directory) as listOfEntries:
        files = {}
        for entry in listOfEntries:
            if entry.is_file():
                files[entry.name.split(".")[0]] = get_image(f"{original_directory}/{entry.name}")

        return files


def generation_forms(surface):
    surfaces = {}
    for i in range(8):
        surfaces[str(i+1)] = pygame.transform.rotate(surface, -45*i)

    return surfaces


def complement_forms(surfaces):
    surfaces["4"] = pygame.transform.flip(surfaces["2"], False, True)
    surfaces["5"] = pygame.transform.flip(surfaces["1"], True, True)
    surfaces["6"] = pygame.transform.flip(surfaces["2"], True, True)
    surfaces["7"] = pygame.transform.flip(surfaces["3"], True, True)
    surfaces["8"] = pygame.transform.flip(surfaces["2"], True, False)
    return surfaces


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
