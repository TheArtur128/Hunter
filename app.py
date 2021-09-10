from configuration import *


#Абстрактный класс всего что позволяет отрисовать pygame
class Primitive:
    #Хранилище всех сущностей для будущего отрисосвывания.
    memory = []

    data_way = "person/blue-circle"

    def __init__(self, name, x, y, health=100):
        Primitive.memory.append(self)
        self.name = name
        if debug_mode: print(f"{self} initialized")
        self.x = x
        self.y = y
        self.health = health
        self.img = self.__class__.img

    def __repr__(self):
        return f"<{self.name}>"

    def dying(self):
        if debug_mode: print(f"{self} died")
        self.__dict__ = {}
        Primitive.memory.remove(self)

#Недвижимые обьекты
class Static(Primitive):
    def __init__(self, name, x, y, health):
        super().__init__(name=name, x=x, y=y, health=health)

    def drawing_data(self):
        return [self.img, (self.x, self.y)]


class Stone(Static):
    img = get_files("statics")


#Движимые обьекты
class Movable(Primitive):
    def __init__(self, name, x, y, health, speed, vector=1):
        super().__init__(name=name, x=x, y=y, health=health)
        self.speed = speed
        '''В игре 8 векторов, первый вектор обозначает 90°,
        последующие уменьшены на 45° от предыдущего'''
        self.vector = vector

    def drawing_data(self):
        return [self.img[str(self.vector)], (self.x, self.y)]


class Weapon(Movable):
    def __init__(self, name, damage=10, health=100, x=0, y=0, vector=1, speed=FPS, master=None):
        super().__init__(name=name, x=x, y=y, health=health, vector=vector, speed=speed)
        #Атрибуты описывающие оружие непосредственно
        self.damage = damage
        #Ссылка на персонажа держущего оружие
        self.master = master
        #Штраф расположении векторов. см документацию метода
        self.coordinates = self.default_coordinates()

    def __update_coordinates(self):
        if self.master is not None:
            try:
                self.vector = self.master.vector + self.action["vector-buffer"]
            except AttributeError:
                self.vector = self.master.vector

            self.vector = check_vector(self.vector)
            self.x = self.master.x + self.coordinates[self.vector][0]
            self.y = self.master.y + self.coordinates[self.vector][1]

        if self.health <= 0:
            self.dying()

    def dying(self):
        self.master.weapon = None
        super().dying()

    @staticmethod
    def default_coordinates():
        return {
            1: [81, 8],
            2: [38, 48],
            3: [-8, 81],
            4: [-25, 35],
            5: [-5, 8],
            6: [-5, -27],
            7: [8, -5],
            8: [45, -15]
            }

    def verification(self):
        self.__update_coordinates()
        self._install_hitbox()


class Katana(Weapon):
    img = get_files(f"weapon/katana/graphix")
    average_speed = FPS // 10
    def __init__(self, name="katana", health=100, damage=10, speed=average_speed, x=0, y=0, vector=1, master=None):
        super().__init__(name, damage=damage, health=health, speed=Katana.average_speed, x=x, y=y, vector=vector, master=master)

    def _install_hitbox(self):
        self.hitbox = []
        if self.vector in (1, 5):
            for i in range(75):
                self.hitbox.append([self.x+2, self.y+i])
        elif self.vector in (2, 6):
            for i in range(54):
                self.hitbox.append([self.x+i, self.y+54-i])
        elif self.vector in (3, 7):
            for i in range(75):
                self.hitbox.append([self.x+i, self.y+2])
        elif self.vector in (4, 8):
            for i in range(54):
                self.hitbox.append([self.x+i, self.y+i])


