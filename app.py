from configuration import *

#Хранилище всех сущностей для будущего отрисосвывания
memory = []

#Абстрактный класс всего что позволяет отрисовать pygame
class Primitive:
    def __init__(self, name, x, y, vector=1):
        memory.append(self)
        self.name = name
        if debug_mode: print(f"{self} initialized")
        self.x = x
        self.y = y
        self.vector = vector
        self.img = self.__class__.img

    #Красиво упакованные данные для функции pygame'a для прорисовки
    def drawing_data(self):
        return [self.img[str(self.vector)], (self.x, self.y)]

    def __repr__(self):
        return f"<{self.name}>"

    def dying(self):
        if debug_mode: print(f"{self} died")
        self.__dict__ = {}
        memory.remove(self)


#Абстрактный класс всех оружий
class Weapon(Primitive):
    def __init__(self, name, damage=10, strength=5, speed=FPS, x=0, y=0, vector=1, master=None):
        super().__init__(name, x, y, vector)
        #Атрибуты описывающие оружие непосредственно
        self.damage = damage
        self.strength = strength
        self.speed = speed
        #Ссылка на персонажа держущего оружие
        self.master = master
        #Атрибуты действия
        self.action = [self.__class__.speed, 0, 0]
        #Штраф при расположении под углом
        self.coordinates = self.default_coordinates()

    def __update_coordinates(self):
        if self.master is not None:
            self.vector = self.master.vector + self.action[1]
            self.vector = check_vector(self.vector)
            self.x = self.master.x + self.coordinates[self.vector-1][0]
            self.y = self.master.y + self.coordinates[self.vector-1][1]

        if self.strength <= 0:
            self.dying()

    def dying(self):
        self.master.weapon = None
        super().dying()

    @staticmethod
    def default_coordinates():
        '''Штраф распоожения для векторов. Первый индекс штрафа
        равняеться положению 1 (up), последний (7) равен вектору "left-up" (8)'''
        return [[81, 8], [38, 48], [-8, 81], [-25, 35], [-5, 8], [-5, -27], [8, -5], [45, -15]]

    def verification(self):
        self.__update_coordinates()


class Katana(Weapon):
    img = get_image(f"weapon/katana/graphix")
    waft = pygame.mixer.Sound(f"{folder_root}/material/weapon/katana/sound/waft-weapon.ogg")
    speed = FPS // 10
    def __init__(self, name="katana", strength=10, damage=10, speed=speed, x=0, y=0, vector=1, master=None):
        super().__init__(name, damage=damage, strength=strength, speed=speed, x=x, y=y, vector=vector, master=master)


