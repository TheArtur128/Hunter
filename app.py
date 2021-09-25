from data import *

Errors = []


#Суперкласс всего что может вычесляться и отрисосвываться Pygame'ом
class Primitive:
    #Хранилище всех экземпляров для их вычислений
    memory = []

    def __init__(self, x, y):
        Primitive.memory.append(self)
        self.x = x
        self.y = y

    def _install_hitbox(self):
        self.hitbox = [[self.x, self.y]]

    def verification(self):
        self._install_hitbox()

    def get_hitbox_by_coordinates(self):
        coordinates = {
            "x": [],
            "y": []
        }
        for hitbox_point in self.hitbox:
            coordinates["x"].append(hitbox_point[0])
            coordinates["y"].append(hitbox_point[1])

        return coordinates

    def _dying(self):
        if debug_mode and not self in Hud.memory: print(f"{self} died")
        self.__dict__ = {}
        Primitive.memory.remove(self)


    def __repr__(self):
        return "<Abstraction>"


class Abstraction(Primitive):
    memory = []

    def __init__(self, x, y):
        super().__init__(x, y)
        Abstraction.memory.append(self)


class Wall(Abstraction):
    def __init__(self, x, y, width, height):
        super().__init__(x, y)
        self.width = width
        self.height = height

    def verification(self):
        super().verification()
        self._working_with_objects_outside_of_self()


class Camera(Wall):
    def __init__(self, x, y, width, height, master):
        super().__init__(x=x, y=y, width=width, height=height)
        self.master = master

    def verification(self):
        super().verification()

    def _working_with_objects_outside_of_self(self):
        coordinates_my_master = self.master.get_hitbox_by_coordinates()

        if min(coordinates_my_master["x"]) < self.x:
            for item in Primitive.memory:
                if item is not self:
                    item.x += self.x - min(coordinates_my_master["x"])

        elif max(coordinates_my_master["x"]) > self.x+self.width:
            for item in Primitive.memory:
                if item is not self:
                    item.x += self.x+self.width - max(coordinates_my_master["x"])

        if min(coordinates_my_master["y"]) < self.y:
            for item in Primitive.memory:
                if item is not self:
                    item.y += self.y - min(coordinates_my_master["y"])

        elif max(coordinates_my_master["y"]) > self.y+self.height:
            for item in Primitive.memory:
                if item is not self:
                    item.y += self.y+self.height - max(coordinates_my_master["y"])

    def draw(self):
        if debug_mode:
            pygame.draw.rect(app, color["debug_mode"], (self.x, self.y, self.width, self.height), 1)
        else:
            pass


class GameZone(Wall):
    #В случии это-го класса сдвигает все предметы если вышли за плошять экземпляра
    def _working_with_objects_outside_of_self(self):
        for item in Entity.memory:
            all_coordinates = item.get_hitbox_by_coordinates()
            if min(all_coordinates["x"]) < self.x:
                item.x += self.x - min(all_coordinates["x"])

            elif max(all_coordinates["x"]) > self.x+self.width:
                item.x += self.x+self.width - max(all_coordinates["x"])


            if min(all_coordinates["y"]) < self.y:
                item.y += self.y - min(all_coordinates["y"])

            elif max(all_coordinates["y"]) > self.y+self.height:
                item.y += self.y+self.height - max(all_coordinates["y"])

    def draw(self):
        pygame.draw.rect(app, color["background"], (self.x, self.y, self.width, self.height))


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
        self.update_size()

    def draw(self):
        app.blit(self.img[str(self.vector)], (self.x, self.y))

    def verification(self):
        self.update_size()
        super().verification()
        if self.health["real"] <= 0:
            self._dying()
            return "dead"
        elif self.health["real"] > self.health["max"]:
            self.health["real"] = self.health["max"]

    def update_size(self):
        self.size = self.img[str(self.vector)].get_rect().size

    def _dying(self):
        super()._dying()
        Entity.memory.remove(self)

    def __repr__(self):
        return f"<{self.name}>"