#Персонажи как класс
class Hunter(Movable):
    img = get_files("person/red-circle")
    def __init__(self, name, x, y, health=100, speed=7, vector=1, weapon=Katana):
        super().__init__(name=name, x=x, y=y, health=health, vector=vector, speed=speed)
        self.__size = 81
        self.action = "quiet"
        self.movement = {
            "left": False,
            "right": False,
            "up": False,
            "down": False
        }
        self.weapon = weapon(master=self)

    def __attack(self):
        if self.weapon is not None:
            #При первой итерации метода создаем атрибуты для работы это-го дейсвия
            try:
                self.weapon.action
            except AttributeError:
                self.weapon.action = {
                    "time-indicator": self.weapon.__class__.average_speed,
                    "vector-buffer": 0, #Складываеться с основным вектором оружия
                    "iterations-done": 0 #Количество прошедших итераций. Нужно для эмуляции покадрового цикла
                }

            #Уменьшаем счётчик до момента удара
            self.weapon.action["time-indicator"] -= 1
            if self.weapon.action["time-indicator"] <= 0:
                self.weapon.action["time-indicator"] = self.weapon.__class__.average_speed
                self.weapon.action["iterations-done"] += 1
                self.weapon.action["vector-buffer"] -= 1

                #Завершаем удар
                if self.weapon.action["iterations-done"] >= 4:
                    self.action = "quiet"
                    self.weapon.coordinates = self.weapon.default_coordinates()
                    del self.weapon.action

                #Проверяем атакавали-ли и в последствии атакуем
                for prey in Primitive.memory:
                    hit = False
                    if not prey in [self, self.weapon]:
                        for weapon_point in self.weapon.hitbox:
                            if weapon_point in prey.hitbox:
                                prey.health -= self.weapon.damage
                                prey.y -= 50#self.weapon.damage * 5
                                self.weapon.health -= 10
                                if debug_mode:
                                    print(f"{self} hit {prey}! {prey} have {prey.health} hp")
                                break

            self.weapon.vector = check_vector(self.weapon.vector)

        else:
            self.action = "quiet"

    def _check_motion(self):
        #Если были нажаты две смежные кнопки
        if self.movement["left"] and self.movement["up"]:
            self.vector = 8
            vector_ban = True
        elif self.movement["left"] and self.movement["down"]:
            self.vector = 6
            vector_ban = True
        elif self.movement["right"] and self.movement["up"]:
            self.vector = 2
            vector_ban = True
        elif self.movement["right"] and self.movement["down"]:
            self.vector = 4
            vector_ban = True
        else:
            vector_ban = False

        #Изминение х координаты
        if self.movement["left"]:
            self.x -= self.speed
            if not vector_ban:
                if self.vector == 3:
                    self.vector += random_pole()
                elif self.vector in [8, 1, 2]:
                    self.vector -= 1
                elif self.vector in [4, 5, 6]:
                    self.vector += 1

        elif self.movement["right"]:
            self.x += self.speed
            if not vector_ban:
                if self.vector == 7:
                    self.vector += random_pole()
                elif self.vector in [4, 5, 6]:
                    self.vector -= 1
                elif self.vector in [8, 1, 2]:
                    self.vector += 1

        #Изминение y координаты
        if self.movement["up"]:
            self.y -= self.speed
            if not vector_ban:
                if self.vector == 5:
                    self.vector += random_pole()
                elif self.vector in [2, 3, 4]:
                    self.vector -= 1
                elif self.vector in [6, 7, 8]:
                    self.vector += 1

        elif self.movement["down"]:
            self.y += self.speed
            if not vector_ban:
                if self.vector == 1:
                    self.vector += random_pole()
                elif self.vector in [2, 3, 4]:
                    self.vector += 1
                elif self.vector in [6, 7, 8]:
                    self.vector -= 1

        self.vector = check_vector(self.vector)

    def _install_hitbox(self):
        self.hitbox = []
        for i in range(360):
            vec = pygame.math.Vector2(0, -40).rotate(i)
            self.hitbox.append([int(self.x+self.size//2+vec.x), int(self.y+self.size//2+vec.y)])

    def verification(self):
        #Вызываем функию состояния
        if self.action == "attack": self.__attack()

        if self.__class__ == Hunter: self._check_motion()

        self._install_hitbox()

        if self.health <= 0:
            self.dying()

    def dying(self):
        if self.weapon is not None:
            self.weapon.master = None
        super().dying()

    @property
    def size(self): return self.__size


class Player(Hunter):
    img = get_files("person/blue-circle")
    def verification(self):

        self._check_motion()

        #Работаем с x координатой
        if self.x + self.size > camera_walls["x"]["right"]:
            for item in Primitive.memory:
                item.x -= self.speed

        elif self.x < camera_walls["x"]["left"]:
            for item in Primitive.memory:
                item.x += self.speed

        #Работаем с y координатой
        if self.y < camera_walls["y"]["up"]:
            for item in Primitive.memory:
                item.y += self.speed

        elif self.y > camera_walls["y"]["down"] - self.size:
            for item in Primitive.memory:
                item.y -= self.speed

        super().verification()


#Тестовый микрочелик отличающийся от своего предка только постоянными атаками
class Opponent(Hunter):
    img = get_files("person/red-circle")
    def verification(self):
        self.action = "attack"
        super().verification()


if __name__ == '__main__':
    #Создаём прлиложение
    app = pygame.display.set_mode(app_win)
    pygame.display.set_icon(icon)
    pygame.display.set_caption("Lonely Hunter")
    pygame.mixer.music.play(loops=-1)
    pygame.mixer.music.set_volume(0.6)
    clock = pygame.time.Clock()

    #Сущность которой мы можем управлять
    Hero = Player("Main Hero", app_win[0]//2 - 40, app_win[1]//2 - 40)

    #Тестовые сущности
    Opponent("Red Hunter", 525, 325)
    Stone("billy", 100, 100, 1)

    if debug_mode: print(f"Primitive.memory: {Primitive.memory}")

#Главный цикл
while game and __name__ == '__main__':
    clock.tick(FPS)

    for action in pygame.event.get():
        if action.type == pygame.QUIT:
            game = False

        if Hero in Primitive.memory:
            if action.type == pygame.MOUSEBUTTONDOWN:
                if action.button == 1:
                    Hero.action = "attack"

            if action.type == pygame.KEYDOWN:
                if action.key == pygame.K_x:
                    Hero.action = "attack"

                if action.key in key["moving player"]["LEFT"]:
                    Hero.movement["left"] = True
                if action.key in key["moving player"]["RIGHT"]:
                    Hero.movement["right"] = True

                if action.key in key["moving player"]["UP"]:
                    Hero.movement["up"] = True
                if action.key in key["moving player"]["DOWN"]:
                    Hero.movement["down"] = True

            if action.type == pygame.KEYUP:
                if action.key in key["moving player"]["LEFT"]:
                    Hero.movement["left"] = False
                if action.key in key["moving player"]["RIGHT"]:
                    Hero.movement["right"] = False

                if action.key in key["moving player"]["UP"]:
                    Hero.movement["up"] = False
                if action.key in key["moving player"]["DOWN"]:
                    Hero.movement["down"] = False


    app.fill(((28, 147, 64)))

    #Граница пересечение через которую начинает двигаться камера
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

    #Работа с обьектами в хранилище
    for item in Primitive.memory:
        #Личноклассовые вычесления
        try: item.verification()
        except AttributeError: pass

        #Рендер
        if item in Primitive.memory:
            app.blit(*item.drawing_data())
            #debug HUD обьектов
            if debug_mode:
                pygame.draw.rect(app, color["debug_mode"], (item.x, item.y, 1, 1))
                if item.__class__ in Weapon.__subclasses__() or item.__class__ in Hunter.__subclasses__():
                    for hitbox in item.hitbox:
                        pygame.draw.rect(app, color["debug_mode"], (hitbox[0], hitbox[1], 1, 1))

    pygame.display.update()
