from data import *

Errors = []


#Абстрактный класс всего что позволяет отрисовать pygame
class Primitive:
    #Хранилище всех сущностей для будущего отрисосвывания.
    memory = []

    def __init__(self, x, y):
        Primitive.memory.append(self)
        self.x = x
        self.y = y

    def _install_hitbox(self):
        self.hitbox = [[self.x, self.y]]

    def verification(self):
        self._install_hitbox()

    def _dying(self):
        if debug_mode and not self in Hud.memory: print(f"{self} died")
        self.__dict__ = {}
        Primitive.memory.remove(self)


class Hud(Primitive):
    memory = []

    def __init__(self, x=0, y=0, frames_to_death=FPS, movable=True, smoothing=False, eternal=False, master=None):
        super().__init__(x=x, y=y)
        Hud.memory.append(self)
        self.master = master
        self.initial_coordinates = [x, y]
        self.smoothing = smoothing
        self.frames_to_death = frames_to_death
        self.eternal = eternal
        self.movable = movable

    def verification(self):
        super().verification()
        if not self.master in Primitive.memory:
            self.master = None

        if self.master is not None:
            self.x, self.y = self.master.x, self.master.y

        if not self.movable:
            self.x, self.y = self.initial_coordinates

        if not self.eternal:
            self.frames_to_death -= 1
            if self.frames_to_death <= 0:
                self._dying()
                return None

    def _dying(self):
        super()._dying()
        Hud.memory.remove(self)

    def __repr__(self):
        return f"<HUD object>"


class Text(Hud):
    font_way = f"{folder_root}/material/general/fonts/Urbanist-Regular.ttf"

    def __init__(self, text, x=0, y=0, color=color["text"], frames_to_death=FPS, movable=True, smoothing=False, eternal=False, size=22, master=None):
        super().__init__(x=x, y=y, frames_to_death=frames_to_death, movable=movable, smoothing=smoothing, eternal=eternal, master=master)
        self.text = text
        self.size = size
        self.color = color

    def verification(self):
        self.drawing_data = pygame.font.Font(self.__class__.font_way, self.size).render(self.text, self.smoothing, self.color)
        super().verification()


    def draw(self):
        app.blit(self.drawing_data, (self.x, self.y))


class Score(Text):
    def verification(self):
        self.text = f"{self.master.killed} kills"
        super().verification()


