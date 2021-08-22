from configuration import *

pygame.init()

#Хранилище всех сущностей для будущего отрисосвывания
memory = []

#Создаём прлиложение
app = pygame.display.set_mode(window_dimensions)
pygame.display.set_icon(icon)
pygame.display.set_caption("Lonely Hunter")
clock = pygame.time.Clock()

#Абстрактный класс всего что позволяет отрисовать pygame
class Primitive:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y

    def __repr__(self):
        return f"#{self.name}"


#Персонажи
class Hunter(Primitive):
    def __init__(self, name, x, y, vector=1):
        self.__speed = 5
        super().__init__(name, x, y)
        self.__size = 81
        self.vector = vector
        self.movement = {
            "left": [False, random_pole()],
            "right": [False, random_pole()],
            "up": [False, random_pole()],
            "down": [False, random_pole()]
        }
        memory.append(self)

    #Красиво упакованные данные для функции pygame'a для прорисовки
    def drawing_data(self):
        return [cricle_image[str(self.vector)], (self.x, self.y)]

    @property
    def speed(self): return self.__speed
    @property
    def size(self): return self.__size

#Сущность которой мы можем управлять
Hero = Hunter("Arthur", 200, 200)

#Главный цикл
world_is_life = True
while world_is_life:
    clock.tick(FPS)

    for action in pygame.event.get():
        if action.type == pygame.QUIT:
            world_is_life = False

        if action.type == pygame.KEYDOWN:
            if action.key == pygame.K_LEFT: Hero.movement["left"] = [True, random_pole()]
            if action.key == pygame.K_RIGHT: Hero.movement["right"] = [True, random_pole()]
            if action.key == pygame.K_UP: Hero.movement["up"] = [True, random_pole()]
            if action.key == pygame.K_DOWN: Hero.movement["down"] = [True, random_pole()]

        if action.type == pygame.KEYUP:
            if action.key == pygame.K_LEFT: Hero.movement["left"] = [False, random_pole()]
            if action.key == pygame.K_RIGHT: Hero.movement["right"] = [False, random_pole()]
            if action.key == pygame.K_UP: Hero.movement["up"] = [False, random_pole()]
            if action.key == pygame.K_DOWN: Hero.movement["down"] = [False, random_pole()]


    #Если были нажаты две смежные кнопки то ставим нужный вектор и запрещаем его изминять
    if Hero.movement["left"][0] and Hero.movement["up"][0]:
        Hero.vector = 8
        vector_ban = True
    elif Hero.movement["left"][0] and Hero.movement["down"][0]:
        Hero.vector = 6
        vector_ban = True
    elif Hero.movement["right"][0] and Hero.movement["up"][0]:
        Hero.vector = 2
        vector_ban = True
    elif Hero.movement["right"][0] and Hero.movement["down"][0]:
        Hero.vector = 4
        vector_ban = True
    else:
        vector_ban = False


    #Изминение х координаты
    if Hero.movement["left"][0]:
        if Hero.x > 0:
            Hero.x -= Hero.speed
        if not vector_ban:
            if Hero.vector == 3:
                Hero.vector += Hero.movement["left"][1]
            elif Hero.vector in [8, 1, 2]:
                Hero.vector -= 1
            elif Hero.vector in [4, 5, 6]:
                Hero.vector += 1

    elif Hero.movement["right"][0]:
        if Hero.x + Hero.size < window_dimensions[0]:
            Hero.x += Hero.speed
        if not vector_ban:
            if Hero.vector == 7:
                Hero.vector += Hero.movement["right"][1]
            elif Hero.vector in [4, 5, 6]:
                Hero.vector -= 1
            elif Hero.vector in [8, 1, 2]:
                Hero.vector += 1


    #Изминение y координаты
    if Hero.movement["up"][0]:
        if Hero.y > 0:
            Hero.y -= Hero.speed
        if not vector_ban:
            if Hero.vector == 5:
                Hero.vector += Hero.movement["up"][1]
            elif Hero.vector in [2, 3, 4]:
                Hero.vector -= 1
            elif Hero.vector in [6, 7, 8]:
                Hero.vector += 1

    elif Hero.movement["down"][0]:
        if Hero.y + Hero.size < window_dimensions[1]:
            Hero.y += Hero.speed
        if not vector_ban:
            if Hero.vector == 1:
                Hero.vector += Hero.movement["down"][1]
            elif Hero.vector in [2, 3, 4]:
                Hero.vector += 1
            elif Hero.vector in [6, 7, 8]:
                Hero.vector -= 1


    #Перебрасываем вектор если перешли границу
    if Hero.vector < 1:
        Hero.vector = 8
    elif Hero.vector > 8:
        Hero.vector = 1


    #Рисуем
    app.blit(fone_image["one"], (0, 0))

    #Прорисовываем все обьекты в хранилище
    for item in memory:
        app.blit(*item.drawing_data())

    pygame.display.update()