class Weapon(Entity):
    def __init__(self, x=0, y=0, vector=1, name=None, damage=None, health=None, speed=None, master=None, discarding_prey=None):
        if name is None: name = self.__class__.name
        if health is None: health = self.__class__.health
        if speed is None: speed = self.__class__.speed
        if damage is None: self.__class__.damage
        if discarding_prey is None: self.__class__.discarding_prey
        super().__init__(name=name, x=x, y=y, health=health, vector=vector, speed=speed)
        self.master = master
        self.coordinates_at_vectors = None
        self.buffer_of_vector = 0

    def __update_coordinates(self):
        if self.master is not None:
            self.vector = self.master.vector + self.buffer_of_vector
            self.vector = check_vector(self.vector)

            self.x = self.master.x + self.master.weapon_coordinates()[self.vector][0]
            self.y = self.master.y + self.master.weapon_coordinates()[self.vector][1]

    def _install_hitbox(self):
        self.hitbox = []
        if self.vector in (1, 5):
            for i in range(self.size[1]):
                self.hitbox.append([self.x+self.size[0]//2, self.y+i])
        elif self.vector in (2, 6):
            for i in range(self.size[1]):
                self.hitbox.append([self.x+i, self.y+self.size[1]-i])
        elif self.vector in (3, 7):
            for i in range(self.size[0]):
                self.hitbox.append([self.x+i, self.y+self.size[1]//2])
        elif self.vector in (4, 8):
            for i in range(self.size[1]):
                self.hitbox.append([self.x+i, self.y+i])

    def _dying(self):
        if self.master is not None:
            self.master.inventory.remove(self)
            self.master.weapon = None
        super()._dying()

    def verification(self):
        super().verification()
        self.__update_coordinates()


class Katana(Weapon):
    img = generation_forms(get_image(f"weapon/katana.png"))
    name = "katana"
    health = 20
    damage = 10
    speed = 3
    discarding_prey = 40


class Mace(Weapon):
    img = generation_forms(get_image(f"weapon/mace.png"))
    name = "mace"
    health = 15
    damage = 15
    speed = 4
    discarding_prey = 75


class Hammer(Weapon):
    img = generation_forms(get_image(f"weapon/hammer.png"))
    name = "hammer"
    health = 20
    damage = 20
    speed = 4
    discarding_prey = 100


class Sword(Weapon):
    img = generation_forms(get_image(f"weapon/sword.png"))
    name = "sword"
    health = 30
    damage = 12
    speed = 3
    discarding_prey = 75


#Персонажи как класс
class Hunter(Entity):
    def __init__(self, name, x, y, health=100, speed=5, vector=1, weapon="random"):
        super().__init__(name=name, x=x, y=y, health=health, vector=vector, speed=speed)
        self.__action = "quiet"
        self.killed = 0
        self.movement = {
            "left": False,
            "right": False,
            "up": False,
            "down": False
        }
        self.inventory = []
        if weapon is "random": self.weapon = choice(Weapon.__subclasses__())(master=self)
        elif weapon is not None: self.weapon = weapon(master=self)
        else: self.weapon = None

        if self.weapon is not None:
            self.inventory.append(self.weapon)

        if settings["health_indicator"]: self.indicator = Indicator(width=self.size[0], x=self.x, y=self.y, master=self)
        else: self.indicator = None

    def _taking_damage(self, damage):
        if self.action is not "stun" or self.weapon is None:
            self.health["real"] -= damage
            if settings["show_damage"]: Text(text=str(damage), x=self.x+self.size[0]//2, y=self.y+self.size[0]//2, color=color["show_damage"])
            if debug_mode: print(f"{self} suffered damage equal to {damage}, {self} have {self.health['real']}")
        else:
            self.health["real"] -= damage // 2
            if settings["show_damage"]: Text(text=str(damage//2), x=self.x+self.size[0]//2, y=self.y+self.size[0]//2, color=color["show_damage"])
            if debug_mode: print(f"{self} suffered damage equal to {damage//2}, {self} have {self.health['real']}, {self} protected itself")

    def _hit(self, prey, damage):
        if debug_mode: print(f"{self} hit {prey}!")
        prey._taking_damage(self.weapon.damage)
        if prey.health["real"] <= 0:
            if settings["drain_health_on_kill"]: self.health["real"] += self.weapon.damage
            self.killed += 1

    def __attack(self):
        for prey in Primitive.memory:
            if prey is not self and prey.__class__ in presence_in_inheritance(Hunter):
                for weapon_point in self.weapon.hitbox:
                    if weapon_point in prey.hitbox:
                        self.weapon.health["real"] -= 1
                        self._hit(prey, self.weapon.damage)

                        if self.vector in (6, 7, 8):
                            prey.x -= self.weapon.discarding_prey
                        if self.vector in (2, 3, 4):
                            prey.x += self.weapon.discarding_prey
                        if self.vector in (8, 1, 2):
                            prey.y -= self.weapon.discarding_prey
                        if self.vector in (4, 5, 6):
                            prey.y += self.weapon.discarding_prey

                        prey.action = "stun"
                        break

    def __chop(self):
        #При первой итерации метода создаем атрибуты для работы это-го дейсвия
        try:
            self.weapon.action
        except AttributeError:
            self.weapon.action = {
                "time-indicator": self.weapon.__class__.speed,
                "iterations-done": 0 #Количество прошедших итераций. Нужно для эмуляции покадрового цикла
            }

        #Уменьшаем счётчик до момента удара
        self.weapon.action["time-indicator"] -= 1
        if self.weapon.action["time-indicator"] <= 0:
            self.weapon.action["time-indicator"] = self.weapon.__class__.speed
            self.weapon.action["iterations-done"] += 1
            self.weapon.buffer_of_vector -= 1

            self.__attack()

            #Завершаем удар
            if self.weapon.action["iterations-done"] >= 4:
                self.action = "quiet"
                self.weapon.buffer_of_vector = 0
                del self.weapon.action

        self.weapon.vector = check_vector(self.weapon.vector)

    def __stun(self):
        try:
            self.stun_attribute
        except AttributeError:
            self.stun_attribute = {
                "stun-time": FPS
            }
            if self.weapon is not None:
                self.weapon.buffer_of_vector = -2

        self.stun_attribute["stun-time"] -= 1
        if self.stun_attribute["stun-time"] <= 0:
            del self.stun_attribute
            if self.weapon is not None: self.weapon.buffer_of_vector = 0
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
            self.hitbox.append([int(self.x+self.size[0]//2+vec.x), int(self.y+self.size[0]//2+vec.y)])

        for i in range(self.size[0]):
            self.hitbox.append([self.x+i, self.y+self.size[1]//2])
            self.hitbox.append([self.x+self.size[0]//2, self.y+i])

    def verification(self):
        super().verification()
        if self.weapon is not None:
            if self.action == "chop": self.__chop()
        if self.action == "stun": self.__stun()
        self._run()
        self._install_hitbox()

    def _dying(self):
        if self.weapon is not None:
            self.weapon.master = None
        if self.indicator is not None:
            self.indicator._dying()
        super()._dying()

    def weapon_coordinates(self):
        self.weapon.update_size()
        return {
            1: [self.size[0], 0],
            2: [self.size[0]*1.5-self.weapon.size[0], self.size[1]//2],
            3: [self.size[0]-self.weapon.size[0], self.size[1]],
            4: [self.size[0]//2-self.weapon.size[0], self.size[1]*1.5-self.weapon.size[1]],
            5: [-self.weapon.size[0], self.size[1]-self.weapon.size[1]],
            6: [-self.size[0]//2, self.size[1]//2-self.weapon.size[1]],
            7: [0, -self.weapon.size[1]],
            8: [self.size[0]//2, -self.size[1]//2]
        }

    @property
    def action(self): return self.__action
    @action.setter
    def action(self, state):
        if self.__action != "stun":
            self.__action = state


#Одноэкземплярный класс
class Player(Hunter):
    img = complement_forms(get_images("person/blue-circle"))

    def verification(self):
        super().verification()
        self._pick_up_items()
        if self.action is "weapon-change" or self.weapon is None:
            self.weapon_change()

    def _pick_up_items(self, weapon=None):
        for item in Primitive.memory:
            if item.__class__ in presence_in_inheritance(Weapon):
                if item.master is None:
                    for hitbox_point in item.hitbox:
                        if hitbox_point in self.hitbox:
                            if debug_mode: print(f"{self} got {item}")
                            self.inventory.append(item)
                            Primitive.memory.remove(item)
                            Entity.memory.remove(item)
                            break

    def weapon_change(self):
        if self.weapon is not None:
            if self.inventory.index(self.weapon) == len(self.inventory)-1:
                new_weapon = self.inventory[0]
            else:
                new_weapon = self.inventory[self.inventory.index(self.weapon)+1]
            if debug_mode: print(f"{self} put the {new_weapon} into service")
            Primitive.memory.remove(self.weapon)
            Entity.memory.remove(self.weapon)
            new_weapon.buffer_of_vector = 0
            self.weapon = new_weapon
            self.weapon.master = self
            Primitive.memory.append(self.weapon)
            Entity.memory.append(self.weapon)
        else:
            if len(self.inventory) > 0:
                self.weapon = self.inventory[0]
                self.weapon.master = self
                Primitive.memory.append(self.inventory[0])
                Entity.memory.append(self.inventory[0])
        self.action = "quiet"

    def _dying(self):
        super()._dying()
        global exit
        exit = True
        Text(text="The End", x=176, y=150, frames_to_death=time_to_exit, movable=False, size=80)


class Opponent(Hunter):
    img = complement_forms(get_images("person/red-circle"))
    waiting_attack = FPS // 2
    sum_all = 0
    spawn_places = [[x, y] for x in range(-81, app_win[0]) for y in [-81, app_win[1]]]
    spawn_places.extend([[x, y] for x in [-81, app_win[0]] for y in range(-81, app_win[0])])

    def __init__(self, x, y, name=None, health=100, speed=5, vector=1, weapon="random"):
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
                        self.action = "chop"
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


DRAW_QUEUE = [Abstraction, Static, Entity, Hud]

if __name__ == '__main__':
    #Создаём прлиложение
    app = pygame.display.set_mode(app_win)
    pygame.display.set_icon(icon)
    pygame.display.set_caption("Lonely Hunter")
    pygame.mixer.music.play(loops=-1)
    pygame.mixer.music.set_volume(0.5)
    clock = pygame.time.Clock()

    veil = pygame.Surface(app_win)
    veil.set_alpha(132)
    veil.fill((255, 255, 255))

    GameZone(x=-plays_area[0]//2, y=-plays_area[1]//2, width=plays_area[0], height=plays_area[1])

    #Сущность которой мы можем управлять
    Hero = Player("Main Hero", app_win[0]//2 - 40, app_win[1]//2 - 40, speed=7, weapon=None)
    Camera(
        x=(app_win[0]-camera_area["width"])//2,
        y=(app_win[1]-camera_area["height"])//2,
        width=camera_area["width"],
        height=camera_area["height"],
        master=Hero
    )
    if settings["score"]: Hero.score = Score(x=20, y=30, text="", movable=False, eternal=True, frames_to_death=time_to_exit, master=Hero)

    #Тестовые сущности
    if settings["plants"]: Plants.initialize_instances()
    Opponent(525, 325)
    Sword(name="Excalibur", x=200, y=180)
    Katana(name="Forest", x=150, y=180)
    Mace(name="Imperor", x=100, y=180)
    Hammer(name="Killer", x=50, y=180)

    if debug_mode: print(f"Entity.memory has {len(Entity.memory)} objects: {Entity.memory}\nHud.memory has {len(Hud.memory)} objects: {Hud.memory}\nStatic.memory has {len(Static.memory)} objects: {Static.memory}\n")

    #Главный цикл
    while game:
        clock.tick(FPS)

        for action in pygame.event.get():
            if action.type == pygame.QUIT:
                game = False

            if Hero in Primitive.memory:
                if action.type == pygame.MOUSEBUTTONDOWN:
                    if action.button == 1:
                        Hero.action = "chop"

                if action.type == pygame.KEYDOWN:
                    if action.key is pygame.K_SPACE:
                        Hero.action = "chop"

                    if action.key is pygame.K_BACKQUOTE:
                        if time: time = False
                        else: time = True

                    #test
                    if action.key in key["player"]["WEAPON_CHANGE"] and time:
                        Hero.weapon_change()

                    if action.key in key["player"]["LEFT"]:
                        Hero.movement["left"] = True
                    if action.key in key["player"]["RIGHT"]:
                        Hero.movement["right"] = True

                    if action.key in key["player"]["UP"]:
                        Hero.movement["up"] = True
                    if action.key in key["player"]["DOWN"]:
                        Hero.movement["down"] = True

                if action.type == pygame.KEYUP:
                    if action.key in key["player"]["LEFT"]:
                        Hero.movement["left"] = False
                    if action.key in key["player"]["RIGHT"]:
                        Hero.movement["right"] = False

                    if action.key in key["player"]["UP"]:
                        Hero.movement["up"] = False
                    if action.key in key["player"]["DOWN"]:
                        Hero.movement["down"] = False

        app.fill((color["emptiness_of_map"]))

        #Самоличностные вычисления
        for item in Primitive.memory:
            if time:
                try:
                    item.verification()
                except Exception as error:
                    if debug_mode and not exit:
                        try: Errors.append(f"from verification, {item}: {type(error)} {error}")
                        except AttributeError: Errors.append(f"from verification: {type(error)} {error}")

        #Рендер
        for class_ in DRAW_QUEUE:
            for item in class_.memory:
                try:
                    item.draw()
                    if debug_mode and item.__class__ in presence_in_inheritance(Entity):
                        for hitbox in item.hitbox:
                            pygame.draw.rect(app, color["debug_mode"], (hitbox[0], hitbox[1], 1, 1))
                except Exception as error:
                    if debug_mode and not exit:
                        try: Errors.append(f"from draw, {item}: {type(error)} {error}")
                        except AttributeError: Errors.append(f"from draw: {type(error)} {error}")

        if not time:
            app.blit(veil, (0, 0))

        if exit and time_to_exit:
            if debug_mode: print(f"{round(time_to_exit/FPS, 2)} seconds left until the game closes")
            time_to_exit -= 1
            if time_to_exit <= 0:
                game = False

        pygame.display.update()


    if debug_mode:
        print(f"\nEntity.memory has {len(Entity.memory)} objects: {Entity.memory}\nHud.memory has {len(Hud.memory)} objects: {Hud.memory}\nStatic.memory has {len(Static.memory)} objects: {Static.memory}")
        print(f"\nEXCLUSION ZONE, {len(Errors)} errors")
        for error in Errors:
            print(error)