class Indicator(Hud):
    def __init__(self, width, master=None, x=0, y=0, height=3, movable=True, smoothing=False, eternal=True):
        super().__init__(x=x, y=y, movable=movable, smoothing=smoothing, master=master, eternal=eternal)
        self.width = width
        self.height = height
        self.color = {
        "absence_health_line": color["absence_health_line"],
        "health_line": color["health_line"],
        "extra_health_line": color["extra_health_line"]
        }

    def draw(self):
        if self.master.health["real"] > self.master.health["max"] // 2:
            pygame.draw.rect(app, self.color["health_line"], (self.x, self.y-10, self.width, self.height))
            line_color = self.color["extra_health_line"]
            width_index = 1
        else:
            pygame.draw.rect(app, self.color["absence_health_line"], (self.x, self.y-10, self.width, self.height))
            more_overall_health = False
            line_color = self.color["health_line"]
            width_index = 0

        pygame.draw.rect(
            app,
            line_color,
            (self.x,
            self.y-10,
            int(self.width*(self.master.health["real"]/(self.master.health["max"]//2) - width_index)),
            self.height),
        )


class Static(Primitive):
    memory = []

    def __init__(self, x, y, img):
        super().__init__(x, y)
        Static.memory.append(self)

        self.img = img

    def __repr__(self):
        return f"<Static object>"

    def draw(self):
        app.blit(self.img, (self.x, self.y))

    def _dying(self):
        super()._dying()
        Static.memory.remove(self)

    @classmethod
    def initialize_instances(cls, amount=settings["number_of_plants"], area=plays_area):
        for i in range(amount):
            index = {
                "x": random(-area[0]//2, area[0]//2),
                "y": random(-area[1]//2, area[1]//2)
            }
            key_img = list(cls.images.keys())
            key_ = key_img[random(0, len(key_img)-1)]
            Static(index["x"], index["y"], cls.images[key_])


class Plants(Static):
    images = get_images("statics\plants")


class Entity(Primitive):
    memory = []

    def __init__(self, name, x, y, speed, vector, health=100):
        Entity.memory.append(self)
        self.name = name
        if debug_mode: print(f"{self} initialized")
        super().__init__(x, y)
        self.speed = speed
        self.health = {
            "real": health,
            "max": health*2
        }
        '''В игре 8 векторов, первый вектор обозначает 90°,
        последующие уменьшены на 45° от предыдущего'''
        self.vector = vector
        self.img = self.__class__.img

    def draw(self):
        app.blit(self.img[str(self.vector)], (self.x, self.y))

    def verification(self):
        if self.health["real"] <= 0:
            self._dying()
            return "dead"
        elif self.health["real"] > self.health["max"]:
            self.health["real"] = self.health["max"]

    def _dying(self):
        super()._dying()
        Entity.memory.remove(self)

    def __repr__(self):
        return f"<{self.name}>"


class Weapon(Entity):
    def __init__(self, name, damage=10, health=13, x=0, y=0, vector=1, speed=FPS, master=None):
        super().__init__(name=name, x=x, y=y, health=health, vector=vector, speed=speed)
        Entity.memory.remove(self)
        Entity.memory.insert(0, self)
        self.damage = damage
        #Ссылка на персонажа держущего оружие
        self.master = master
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

        if self.health["real"] <= 0:
            self._dying()

    def _dying(self):
        self.master.weapon = None
        super()._dying()

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
        super().verification()
        self.__update_coordinates()
        self._install_hitbox()


class Katana(Weapon):
    img = get_images(f"weapon/katana")
    average_speed = FPS // 10
    def __init__(self, name="katana", health=20, damage=10, speed=average_speed, x=0, y=0, vector=1, master=None):
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
class Hunter(Entity):
    def __init__(self, name, x, y, health=100, speed=5, vector=1, weapon=Katana):
        super().__init__(name=name, x=x, y=y, health=health, vector=vector, speed=speed)
        self.__size = 81
        self.__action = "quiet"
        self.killed = 0
        self.movement = {
            "left": False,
            "right": False,
            "up": False,
            "down": False
        }
        if weapon is not None:
            self.weapon = weapon(master=self)
        else:
            self.weapon = None

        if settings["health_indicator"]:
            self.indicator = Indicator(width=self.__size, x=self.x, y=self.y, master=self)
        else:
            self.indicator = None

    def _taking_damage(self, damage):
        self.health["real"] -= damage
        if settings["show_damage"]: Text(text=str(damage), x=self.x+self.size//2, y=self.y+self.size//2, color=color["show_damage"])
        if debug_mode: print(f"{self} suffered damage equal to {damage}, {self} have {self.health['real']}")

    def _hit(self, prey, damage):
        if debug_mode: print(f"{self} hit {prey}!")
        prey._taking_damage(self.weapon.damage)
        if prey.health["real"] <= 0:
            if settings["drain_health_on_kill"]: self.health["real"] += self.weapon.damage
            self.killed += 1

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
                    if prey is not self and prey.__class__ in presence_in_inheritance(Hunter):
                        for weapon_point in self.weapon.hitbox:
                            if weapon_point in prey.hitbox:
                                self.weapon.health["real"] -= 1

                                if prey.action is not "stun" or prey.weapon is None:
                                    self._hit(prey, self.weapon.damage)
                                else:
                                    self._hit(prey, self.weapon.damage // 2)

                                if self.vector in (6, 7, 8):
                                    prey.x -= self.weapon.damage * 5
                                if self.vector in (2, 3, 4):
                                    prey.x += self.weapon.damage * 5
                                if self.vector in (8, 1, 2):
                                    prey.y -= self.weapon.damage * 5
                                if self.vector in (4, 5, 6):
                                    prey.y += self.weapon.damage * 5

                                prey.action = "stun"
                                break

            self.weapon.vector = check_vector(self.weapon.vector)

        else:
            self.action = "quiet"

    def __stun(self):
        try:
            self.stun_attribute
        except AttributeError:
            self.stun_attribute = {
                "stun-time": FPS
            }
            if self.weapon is not None:
                self.weapon.action = {
                    "vector-buffer": -2
                }

        self.stun_attribute["stun-time"] -= 1
        if self.stun_attribute["stun-time"] <= 0:
            del self.stun_attribute
            del self.weapon.action
            self.__action = "quiet"

    def _run(self):
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
        super().verification()
        if self.action == "attack": self.__attack()
        elif self.action == "stun": self.__stun()

        if self.__class__ is not Player: self._run()

        self._install_hitbox()

    def _dying(self):
        if self.weapon is not None:
            self.weapon.master = None
        if self.indicator is not None:
            self.indicator._dying()
        super()._dying()

    @property
    def size(self): return self.__size

    @property
    def action(self): return self.__action
    @action.setter
    def action(self, state):
        if self.__action != "stun":
            self.__action = state


#Одноэкземплярный класс
class Player(Hunter):
    img = get_images("person/blue-circle")

    def verification(self):
        if debug_mode: self.health["real"] += 1
        self._run()
        self.__move_camera()
        super().verification()
        if self.weapon is None:
            self._pick_up_weapons()

    def __move_camera(self):
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

    def _pick_up_weapons(self, weapon=None):
        if weapon is None:
            for item in Primitive.memory:
                if item.__class__ in presence_in_inheritance(Weapon):
                    if item.master is None:
                        for hitbox_point in item.hitbox:
                            if hitbox_point in self.hitbox:
                                self.weapon = item
                                item.master = self
                                return None
        else:
            self.weapon = weapon

    def _dying(self):
        super()._dying()
        global exit
        exit = True
        Text(text="The End", x=176, y=150, frames_to_death=time_to_exit, movable=False, size=80)


class Opponent(Hunter):
    img = get_images("person/red-circle")
    waiting_attack = FPS // 2
    #test
    sum_all = 0
    spawn_places = [[x, y] for x in range(-81, app_win[0]) for y in [-81, app_win[1]]]
    spawn_places.extend([[x, y] for x in [-81, app_win[0]] for y in range(-81, app_win[0])])

    def __init__(self, x, y, name=None, health=100, speed=5, vector=1, weapon=Katana):
        Opponent.sum_all += 1
        if name is None: name = f"Opponent {Opponent.sum_all}"
        super().__init__(name=name, x=x, y=y, health=health, speed=speed, vector=vector, weapon=weapon)
        self.waiting_attack = self.__class__.waiting_attack

    def verification(self):
        for prey in Primitive.memory:
            if prey.__class__ in presence_in_inheritance(Player):
                if self.weapon is not None and self.action is not "stun":
                    if self.x // 10 > prey.x // 10: self.movement["left"] = True
                    else: self.movement["left"] = False

                    if self.x // 10 < prey.x // 10: self.movement["right"] = True
                    else: self.movement["right"] = False

                    if self.y // 10 > prey.y // 10: self.movement["up"] = True
                    else: self.movement["up"] = False

                    if self.y // 10 < prey.y // 10: self.movement["down"] = True
                    else: self.movement["down"] = False

                    self.waiting_attack -= 1
                    if self.waiting_attack <= 0:
                        self.action = "attack"
                        self.waiting_attack = self.__class__.waiting_attack
                    break

                else:
                    if self.x // 10 < prey.x // 10: self.movement["left"] = True
                    else: self.movement["left"] = False

                    if self.x // 10 > prey.x // 10: self.movement["right"] = True
                    else: self.movement["right"] = False

                    if self.y // 10 < prey.y // 10: self.movement["up"] = True
                    else: self.movement["up"] = False

                    if self.y // 10 > prey.y // 10: self.movement["down"] = True
                    else: self.movement["down"] = False
                    break

        super().verification()

    def _dying(self):
        super()._dying()
        random_place = Opponent.spawn_places[random(0, len(Opponent.spawn_places))]
        Opponent(x=random_place[0], y=random_place[1])


DRAW_QUEUE = [Static, Entity, Hud]

if __name__ == '__main__':
    #Создаём прлиложение
    app = pygame.display.set_mode(app_win)
    pygame.display.set_icon(icon)
    pygame.display.set_caption("Lonely Hunter")
    pygame.mixer.music.play(loops=-1)
    pygame.mixer.music.set_volume(0.5)
    clock = pygame.time.Clock()

    #Сущность которой мы можем управлять
    Hero = Player("Main Hero", app_win[0]//2 - 40, app_win[1]//2 - 40, speed=7, weapon=None)

    #Тестовые сущности
    if settings["score"]: Hero.score = Score(x=20, y=30, text="", movable=False, eternal=True, frames_to_death=time_to_exit, master=Hero)
    if settings["plants"]: Plants.initialize_instances()
    Opponent(525, 325)
    Katana("Excalibur", x=200, y=180, health=15, damage=20)

    if debug_mode: print(f"Primitive.memory: {Primitive.memory}\nHud.memory has {len(Hud.memory)} objects")

    #Главный цикл
    while game:
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

        app.fill((color["background"]))

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


        #Самоличностные вычисления
        for item in Primitive.memory:
            try:
                item.verification()
            except AttributeError as error:
                Errors.append(f"verification: {error}")

        #Рендер
        for class_ in DRAW_QUEUE:
            for item in class_.memory:
                try:
                    item.draw()

                    if debug_mode and item.__class__ in presence_in_inheritance(Entity):
                        for hitbox in item.hitbox:
                            pygame.draw.rect(app, color["debug_mode"], (hitbox[0], hitbox[1], 1, 1))
                except Exception as error:
                    Errors.append(f"draw: {error}")



        if exit and time_to_exit:
            if debug_mode: print(f"{round(time_to_exit/FPS, 2)} seconds left until the game closes")
            time_to_exit -= 1
            if time_to_exit <= 0:
                game = False

        pygame.display.update()

    if debug_mode:
        print(f"Entity.memory has {len(Entity.memory)} objects: {Entity.memory}\nHud.memory has {len(Hud.memory)} objects: {Hud.memory}\nStatic.memory has {len(Static.memory)} objects: {Static.memory}")
        print(f"\nEXCLUSION ZONE, {len(Errors)} errors")
        for error in Errors:
            print(error)
