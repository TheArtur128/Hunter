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


def get_files(original_directory, parse_func=get_image):
    '''Парсит все файлы в словарь ключами которых являеться названия этих файлов'''
    directory = f"{folder_root}/material/{original_directory}"
    with os.scandir(directory) as listOfEntries:
        files = {}
        for entry in listOfEntries:
            if entry.is_file():
                files[entry.name.split(".")[0]] = parse_func(f"{original_directory}/{entry.name}")

        return files


def get_catalog(original_directory):
    '''Парсит пути всех обьектов в директории в список'''
    directory = f"{folder_root}/material/{original_directory}"
    with os.scandir(directory) as listOfEntries:
        directoryes = []
        for entry in listOfEntries:
            directoryes.append(f"{original_directory}/{entry.name}")

        return directoryes


def generation_forms(surface):
    surfaces = {}
    for i in range(8):
        surfaces[str(i+1)] = pygame.transform.rotate(surface, -45*i)

    return surfaces


def complement_forms(surfaces):
    surfaces["3"] = pygame.transform.rotate(surfaces["1"], -90)
    surfaces["4"] = pygame.transform.flip(surfaces["2"], False, True)
    surfaces["5"] = pygame.transform.rotate(surfaces["3"], -90)
    surfaces["6"] = pygame.transform.flip(surfaces["2"], True, True)
    surfaces["7"] = pygame.transform.rotate(surfaces["5"], -90)
    surfaces["8"] = pygame.transform.flip(surfaces["2"], True, False)
    return surfaces


def variety_of_forms(surfaces):
    variations = [((True, True), "vertically horizontally"), ((True, False), "horizontally"), ((False, True), "vertically")]
    for item in get_dict_list(surfaces):
        for variation in variations:
            surfaces[f"{item[0]} {variation[1]} reflected"] = pygame.transform.flip(item[1], *variation[0])
    return surfaces


def round(vaule, number_after_point=1):
    if isinstance(vaule, float):
        return float(str(int(vaule))+ "." + str(vaule).split(".")[1][:number_after_point])


def get_dict_list(dict_):
    return [[list(dict_.keys())[i], list(dict_.values())[i]] for i in range(len(dict_))]


def get_family(class_):
    classes = [class_]
    while True:
        free_classes = False
        for our_class in classes:
            for subclass in our_class.__subclasses__():
                if not subclass in classes:
                    classes.append(subclass)
                    free_classes = True

        if not free_classes:
            return classes.copy()


def is_there_attribute(object_, attribute: str):
    try:
        object_.__dict__[attribute]
        return True
    except KeyError:
        return False


def sorting_by_attribute(array: list, attribute: str):
    for object_ in array:
        if not is_there_attribute(object_, attribute):
            array.remove(object_)

    return array


#Группы кнопок которые в контесте приводят к одному результату
key = {
    "player": {
        "ATTACK": [pygame.K_SPACE],
        "LEFT": [pygame.K_LEFT, pygame.K_a],
        "RIGHT": [pygame.K_RIGHT, pygame.K_d],
        "UP": [pygame.K_UP, pygame.K_w],
        "DOWN": [pygame.K_DOWN, pygame.K_s],
        "WEAPON_CHANGE": [pygame.K_TAB, pygame.K_RALT, pygame.K_LALT],
        "DASH": [pygame.K_x],
        "PAUSE": [pygame.K_BACKQUOTE]
    },
    "menu": {
        "AGAIN": [pygame.K_SPACE],
        "ENABLE MINIMAP": [pygame.K_m]
    }
}

with open(f"{folder_root}/material/general/names.json", "r") as file:
    names = json.loads(file.read())

with open(f"{folder_root}/configuration.json", "r") as file:
    j_soup = json.loads(file.read())
    settings = j_soup["settings"]
    files = j_soup["files"]
    color = j_soup["color"]
    

debug_mode = settings["debug mode"]

FPS = 30

time_to_exit = FPS * settings["seconds to exit"]

app_win = settings["window"]

plays_area = [app_win[0]*settings["factor plays area"], app_win[1]*settings["factor plays area"]]

tithe_win = [app_win[0]//10, app_win[1]//10]

camera_area = {
    "width": app_win[0] - tithe_win[0]*settings["factor of camera width"]*2,
    "height": app_win[1] - tithe_win[1]*settings["factor of camera height"]*2
}