#Персонажи как класс
class Hunter(Primitive):
    img = get_image(f"person/red-circle")
    def __init__(self, name, x, y, health=100, vector=1, weapon=Katana):
        super().__init__(name, x, y, vector)
        self.health = health
        self.speed = 7
        self.__size = 81
        self.action = "quiet"
        self.movement = {
            "left": [False, random_pole()],
            "right": [False, random_pole()],
            "up": [False, random_pole()],
            "down": [False, random_pole()]
        }
        self.weapon = weapon(master=self)

    def __attack(self):
        if self.weapon is not None:
            #Уменьшаем счётчик до момента удара
            self.weapon.action[0] -= 1
            if self.weapon.action[0] <= 0:
                self.weapon.action[0] = self.weapon.__class__.speed #Обновляем счётчик до следуещего удара
                self.weapon.action[1] -= 1 #перемещаем оружие
                self.weapon.action[2] += 1 #Устанавливаем точное кол. итераций

                if self.weapon.action[2] == 2:
                    for item in memory:
                        if item.__class__ in Hunter.__subclasses__() or item.__class__ == Hunter and item != self:
                            if self.x < item.x:
                                item.health -= self.weapon.damage
                                self.weapon.strength -= 1
                                if debug_mode:
                                    print(f"{self} hit {item}! {item} have {item.health} hp")

                #Завершаем удар
                if self.weapon.action[2] >= 4:
                    self.action = "quiet"
                    #Ставим атрибуты на свои места
                    self.weapon.action[1] = 0
                    self.weapon.action[2] = 0
                    self.weapon.coordinates = self.weapon.default_coordinates()

            self.weapon.vector = check_vector(self.weapon.vector)
        else:
            self.action = "quiet"

    def check_motion(self):
        #Если были нажаты две смежные кнопки
        if self.movement["left"][0] and self.movement["up"][0]:
            self.vector = 8
            vector_ban = True
        elif self.movement["left"][0] and self.movement["down"][0]:
            self.vector = 6
            vector_ban = True
        elif self.movement["right"][0] and self.movement["up"][0]:
            self.vector = 2
            vector_ban = True
        elif self.movement["right"][0] and self.movement["down"][0]:
            self.vector = 4
            vector_ban = True
        else:
            vector_ban = False

        #Изминение х координаты
        if self.movement["left"][0]:
            if self.x > 0:
                self.x -= self.speed
            if not vector_ban:
                if self.vector == 3:
                    self.vector += self.movement["left"][1]
                elif self.vector in [8, 1, 2]:
                    self.vector -= 1
                elif self.vector in [4, 5, 6]:
                    self.vector += 1

        elif self.movement["right"][0]:
            if self.x + self.size < app_win[0]:
                self.x += self.speed
            if not vector_ban:
                if self.vector == 7:
                    self.vector += self.movement["right"][1]
                elif self.vector in [4, 5, 6]:
                    self.vector -= 1
                elif self.vector in [8, 1, 2]:
                    self.vector += 1

        #Изминение y координаты
        if self.movement["up"][0]:
            if self.y > 0:
                self.y -= self.speed
            if not vector_ban:
                if self.vector == 5:
                    self.vector += self.movement["up"][1]
                elif self.vector in [2, 3, 4]:
                    self.vector -= 1
                elif self.vector in [6, 7, 8]:
                    self.vector += 1

        elif self.movement["down"][0]:
            if self.y + self.size < app_win[1]:
                self.y += self.speed
            if not vector_ban:
                if self.vector == 1:
                    self.vector += self.movement["down"][1]
                elif self.vector in [2, 3, 4]:
                    self.vector += 1
                elif self.vector in [6, 7, 8]:
                    self.vector -= 1

        self.vector = check_vector(self.vector)

    def verification(self):
        #Вызываем функию состояния
        if self.action == "attack": self.__attack()

        if self.__class__ == Hunter: self.check_motion()

        #Подгоняем хитбокс под новые координаты
        self.hitbox = []
        for i in range(360):
            vec = pygame.math.Vector2(0, -40).rotate(i)
            self.hitbox.append([int(self.x+self.size//2+vec.x), int(self.y+self.size//2+vec.y)])

        if self.health <= 0:
            self.dying()

    def dying(self):
        if self.weapon is not None:
            self.weapon.master = None
        super().dying()

    @property
    def size(self): return self.__size


class Player(Hunter):
    img = get_image(f"person/blue-circle")
    def verification(self):

        self.check_motion()

        #Работаем с x координатой
        if self.x + self.size > camera_walls["x"]["right"]:
            for item in memory:
                item.x -= self.speed

        elif self.x < camera_walls["x"]["left"]:
            for item in memory:
                item.x += self.speed

        #Работаем с y координатой
        if self.y < camera_walls["y"]["up"]:
            for item in memory:
                item.y += self.speed

        elif self.y > camera_walls["y"]["down"] - self.size:
            for item in memory:
                item.y -= self.speed

        super().verification()


#Тестовый микрочелик отличающийся от своего предка только постоянными атаками
class Opponent(Hunter):
    img = get_image(f"person/red-circle")
    def verification(self):
        self.action = "attack"
        super().verification()


#Создаём прлиложение
app = pygame.display.set_mode(app_win)
pygame.display.set_icon(icon)
pygame.display.set_caption("Lonely Hunter")
pygame.mixer.music.play(loops=-1)
pygame.mixer.music.set_volume(0.08)
clock = pygame.time.Clock()

#Сущность которой мы можем управлять
Hero = Player("Main Hero", app_win[0]//2 - 40, app_win[1]//2 - 40)

#Тестовая сущность
Opponent("Red Hunter", 525, 325)

if debug_mode: print(f"memory: {memory}")

#Главный цикл
while game and __name__ == '__main__':
    clock.tick(FPS)

    for action in pygame.event.get():
        if action.type == pygame.QUIT:
            game = False

        if Hero in memory:
            if action.type == pygame.MOUSEBUTTONDOWN:
                if action.button == 1:
                    Hero.action = "attack"

            if action.type == pygame.KEYDOWN:
                if action.key == pygame.K_x:
                    Hero.action = "attack"

                if action.key in key["LEFT"]: Hero.movement["left"] = [True, random_pole()]
                if action.key in key["RIGHT"]: Hero.movement["right"] = [True, random_pole()]
                if action.key in key["UP"]: Hero.movement["up"] = [True, random_pole()]
                if action.key in key["DOWN"]: Hero.movement["down"] = [True, random_pole()]

            if action.type == pygame.KEYUP:
                if action.key in key["LEFT"]: Hero.movement["left"] = [False, random_pole()]
                if action.key in key["RIGHT"]: Hero.movement["right"] = [False, random_pole()]
                if action.key in key["UP"]: Hero.movement["up"] = [False, random_pole()]
                if action.key in key["DOWN"]: Hero.movement["down"] = [False, random_pole()]


    app.fill(((28, 147, 64)))#statics_image["glade"]

    if debug_mode:
        for pos_y in ("up", "down"):
            pygame.draw.line(app, color["debug_mode"],
                [camera_walls["x"]["left"], camera_walls["y"][pos_y]],
                [camera_walls["x"]["right"], camera_walls["y"][pos_y]]
            )

        for pos_x in ("left", "right"):
            pygame.draw.line(app, color["debug_mode"],
                [camera_walls["x"][pos_x], camera_walls["y"]["up"]],
                [camera_walls["x"][pos_x], camera_walls["y"]["down"]]
            )

    #Работа с хранилищем
    for item in memory:
        item.verification() #Для каждого обьекта проводим его личную проверку
        if item in memory:
            app.blit(*item.drawing_data()) #Рисуем обькт из упакованных данных
            if debug_mode and item.__class__ in Hunter.__subclasses__():
                for hitbox in item.hitbox:
                    pygame.draw.rect(app, color["debug_mode"], (hitbox[0], hitbox[1], 1, 1))

    pygame.display.update()
