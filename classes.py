from sys import exit
from datetime import datetime

from data import *


class Primitive:
    '''Также суперкласс всего что может вычесляться'''
    
    visibility = [] #Хранилище всех экземпляров для их вычислений

    def __init__(self, x, y):
        Primitive.visibility.append(self)
        self.x = x
        self.y = y

    def _install_hitbox(self):
        self.hitbox = [[self.x, self.y]]

    def verification(self):
        self._install_hitbox()

    def _get_hitbox_by_coordinates(self):
        coordinates = {
            "x": [],
            "y": []
        }
        for hitbox_point in self.hitbox:
            coordinates["x"].append(hitbox_point[0])
            coordinates["y"].append(hitbox_point[1])

        return coordinates

    @staticmethod
    def set_at_beginning_of_visibility(object_):
        Primitive.visibility.remove(object_)
        Primitive.visibility.insert(0, object_)

    def _dying(self):
        log = local_logger.new_log(Log, f"{self} died")
        if debug_mode: print(log)
        self.__dict__ = {}
        Primitive.visibility.remove(self)


class Hud(Primitive):
    visibility = []

    def __init__(self, x=0, y=0, frames_to_death=FPS, movable=True, eternal=False, master=None):
        super().__init__(x, y)
        Hud.visibility.append(self)
        self.master = master
        self.initial_coordinates = [x, y]
        self.frames_to_death = frames_to_death
        self.eternal = eternal
        self.movable = movable

    def verification(self):
        super().verification()
        if not self.master in Primitive.visibility and self.master is not None:
            self._dying()
            return None

        if not self.movable:
            self.x, self.y = self.initial_coordinates

        elif self.master is not None:
            self.x, self.y = self.master.x, self.master.y

        if not self.eternal:
            self.frames_to_death -= 1
            if self.frames_to_death <= 0:
                self._dying()
                return None

    def _dying(self):
        super()._dying()
        Hud.visibility.remove(self)

    def __repr__(self):
        return f"<HUD object>"


class Indicator(Hud):
    def __init__(self, full_color=None, color_of_absence=color["absence line"], extra_color=color["extra line"], max_width=None, height=3, shift=[0, 0], master=None, x=0, y=0, movable=True, eternal=True, frames_to_death=FPS):
        super().__init__(x=x, y=y, movable=movable, master=master, eternal=eternal, frames_to_death=frames_to_death)
        self.max_width = self.master.size[0] if max_width is None else max_width
        self.height = height
        self.shift = shift
        self.colors = {
            "absence": color_of_absence,
            "full": self.__class__.color if full_color is None else full_color,
            "extra": extra_color
        }

    @property
    def width(self):
        return self.max_width

    @property
    def actual_color(self):
        return self.colors["full"]

    @property
    def background_color(self):
        return self.colors["absence"]

    def draw(self, surface):
        if self.width > self.max_width:
            raise AttributeError ("property \"width\" returns a value greater than the maximum")

        pygame.draw.rect(
            surface,
            self.background_color,
            (
                self.x + self.shift[0],
                self.y + self.shift[1],
                self.max_width,
                self.height
            ),
        )

        pygame.draw.rect(
            surface,
            self.actual_color,
            (
                self.x + self.shift[0],
                self.y + self.shift[1],
                self.width,
                self.height
            ),
        )


class HealthIndicator(Indicator):
    color = color["health line"]

    def __init__(self, master, max_width=None, height=3, shift=[0, -12], x=0, y=0, movable=True, eternal=True, frames_to_death=FPS):
        super().__init__(master=master, height=height, shift=shift, x=x, y=y, movable=movable, eternal=eternal, frames_to_death=frames_to_death)

    @property
    def width(self):
        if self.master.health_percentage <= 0.5:
            percent = self.master.health_percentage * 2
        else:
            percent = (self.master.health_percentage - 0.5)*2

        return int(self.max_width * percent)

    @property
    def actual_color(self):
        if self.master.health_percentage <= 0.5:
            return self.colors["full"]
        else:
            return self.colors["extra"]

    @property
    def background_color(self):
        if self.master.health_percentage <= 0.5:
            return self.colors["absence"]
        else:
            return self.colors["full"]


class DashIndicator(Indicator):
    color = color["dash line"]

    def __init__(self, master, max_width=None, height=1, shift=[0, -7], x=0, y=0, movable=True, eternal=True, frames_to_death=FPS):
        super().__init__(master=master, height=height, shift=shift, x=x, y=y, movable=movable, eternal=eternal, frames_to_death=frames_to_death)

    @property
    def width(self):
        return int(self.max_width * self.master.get_charge_percentage("dash"))

    @property
    def actual_color(self):
        if self.master.get_charge_percentage("dash") != 1:
            return self.colors["full"]
        else:
            return self.colors["extra"]


class Text(Hud):
    font_way = f"{folder_root}/material/general/fonts/{files['font']}"

    def __init__(self, text, x=0, y=0, color=color["text"], frames_to_death=FPS, movable=True, smoothing=True, eternal=False, size=21, master=None):
        super().__init__(x=x, y=y, frames_to_death=frames_to_death, movable=movable, eternal=eternal, master=master)
        self.smoothing = smoothing
        self.text = text
        self.size = size
        self.color = color

    def verification(self):
        self.drawing_data = pygame.font.Font(self.__class__.font_way, self.size).render(self.text, self.smoothing, self.color)
        super().verification()

    def draw(self, surface):
        surface.blit(self.drawing_data, (self.x, self.y))


class KillScore(Text):
    def verification(self):
        self.text = f"kills: {self.master.killed}"
        super().verification()


class InformationAboutSelectedWeapon(Text):
    def verification(self):
        weapon_index = self.master.inventory.index(self.master.weapon) + 1 if self.master.weapon is not None else None
        weapon_name = self.master.weapon.name if self.master.weapon is not None else ""

        self.text = f"{weapon_index}/{len(self.master.inventory)}: {weapon_name}"
        super().verification()


class Static(Primitive):
    visibility = []

    def __init__(self, x, y, img=None):
        super().__init__(x, y)
        Static.visibility.append(self)
        self.img = img if img is not None else choice(list(self.__class__.img.values()))

    def __repr__(self):
        return f"<Static object>"

    def draw(self, surface):
        surface.blit(self.img, (self.x, self.y))

    def _dying(self):
        super()._dying()
        Static.visibility.remove(self)

    @classmethod
    def initialize_instances(cls, amount, area=plays_area):
        for i in range(amount):
            cls(
                random(-area[0]//2, area[0]//2),
                random(-area[1]//2, area[1]//2)
            )


class Plants(Static):
    img = variety_of_forms(get_files("statics\plants"))


class Corpse(Static):
    img = complement_forms(get_files("statics\corpse"))


class GameplayEntity(Primitive):
    visibility = []

    def __init__(self, name, x, y, vector, health, img=None):
        self.name = name
        super().__init__(x, y)
        GameplayEntity.visibility.append(self)
        self.health = {
            "real": health,
            "max": health*2
        }
        self.__vector = vector
        if img is None: self.img = self.__class__.img
        else: self.img = img
        self._update_size()
        log = local_logger.new_log(Log, f"{self} initialized")
        if debug_mode: print(log)

    def draw(self, surface):
        surface.blit(self.img[str(self.vector)], (self.x, self.y))

    def verification(self):
        self._update_size()
        super().verification()
        if self.health["real"] <= 0:
            self._dying()
            return "dead"
        elif self.health["real"] > self.health["max"]:
            self.health["real"] = self.health["max"]

    def _update_size(self):
        self.__size = self.img[str(self.vector)].get_rect().size

    def _dying(self):
        super()._dying()
        GameplayEntity.visibility.remove(self)

    def hide_in(self, place):
        if self.is_hidden:
            raise AttributeError ("the object is already closed")
        else:
            Primitive.visibility.remove(self)
            GameplayEntity.visibility.remove(self)
            if place is not None: place.append(self)

    def outward(self):
        if not self.is_hidden:
            raise AttributeError ("the object is already outside")
        else:
            Primitive.visibility.append(self)
            GameplayEntity.visibility.append(self)

    def __repr__(self):
        return f"<{self.name}>"

    @property
    def is_hidden(self):
        if self in Primitive.visibility and self in GameplayEntity.visibility:
            return False
        else:
            return True

    @property
    def health_percentage(self):
        return self.health["real"] / self.health["max"]

    @property
    def size(self): return self.__size

    @property
    def vector(self): return self.__vector
    @vector.setter
    def vector(self, vaule):
        self.__vector = vaule
        if self.__vector < 1:
            self.__vector += 8
        elif self.__vector > 8:
            self.__vector -= 8


class Weapon(GameplayEntity):
    def __init__(self, master=None, x=0, y=0, vector=1, name=None, damage=None, health=None, weight=None, discarding_prey=None, img=None, status="common"):
        if status == "common":
            if name is None: name = self.__class__.name
            if health is None: health = self.__class__.health
            if weight is None: weight = self.__class__.weight
            if damage is None: self.__class__.damage
            if discarding_prey is None: self.__class__.discarding_prey
        elif status == "unique":
            if name is None: name = choice(names["weapons"])
            if health is None: health = random(self.__class__.health-settings["factor of unique weapons"]//2, self.__class__.health+settings["factor of unique weapons"]//2)
            if weight is None: weight = random(self.__class__.weight-settings["factor of unique weapons"]//2, self.__class__.weight+settings["factor of unique weapons"]//2)
            if damage is None: damage = random(self.__class__.damage-settings["factor of unique weapons"]//2, self.__class__.damage+settings["factor of unique weapons"]//2)
            if discarding_prey is None: discarding_prey = random(self.__class__.discarding_prey-settings["factor of unique weapons"]//2, self.__class__.discarding_prey+settings["factor of unique weapons"]//2)
        else:
            raise TypeError ("weapon status can only be common or unique")

        super().__init__(name=name, x=x, y=y, health=health, vector=vector, img=img)
        self.weight = weight
        self.status = status
        self.master = master
        self.buffer_of_vector = 0

        try:
            if self.master.weapon is None:
                self.master._equip_weapon(self)
            else:
                self.hide_in(self.master.inventory)
        except AttributeError: #Ошибка должна прилитать во время инициализации мастера
            self.hide_in(self.master.inventory)
            self.outward()


    def __update_coordinates(self):
        if self.master is not None:
            self.vector = self.master.vector + self.buffer_of_vector

            self.x = int(self.master.x + self.master.weapon_coordinates()[self.vector][0])
            self.y = int(self.master.y + self.master.weapon_coordinates()[self.vector][1])

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
        if settings["pop-up text"]: Text(text=f"{self.name} is broken", x=self.x+self.size[0]//2, y=self.y+self.size[0]//2, color=color["broken"])
        super()._dying()

    def verification(self):
        super().verification()
        self.__update_coordinates()


class Katana(Weapon):
    img = generation_forms(get_image(f"weapon/katana.png"))
    name = "Katana"
    health = 36
    damage = 10
    weight = 3
    discarding_prey = 40


class Mace(Weapon):
    img = generation_forms(get_image(f"weapon/mace.png"))
    name = "Mace"
    health = 24
    damage = 15
    weight = 4
    discarding_prey = 75


class Hammer(Weapon):
    img = generation_forms(get_image(f"weapon/hammer.png"))
    name = "Hammer"
    health = 21
    damage = 20
    weight = 4
    discarding_prey = 100


class Sword(Weapon):
    img = generation_forms(get_image(f"weapon/sword.png"))
    name = "Sword"
    health = 33
    damage = 12
    weight = 3
    discarding_prey = 75


class Scythe(Weapon):
    img = generation_forms(get_image(f"weapon/scythe.png"))
    name = "Scythe"
    health = 20
    damage = 17
    weight = 5
    discarding_prey = 95


class Hunter(GameplayEntity):
    skins = {directory.replace("person/", ""): complement_forms(get_files(directory)) for directory in get_catalog("person")}

    def __init__(self, name, x, y, health=100, speed=5, vector=1, weapon="random", img=None):
        super().__init__(name=name, x=x, y=y, health=health, vector=vector, img=img)
        self.speed = speed
        self.__action = "quiet"
        self.killed = 0
        self.movement = {
            "left": False,
            "right": False,
            "up": False,
            "down": False
        }
        self.charge_level = {
            "dash": {
                "real": 0,
                "max": 4*FPS
            }
        }
        self.inventory = []
        if weapon == "random":
            if random(0, 100) < settings["spread of characteristics for unique weapons"]:
                weapon_status = "unique"
            else:
                weapon_status = "common"
            self.weapon = choice(Weapon.__subclasses__())(master=self, status=weapon_status)
        else:
            self.weapon = weapon

        if settings["hud"]:
            HealthIndicator(master=self, height=3, shift=[0, -12])
            DashIndicator(master=self, height=1, shift=[0, -15])

    def __taking_damage(self, damage):
        if self.action == "stun" and self.weapon is not None:
            damage //= 2

        if settings["pop-up text"]: Text(text=str(damage), x=self.x+self.size[0]//2, y=self.y+self.size[0]//2, color=color["show damage"])
        self.health["real"] -= damage
        log = local_logger.new_log(Log, f"{self} suffered damage equal to {damage}, {self} have {self.health['real']} HP")
        if debug_mode: print(log)

        if self.health["real"] <= 0: return "died"
        else: return "alive"

    def __hit(self, prey, damage):
        log = local_logger.new_log(Log, f"{self} hit {prey}!")
        if debug_mode: print(log)
        if prey.__taking_damage(damage) == "died":
            if settings["drain health on kill"]:
                log = local_logger.new_log(Log, f"{self} got {prey.health['max']//10} hp from the {prey}")
                if debug_mode: print(log)
                self.health["real"] += prey.health["max"]//10
            self.killed += 1

    def __attack(self):
        for prey in Primitive.visibility:
            if prey is not self and prey.__class__ in get_family(Hunter):
                for weapon_point in self.weapon.hitbox:
                    if weapon_point in prey.hitbox:
                        self.weapon.health["real"] -= 1
                        self.__hit(prey, self.weapon.damage)

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
        #При первой итерации метода создаем атрибуты для работы это-го дейсвия #TO DO (later)
        try:
            self.weapon.action
        except AttributeError:
            self.weapon.action = {
                "time-indicator": self.weapon.__class__.weight,
                "iterations-done": 0 #Количество прошедших итераций. Нужно для эмуляции покадрового цикла
            }

        self.__attack()
        self.weapon.action["time-indicator"] -= 1
        if self.weapon.action["time-indicator"] <= 0:
            self.weapon.action["time-indicator"] = self.weapon.__class__.weight
            self.weapon.action["iterations-done"] += 1
            self.weapon.buffer_of_vector -= 1

            #Завершаем удар
            if self.weapon.action["iterations-done"] >= 4:
                self.__action = "quiet"
                self.weapon.buffer_of_vector = 0
                del self.weapon.action

    def __stun(self):
        if self.weapon is None:
            self.__action = "quiet"
            return None

        try:
            self.stun_attribute
        except AttributeError:
            self.stun_attribute = {
                "stun-time": FPS
            }
            log = local_logger.new_log(Log, f"{self} is stunned")
            if debug_mode: print(log)
            if self.weapon is not None:
                self.weapon.buffer_of_vector = -2

        self.stun_attribute["stun-time"] -= 1
        if self.stun_attribute["stun-time"] <= 0:
            del self.stun_attribute
            if self.weapon is not None: self.weapon.buffer_of_vector = 0
            self.__action = "quiet"

    def __dash(self):
        if self.charge_level["dash"]["real"] >= self.charge_level["dash"]["max"]:
            self.charge_level["dash"]["real"] = 0

            if self.vector in (8, 1, 2):
                self.y -= self.speed * settings["dash multiplier"]
            if self.vector in (2, 3, 4):
                self.x += self.speed * settings["dash multiplier"]
            if self.vector in (4, 5, 6):
                self.y += self.speed * settings["dash multiplier"]
            if self.vector in (6, 7, 8):
                self.x -= self.speed * settings["dash multiplier"]

            log = local_logger.new_log(Log, f"{self} made a dash")
            if debug_mode: print(log)

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
                    self.vector += choice([-1, 1])
                elif self.vector in [8, 1, 2]:
                    self.vector -= 1
                elif self.vector in [4, 5, 6]:
                    self.vector += 1

        elif self.movement["right"]:
            self.x += self.speed
            if not vector_ban:
                if self.vector == 7:
                    self.vector += choice([-1, 1])
                elif self.vector in [4, 5, 6]:
                    self.vector -= 1
                elif self.vector in [8, 1, 2]:
                    self.vector += 1

        #Изминение y координаты
        if self.movement["up"]:
            self.y -= self.speed
            if not vector_ban:
                if self.vector == 5:
                    self.vector += choice([-1, 1])
                elif self.vector in [2, 3, 4]:
                    self.vector -= 1
                elif self.vector in [6, 7, 8]:
                    self.vector += 1

        elif self.movement["down"]:
            self.y += self.speed
            if not vector_ban:
                if self.vector == 1:
                    self.vector += choice([-1, 1])
                elif self.vector in [2, 3, 4]:
                    self.vector += 1
                elif self.vector in [6, 7, 8]:
                    self.vector -= 1

        self.vector = self.vector

    def _install_hitbox(self):
        self.hitbox = []
        for i in range(360):
            vec = pygame.math.Vector2(0, -40).rotate(i)
            self.hitbox.append([int(self.x+self.size[0]//2+vec.x), int(self.y+self.size[0]//2+vec.y)])

        for i in range(self.size[0]):
            self.hitbox.append([self.x+i, self.y+self.size[1]//2])
            self.hitbox.append([self.x+self.size[0]//2, self.y+i])

    def _pick_up_items(self):
        for item in GameplayEntity.visibility:
            if item.__class__ in get_family(Weapon):
                if item.master is None:
                    for hitbox_point in item.hitbox:
                        if hitbox_point in self.hitbox:
                            log = local_logger.new_log(Log, f"{self} got {item}")
                            if debug_mode: print(log)
                            item.hide_in(self.inventory)
                            break

    def _equip_weapon(self, weapon):
        self.weapon = weapon
        self.weapon.master = self
        if self.weapon.is_hidden:
            self.weapon.outward()
        log = local_logger.new_log(Log, f"{self} put the {weapon} into service")
        if debug_mode: print(log)

    def weapon_change(self):
        if self.weapon is not None:
            if self.inventory.index(self.weapon) == len(self.inventory)-1:
                next_weapon = self.inventory[0]
            else:
                next_weapon = self.inventory[self.inventory.index(self.weapon)+1]

            self.weapon.hide_in(None)
            next_weapon.buffer_of_vector = 0
            self._equip_weapon(next_weapon)
        else:
            if len(self.inventory) > 0:
                self._equip_weapon(self.inventory[0])

        self.__action = "quiet"

    def __activity_charging(self):
        for action in self.charge_level:
            if self.charge_level[action]["real"] < self.charge_level[action]["max"]:
                self.charge_level[action]["real"] += 1

    def verification(self):
        super().verification()
        self.__activity_charging()

        if self.weapon is not None:
            if self.action == "chop": self.__chop()
        else:
            if len(self.inventory) >= 1:
                self.weapon_change()
        if self.action == "weapon-change": self.weapon_change()
        if self.action == "dash": self.__dash()
        if self.action == "stun": self.__stun()

        self._run()
        self._install_hitbox()

    def _dying(self):
        if self.weapon is not None:
            self.weapon.master = None
        Corpse(x=self.x, y=self.y, img=Corpse.img[str(self.vector)])
        super()._dying()

    def weapon_coordinates(self):
        self.weapon._update_size()
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

    def get_charge_percentage(self, action):
        return self.charge_level[action]["real"] / self.charge_level[action]["max"]

    @property
    def action_hierarchy(self):
        return ("quiet", "weapon-change", "chop", "dash", "stun")

    @property
    def action(self): return self.__action
    @action.setter
    def action(self, state):
        if self.action_hierarchy.index(state) > self.action_hierarchy.index(self.__action):
            for action in list(self.charge_level.keys()):
                if action == state:
                    if self.charge_level[state]["real"] < self.charge_level[state]["max"]:
                        return
                    else:
                        break

            self.__action = state
            if self.weapon is not None:
                self.weapon.buffer_of_vector = 0


class Player(Hunter):
    img = Hunter.skins[files["player skin"]]
    hero = None

    def __init__(self, name, x, y, health=100, speed=5, vector=1, weapon="random", img=None):
        super().__init__(name=name, x=x, y=y, health=health, speed=speed, vector=vector, weapon=weapon, img=img)
        Player.hero = self

    def verification(self):
        super().verification()
        self._pick_up_items()

    def _dying(self):
        super()._dying()
        Player.hero = None
        Text(text="The End", x=176, y=150, frames_to_death=time_to_exit, movable=False, size=80)
        Text(text="Again?", x=285, y=235, frames_to_death=time_to_exit, movable=False, size=21)


class Opponent(Hunter):
    total = 0 #Умершие включительно
    spawn_places = [[x, y] for x in range(-81, app_win[0]) for y in [-81, app_win[1]]]
    spawn_places.extend([[x, y] for x in [-81, app_win[0]] for y in range(-81, app_win[0])])

    def __init__(self, x, y, name=None, health=100, speed=5, waiting_attack=FPS//2, vector=1, img=None, weapon="random"):
        Opponent.total += 1
        super().__init__(name=f"Opponent {Opponent.total}" if name is None else name, x=x, y=y, health=health, speed=speed, vector=vector, weapon=weapon, img=img)
        self.waiting_attack = {
            "real": waiting_attack,
            "filled": waiting_attack
        }

    def _dying(self):
        super()._dying()
        point = choice(Opponent.spawn_places)
        self.get_class_of_opponent_by_level()(x=point[0], y=point[1])

    def _bot_work(self):
        for prey in Primitive.visibility:
            if prey.__class__ in get_family(Player):
                if self.weapon is not None and self.action != "stun":
                    self._move(prey, direction=True)
                    self.waiting_attack["real"] -= 1
                    if self.waiting_attack["real"] <= 0:
                        self.action = "chop"
                        self.waiting_attack["real"] = self.waiting_attack["filled"]
                    break
                else:
                    self._move(prey, direction=False)

        if self.charge_level["dash"]["real"] >= self.charge_level["dash"]["max"]:
            self.action = "dash"

    def verification(self):
        self._bot_work()
        super().verification()

    def _move(self, prey, direction=True):
        if self.x > (prey.x+prey.size[0]//2): self.movement["left"] = direction
        else: self.movement["left"] = not direction

        if (self.x+self.size[0]//2) < prey.x: self.movement["right"] = direction
        else: self.movement["right"] = not direction

        if self.y > (prey.y+prey.size[1]//2): self.movement["up"] = direction
        else: self.movement["up"] = not direction

        if (self.y+self.size[1]//2) < prey.y: self.movement["down"] = direction
        else: self.movement["down"] = not direction

    @classmethod
    def get_level(cls):
        return cls.total // (settings["Opponents for new opponent level"] + settings["cape for add. opponent level"]*(cls.total//settings["Opponents for new opponent level"]))

    @staticmethod
    def get_class_of_opponent_by_level(level: int = None):
        opponents_by_level = {
            0: RedOpponent,
            1: GreenOpponent,
            2: PurpleOpponent,
            3: GoldOpponent,
            4: BlackOpponent
        }
        try:
            return opponents_by_level[Opponent.get_level() if level is None else level]
        except IndexError:
            return opponents_by_level[list(opponents_by_level.keys())[-1]]


class RedOpponent(Opponent):
    img = Hunter.skins["red"]

    def __init__(self, x, y, name=None, vector=1, weapon="random"):
        super().__init__(health=100, speed=5, waiting_attack=FPS//2, name=name, x=x, y=y, vector=vector, weapon=weapon, img=None)


class GreenOpponent(Opponent):
    img = Hunter.skins["green"]

    def __init__(self, x, y, name=None, vector=1, weapon="random"):
        super().__init__(health=150, speed=6, waiting_attack=FPS//2, name=name, x=x, y=y, vector=vector, weapon=weapon, img=None)


class PurpleOpponent(Opponent):
    img = Hunter.skins["purple"]

    def __init__(self, x, y, name=None, vector=1, weapon="random"):
        super().__init__(health=175, speed=6, waiting_attack=FPS//2, name=name, x=x, y=y, vector=vector, weapon=weapon, img=None)


class GoldOpponent(Opponent):
    img = Hunter.skins["gold"]

    def __init__(self, x, y, name=None, vector=1, weapon="random"):
        super().__init__(health=200, speed=7, waiting_attack=FPS//2, name=name, x=x, y=y, vector=vector, weapon=weapon, img=None)


class BlackOpponent(Opponent):
    img = Hunter.skins["black"]

    def __init__(self, x, y, name=None, vector=1, weapon="random"):
        super().__init__(health=300, speed=8, waiting_attack=FPS//2, name=name, x=x, y=y, vector=vector, weapon=weapon, img=None)


class Abstraction(Primitive):
    visibility = []

    def __init__(self, x, y):
        super().__init__(x, y)
        Abstraction.visibility.append(self)
        self.set_at_beginning_of_visibility(self)

    def __repr__(self):
        return "<Abstraction>"


class Wall(Abstraction):
    to_work_with_groups = []

    def __init__(self, x, y, width, height):
        super().__init__(x, y)
        self.width = width
        self.height = height

    def _working_with_objects_outside_of_self(self):
        pass

    def _working_with_objects_inside_of_self(self):
        pass

    def verification(self):
        super().verification()
        self._working_with_objects_inside_of_self()
        self._working_with_objects_outside_of_self()


class Camera(Wall):
    to_work_with_groups = [Primitive]

    def __init__(self, x, y, width, height, master):
        super().__init__(x=x, y=y, width=width, height=height)
        self.master = master

    def _working_with_objects_outside_of_self(self):
        coordinates_my_master = self.master._get_hitbox_by_coordinates()

        for group in self.__class__.to_work_with_groups:
            if min(coordinates_my_master["x"]) < self.x:
                for item in group.visibility:
                    if item is not self:
                        item.x += self.x - min(coordinates_my_master["x"])

            elif max(coordinates_my_master["x"]) > self.x+self.width:
                for item in group.visibility:
                    if item is not self:
                        item.x += self.x+self.width - max(coordinates_my_master["x"])

            if min(coordinates_my_master["y"]) < self.y:
                for item in group.visibility:
                    if item is not self:
                        item.y += self.y - min(coordinates_my_master["y"])

            elif max(coordinates_my_master["y"]) > self.y+self.height:
                for item in group.visibility:
                    if item is not self:
                        item.y += self.y+self.height - max(coordinates_my_master["y"])

    def draw(self, surface):
        if debug_mode:
            pygame.draw.rect(surface, color["debug mode"], (self.x, self.y, self.width, self.height), 1)
        else:
            pass


class GameZone(Wall):
    to_work_with_groups = [GameplayEntity, Static]

    def _working_with_objects_outside_of_self(self):
        for group in self.__class__.to_work_with_groups:
            for item in group.visibility:
                all_coordinates = item._get_hitbox_by_coordinates()

                if min(all_coordinates["x"]) < self.x:
                    item.x += self.x - min(all_coordinates["x"])

                elif max(all_coordinates["x"]) > self.x+self.width:
                    item.x += self.x+self.width - max(all_coordinates["x"])

                if min(all_coordinates["y"]) < self.y:
                    item.y += self.y - min(all_coordinates["y"])

                elif max(all_coordinates["y"]) > self.y+self.height:
                    item.y += self.y+self.height - max(all_coordinates["y"])

    def draw(self, surface):
        pygame.draw.rect(surface, color["background"], (self.x, self.y, self.width, self.height))


class Minimap(Hud):
    def __init__(self, visibility: GameZone, size_factor: int, size_of_objects=settings["size of objects on minimap"], transparency=settings["minimap transparency"], x=0, y=0, movable=False, eternal=True, frames_to_death=FPS):
        super().__init__(x=x, y=y, movable=movable, master=None, eternal=eternal, frames_to_death=frames_to_death)
        self.size_factor = size_factor
        self.size_of_objects = size_of_objects
        self.transparency = transparency
        self.visibility = visibility

    def verification(self):
        super().verification()
        self._update_surface()

    def _update_surface(self):
        self.surface = pygame.Surface(self.size)
        self.surface.set_alpha(255 * self.transparency)
        self.surface.fill(color["minimap"])
        for group in [group.visibility for group in self.visibility.to_work_with_groups]:
            for object in group:
                if object.__class__ in self.classes_attributes_for_drawing.keys():
                    pygame.draw.circle(
                        self.surface,
                        self.classes_attributes_for_drawing[object.__class__]["color"],
                        (
                            -int((self.visibility.x - object.x)*self.size_factor),
                            -int((self.visibility.y - object.y)*self.size_factor),
                        ),
                        self.size_of_objects * self.classes_attributes_for_drawing[object.__class__]["factor"]
                    )

    def draw(self, surface):
        surface.blit(self.surface, (self.x, self.y))

    @property
    def size(self):
        return (int(self.visibility.width * self.size_factor), int(self.visibility.height * self.size_factor))

    @property
    def classes_attributes_for_drawing(self):
        return {
            **{hunter: {"color": color["hunters on minimap"], "factor": 1} for hunter in get_family(Hunter)},
            **{weapon: {"color": color["weapons on minimap"], "factor": 0.5} for weapon in get_family(Weapon)},
            BlackOpponent: {"color": color["corpses on minimap"], "factor": 1},
            Corpse: {"color": color["corpses on minimap"], "factor": 1}
        }


class Logger:
    file_start_time = datetime.now()

    def __init__(self):
        self.__logs = []

    def new_log(self, log_class, *log_atrs):
        log = log_class(*log_atrs)
        self.__logs.append(log)
        return log

    def show_logs(self):
        for log in self.__logs:
            print(log)

    def clear_logs(self):
        for log in self.__logs:
            self.__logs.remove(log)
            log.clear()

    def write_logs_to_file(self, file_name="logs.log"):
        if not settings["overwrite log file"]:
            try:
                with open(file_name) as file:
                    if file.read().replace(" ", "") == "":
                        file_is_empty = True
                    else:
                        file_is_empty = False
            except FileNotFoundError:
                file_is_empty = True
        else:
            with open(file_name, "w"):
                pass
            file_is_empty = True        

        with open(file_name, "a") as file:
            file.write(("\n" if not file_is_empty else "") + "logs from " + str(Logger.file_start_time))
            for log in self.logs:
                file.write("\n" + str(log))
                    

    @property
    def logs(self):
        return self.__logs


class Log:
    def __init__(self, *atr):
        self.update(*atr)

    def update(self, text, time_flag=True):
        self.__date = {
            "text": text,
            "time of creation": datetime.now() - Logger.file_start_time if time_flag else None #Время от старта файла
        }

    def __str__(self):
        return f"[{self.__date['time of creation'] if self.__date['time of creation'] is not None else ''}] {self.__date['text']}"

    def clear(self):
        self.__dict__ = {}


class App:
    def __init__(self, size, icon, caption, music_catalog, FPS, time_to_exit, debugging, logger=None):
        self.__caption = caption
        self.__size = size
        self.__debugging = debugging
        self.__time = True
        self.__time_to_exit = {"real": time_to_exit, "full": time_to_exit}
        self.__FPS = FPS
        self.__icon = icon
        self.__music_catalog = music_catalog
        self.__logger = logger

    def __app_creation(self):
        self.__window = pygame.display.set_mode(self.__size)
        self.__clock = pygame.time.Clock()
        pygame.display.set_icon(self.__icon)
        pygame.display.set_caption(self.__caption)
        pygame.mixer.music.load(self.__music_catalog)

    def __set_start_scene(self):
        for class_ in sorting_by_attribute(get_family(Primitive), "visibility"):
            class_.visibility = []

        self.__time_to_exit["real"] = self.__time_to_exit["full"]

        pygame.mixer.music.play(loops=-1)
        pygame.mixer.music.set_volume(0.5)

        Player("Main Hero", tithe_win[0]*settings["factor of camera width"], app_win[1]//2 - 40, speed=7, vector=3)

        Opponent.total = 0
        Opponent.get_class_of_opponent_by_level()(x=app_win[0] - tithe_win[0]*settings["factor of camera width"] - 80, y=app_win[1]//2 - 40, vector=7)

        gm_zone = GameZone(x=-plays_area[0]//2, y=-plays_area[1]//2, width=plays_area[0], height=plays_area[1])
        
        if settings["minimap"]:
            Minimap(
                visibility=gm_zone,
                transparency=settings["minimap transparency"] if not settings["show minimap when pressing the key"] else 0,
                size_factor=settings["minimap size factor"],
                x=app_win[0] - plays_area[0]*settings["minimap size factor"] - 4,
                y=5
            )

        Camera(
            x=(app_win[0]-camera_area["width"])//2,
            y=(app_win[1]-camera_area["height"])//2,
            width=camera_area["width"],
            height=camera_area["height"],
            master=Player.hero
        )

        if settings["hud"]:
            KillScore(x=20, y=40, text="", movable=False, eternal=True, master=Player.hero)
            InformationAboutSelectedWeapon(x=20, y=15, text="", movable=False, eternal=True, master=Player.hero)

        if settings["plants"]:
            Plants.initialize_instances(amount=settings["number of plants"])

    def __button_maintenance(self):
        for action in pygame.event.get():
            if action.type == pygame.QUIT:
                self.stop()

            if settings["show minimap when pressing the key"]:
                if action.type == pygame.KEYDOWN:
                    if action.key in key["menu"]["ENABLE MINIMAP"]:
                        for object_ in Hud.visibility:
                            if object_.__class__ == Minimap:
                                object_.transparency = settings["minimap transparency"]

                if action.type == pygame.KEYUP:
                    if action.key in key["menu"]["ENABLE MINIMAP"]:
                        for object_ in Hud.visibility:
                            if object_.__class__ == Minimap:
                                object_.transparency = 0

            if Player.hero is not None:
                if action.type == pygame.MOUSEBUTTONDOWN:
                    if action.button == 1:
                        Player.hero.action = "chop"
                    if action.button == 3:
                        Player.hero.action = "dash"

                if action.type == pygame.KEYDOWN:
                    if action.key in key["player"]["ATTACK"]:
                        Player.hero.action = "chop"

                    if action.key in key["player"]["PAUSE"]:
                        if self.__time:
                            self.__time = False
                            pygame.mixer.music.pause()
                        else:
                            self.__time = True
                            pygame.mixer.music.unpause()

                    if action.key in key["player"]["DASH"]:
                        Player.hero.action = "dash"

                    if action.key in key["player"]["WEAPON_CHANGE"]:
                        Player.hero.action = "weapon-change"

                    if action.key in key["player"]["LEFT"]:
                        Player.hero.movement["left"] = True
                    if action.key in key["player"]["RIGHT"]:
                        Player.hero.movement["right"] = True

                    if action.key in key["player"]["UP"]:
                        Player.hero.movement["up"] = True
                    if action.key in key["player"]["DOWN"]:
                        Player.hero.movement["down"] = True

                if action.type == pygame.KEYUP:
                    if action.key in key["player"]["LEFT"]:
                        Player.hero.movement["left"] = False
                    if action.key in key["player"]["RIGHT"]:
                        Player.hero.movement["right"] = False

                    if action.key in key["player"]["UP"]:
                        Player.hero.movement["up"] = False
                    if action.key in key["player"]["DOWN"]:
                        Player.hero.movement["down"] = False
            else:
                if action.type == pygame.KEYDOWN:
                    if action.key in key["menu"]["AGAIN"]:
                        self.__set_start_scene()          

    def __computation_for_all_objects(self):
        for object in Primitive.visibility:
            if self.__time:
                try:
                    object.verification()

                except Exception as error:
                    error_name = str(error.__class__).replace('<class ', '').replace('>', '')
                    log = self.__logger.new_log(
                         Log,
                        f"from verification {object.__class__} instance: {error_name} {error}"
                    )
                    print(log) if self.__debugging else None

    def __render(self):
        self.__window.fill((color["emptiness of map"]))
        for class_ in self.__draw_queue:
            for item in class_.visibility:
                try:
                    item.draw(self.__window)
                    if self.__debugging and item.__class__ in get_family(GameplayEntity):
                        for hitbox in item.hitbox:
                            pygame.draw.rect(self.__window, color["debug mode"], (hitbox[0], hitbox[1], 1, 1))

                except Exception as error:
                    error_name = str(error.__class__).replace('<class ', '').replace('>', '')
                    log = self.__logger.new_log(
                        Log,
                        f"from draw {item.__class__} instance: {error_name} {error}"
                    )
                    if self.__debugging: print(log)

        if not self.__time:
            veil = pygame.Surface(app_win)
            veil.set_alpha(132)
            veil.fill((255, 255, 255))
            veil.blit(pygame.font.Font(f"{folder_root}/material/general/fonts/{files['font']}", 80).render("Pause", False, color["text"]), (210, 150))
            self.__window.blit(veil, (0, 0))

        pygame.display.update()

    def __exit(self):
        log = self.__logger.new_log(Log, f"{round(self.__time_to_exit['real']/FPS, 2)} seconds left until the game closes")
        print(log) if self.__debugging else None
        self.__window.blit(pygame.font.Font(f"{folder_root}/material/general/fonts/{files['font']}", 80).render("The End", True, color["text"]), (176, 150))
        self.__window.blit(pygame.font.Font(f"{folder_root}/material/general/fonts/{files['font']}", 21).render("Again?", True, color["text"]), (285, 235))
        self.__time_to_exit["real"] -= 1
        if self.__time_to_exit["real"] <= 0:
            self.stop()

        pygame.display.update()

    def run(self):
        self.__app_creation()
        self.__set_start_scene()

        while True:
            self.__clock.tick(self.__FPS)
            self.__button_maintenance()
            self.__computation_for_all_objects()
            self.__render()
            if Player.hero is None and self.__time_to_exit["real"]:
                self.__exit()

    def stop(self):
        if settings["remember logs"]: self.__logger.write_logs_to_file()
        pygame.quit()
        exit()

    @property
    def __draw_queue(self):
        return [Abstraction, Static, GameplayEntity, Hud]


local_logger = Logger()