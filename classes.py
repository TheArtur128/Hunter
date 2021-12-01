from sys import exit
from datetime import datetime

from data import *


#Суперкласс всего что может вычесляться
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

    def _get_hitbox_by_coordinates(self):
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


class Hud(Primitive):
    memory = []

    def __init__(self, x=0, y=0, frames_to_death=FPS, movable=True, eternal=False, master=None):
        super().__init__(x=x, y=y)
        Hud.memory.append(self)
        self.master = master
        self.initial_coordinates = [x, y]
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


class Indicator(Hud):
    def __init__(self, width, master=None, x=0, y=0, height=3, movable=True, eternal=True):
        super().__init__(x=x, y=y, movable=movable, master=master, eternal=eternal)
        self.width = width
        self.height = height


class HealthIndicator(Indicator):
    def draw(self, surface):
        if self.master.health["real"] > self.master.health["max"] // 2:
            pygame.draw.rect(surface, color["health_line"], (self.x, self.y-12, self.width, self.height))
            line_color = color["extra_line"]
            width_index = 1
        else:
            pygame.draw.rect(surface, color["absence_line"], (self.x, self.y-12, self.width, self.height))
            more_overall_health = False
            line_color = color["health_line"]
            width_index = 0

        pygame.draw.rect(
            surface,
            line_color,
            (self.x,
            self.y-12,
            int(self.width*(self.master.health["real"]/(self.master.health["max"]//2) - width_index)),
            self.height),
        )


class RushIndicator(Indicator):
    def draw(self, surface):
        pygame.draw.rect(surface, color["absence_line"], (self.x, self.y-7, self.width, self.height))

        if self.master.charge_level["dash"]["real"] < self.master.charge_level["dash"]["max"]:
            line_color = color["dash_line"]
        else:
            line_color = color["extra_line"]

        pygame.draw.rect(
            surface,
            line_color,
            (self.x,
            self.y-7,
            self.width*(self.master.charge_level["dash"]["real"]/self.master.charge_level["dash"]["max"]),
            self.height),
        )


class Text(Hud):
    font_way = f"{folder_root}/material/general/fonts/{settings['font']}"

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


class Score(Text):
    def verification(self):
        self.text = f"kills: {self.master.killed}"
        super().verification()


class SelectedWeaponsIndex(Text):
    def verification(self):
        if self.master.weapon is not None:
            weapon_index = self.master.inventory.index(self.master.weapon) + 1
            weapon_name = self.master.weapon.name
        else:
            weapon_index = None
            weapon_name = ""

        self.text = f"{weapon_index}/{len(self.master.inventory)}: {weapon_name}"
        super().verification()


class Static(Primitive):
    memory = []

    def __init__(self, x, y, img):
        super().__init__(x, y)
        Static.memory.append(self)
        self.img = img

    def __repr__(self):
        return f"<Static object>"

    def draw(self, surface):
        surface.blit(self.img, (self.x, self.y))

    def _dying(self):
        super()._dying()
        Static.memory.remove(self)

    @classmethod
    def initialize_instances(cls, amount, area=plays_area):
        for i in range(amount):
            index = {
                "x": random(-area[0]//2, area[0]//2),
                "y": random(-area[1]//2, area[1]//2)
            }
            key_img = list(cls.images.keys())
            key_ = key_img[random(0, len(key_img)-1)]
            Static(index["x"], index["y"], cls.images[key_])


class Plants(Static):
    images = get_files("statics\plants")


class Corpse(Static):
    images = complement_forms(get_files("statics\corpse"))


class GameplayEntity(Primitive):
    memory = []

    def __init__(self, name, x, y, speed, vector, health, img=None):
        GameplayEntity.memory.append(self)
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
        self.__vector = vector
        if img is None: self.img = self.__class__.img
        else: self.img = img
        self._update_size()

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
        GameplayEntity.memory.remove(self)

    def __repr__(self):
        return f"<{self.name}>"

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
    def __init__(self, master=None, x=0, y=0, vector=1, name=None, damage=None, health=None, speed=None, discarding_prey=None, img=None, status="common"):
        if status == "common":
            if name is None: name = self.__class__.name
            if health is None: health = self.__class__.health
            if speed is None: speed = self.__class__.speed
            if damage is None: self.__class__.damage
            if discarding_prey is None: self.__class__.discarding_prey
        elif status == "unique":
            if name is None: name = choice(names["weapons"])
            if health is None: health = random(self.__class__.health-settings["factor_of_unique_weapons"]//2, self.__class__.health+settings["factor_of_unique_weapons"]//2)
            if speed is None: speed = random(self.__class__.speed-settings["factor_of_unique_weapons"]//2, self.__class__.speed+settings["factor_of_unique_weapons"]//2)
            if damage is None: damage = random(self.__class__.damage-settings["factor_of_unique_weapons"]//2, self.__class__.damage+settings["factor_of_unique_weapons"]//2)
            if discarding_prey is None: discarding_prey = random(self.__class__.discarding_prey-settings["factor_of_unique_weapons"]//2, self.__class__.discarding_prey+settings["factor_of_unique_weapons"]//2)
        else:
            raise TypeError ("weapon status can only be common or unique")

        super().__init__(name=name, x=x, y=y, health=health, vector=vector, speed=speed, img=img)
        self.status = status
        self.master = master
        self.buffer_of_vector = 0

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
        if settings["hud"]: Text(text=f"{self.name} is broken", x=self.x+self.size[0]//2, y=self.y+self.size[0]//2, color=color["broken"])
        super()._dying()

    def verification(self):
        super().verification()
        self.__update_coordinates()


class Katana(Weapon):
    img = generation_forms(get_image(f"weapon/katana.png"))
    name = "Katana"
    health = 36
    damage = 10
    speed = 3
    discarding_prey = 40


class Mace(Weapon):
    img = generation_forms(get_image(f"weapon/mace.png"))
    name = "Mace"
    health = 24
    damage = 15
    speed = 4
    discarding_prey = 75


class Hammer(Weapon):
    img = generation_forms(get_image(f"weapon/hammer.png"))
    name = "Hammer"
    health = 21
    damage = 20
    speed = 4
    discarding_prey = 100


class Sword(Weapon):
    img = generation_forms(get_image(f"weapon/sword.png"))
    name = "Sword"
    health = 33
    damage = 12
    speed = 3
    discarding_prey = 75


class Scythe(Weapon):
    img = generation_forms(get_image(f"weapon/scythe.png"))
    name = "Scythe"
    health = 20
    damage = 17
    speed = 5
    discarding_prey = 95


class Hunter(GameplayEntity):
    skins = {}
    for directory in get_catalog("person"):
        skins[directory.replace("person/", "")] = complement_forms(get_files(directory))

    def __init__(self, name, x, y, health=100, speed=5, vector=1, weapon="random", weapon_status="common", img=None):
        super().__init__(name=name, x=x, y=y, health=health, vector=vector, speed=speed, img=img)
        self.__action = "quiet"
        self.killed = 0
        self.movement = {
            "left": False,
            "right": False,
            "up": False,
            "down": False
        }
        self.inventory = []
        if weapon == "random":
            if random(0, 100) < settings["spread_of_characteristics_for_unique_weapons"]:
                weapon_status_ = "unique"
            else:
                weapon_status_ = "common"
            self.weapon = choice(Weapon.__subclasses__())(master=self, status=weapon_status_)
        else:
            self.weapon = weapon

        if self.weapon is not None: self.inventory.append(self.weapon)

        if settings["hud"]:
            self.indicators = [
                HealthIndicator(width=self.size[0], height=3, x=self.x, y=self.y, master=self),
                RushIndicator(width=self.size[0], height=1, x=self.x, y=self.y, master=self)
            ]
        else:
            self.indicators = None

        self.charge_level = {
            "dash": {
                "real": 0,
                "max": 4*FPS
            }
        }

    def __taking_damage(self, damage):
        if self.action == "stun" and self.weapon is not None:
            damage //= 2

        if settings["hud"]: Text(text=str(damage), x=self.x+self.size[0]//2, y=self.y+self.size[0]//2, color=color["show_damage"])
        self.health["real"] -= damage
        if debug_mode: print(f"{self} suffered damage equal to {damage}, {self} have {self.health['real']} HP")

        if self.health["real"] <= 0: return "died"
        else: return "alive"

    def __hit(self, prey, damage):
        if debug_mode: print(f"{self} hit {prey}!")
        if prey.__taking_damage(damage) == "died":
            if settings["drain_health_on_kill"]:
                if debug_mode: print(f"{self} got {prey.health['max']//10} hp from the {prey}")
                self.health["real"] += prey.health["max"]//10
            self.killed += 1

    def __attack(self):
        for prey in Primitive.memory:
            if prey is not self and prey.__class__ in presence_in_inheritance(Hunter):
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
        #При первой итерации метода создаем атрибуты для работы это-го дейсвия
        try:
            self.weapon.action
        except AttributeError:
            self.weapon.action = {
                "time-indicator": self.weapon.__class__.speed,
                "iterations-done": 0 #Количество прошедших итераций. Нужно для эмуляции покадрового цикла
            }

        self.__attack()
        self.weapon.action["time-indicator"] -= 1
        if self.weapon.action["time-indicator"] <= 0:
            self.weapon.action["time-indicator"] = self.weapon.__class__.speed
            self.weapon.action["iterations-done"] += 1
            self.weapon.buffer_of_vector -= 1

            #Завершаем удар
            if self.weapon.action["iterations-done"] >= 4:
                self.action = "quiet"
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
                self.y -= self.speed * settings["dash_multiplier"]
            if self.vector in (2, 3, 4):
                self.x += self.speed * settings["dash_multiplier"]
            if self.vector in (4, 5, 6):
                self.y += self.speed * settings["dash_multiplier"]
            if self.vector in (6, 7, 8):
                self.x -= self.speed * settings["dash_multiplier"]

            if debug_mode: print(f"{self} made a rush")

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
        for item in Primitive.memory:
            if item.__class__ in presence_in_inheritance(Weapon):
                if item.master is None:
                    for hitbox_point in item.hitbox:
                        if hitbox_point in self.hitbox:
                            if debug_mode: print(f"{self} got {item}")
                            self.inventory.append(item)
                            Primitive.memory.remove(item)
                            GameplayEntity.memory.remove(item)
                            break

    def weapon_change(self):
        if self.weapon is not None:
            if self.inventory.index(self.weapon) == len(self.inventory)-1:
                new_weapon = self.inventory[0]
            else:
                new_weapon = self.inventory[self.inventory.index(self.weapon)+1]
            if debug_mode: print(f"{self} put the {new_weapon} into service")
            Primitive.memory.remove(self.weapon)
            GameplayEntity.memory.remove(self.weapon)
            new_weapon.buffer_of_vector = 0
            self.weapon = new_weapon
            self.weapon.master = self
            Primitive.memory.append(self.weapon)
            GameplayEntity.memory.append(self.weapon)
        else:
            if len(self.inventory) > 0:
                self.weapon = self.inventory[0]
                self.weapon.master = self
                Primitive.memory.append(self.inventory[0])
                GameplayEntity.memory.append(self.inventory[0])
        self.action = "quiet"

    def verification(self):
        super().verification()
        for action in self.charge_level:
            if self.charge_level[action]["real"] < self.charge_level[action]["max"]:
                self.charge_level[action]["real"] += 1

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
        if self.indicators is not None:
            for item in self.indicators:
                item._dying()
        Corpse(x=self.x, y=self.y, img=Corpse.images[str(self.vector)])
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

    @property
    def action(self): return self.__action
    @action.setter
    def action(self, state):
        if self.__action != "stun":
            self.__action = state


class Player(Hunter):
    img = Hunter.skins["blue"]
    hero = None

    def __init__(self, name, x, y, health=100, speed=5, vector=1, weapon="random", weapon_status="common", img=None):
        super().__init__(name=name, x=x, y=y, health=health, speed=speed, vector=vector, weapon=weapon, weapon_status=weapon_status, img=img)
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
    Opponent.set_class_attributes()

    def __init__(self, x, y, name=None, health=100, speed=5, waiting_attack=FPS//2, vector=1, img=None, weapon="random", weapon_status="common"):
        Opponent.total += 1
        super().__init__(name=f"Opponent {Opponent.total}" if name is None else name, x=x, y=y, health=health, speed=speed, vector=vector, weapon=weapon, img=img)
        self.waiting_attack = {
            "real": waiting_attack,
            "filled": waiting_attack
        }

    def _bot_work(self):
        for prey in Primitive.memory:
            if prey.__class__ in presence_in_inheritance(Player):
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
    def set_class_attributes(cls):
        cls.total = 0 #Умершие включительно
        cls.spawn_places = [[x, y] for x in range(-81, app_win[0]) for y in [-81, app_win[1]]]
        cls.spawn_places.extend([[x, y] for x in [-81, app_win[0]] for y in range(-81, app_win[0])])


class RedOpponent(Opponent):
    img = Hunter.skins["red"]

    def __init__(self, x, y, vector=1, weapon="random", weapon_status="common"):
        super().__init__(health=100, speed=5, waiting_attack=FPS//2, name=None, x=x, y=y, vector=vector, weapon=weapon, img=None)


class GreenOpponent(Opponent):
    img = Hunter.skins["green"]

    def __init__(self, x, y, vector=1, weapon="random", weapon_status="common"):
        super().__init__(health=150, speed=6, waiting_attack=FPS//2, name=None, x=x, y=y, vector=vector, weapon=weapon, img=None)


class PurpleOpponent(Opponent):
    img = Hunter.skins["purple"]

    def __init__(self, x, y, vector=1, weapon="random", weapon_status="common"):
        super().__init__(health=175, speed=6, waiting_attack=FPS//2, name=None, x=x, y=y, vector=vector, weapon=weapon, img=None)


class GoldOpponent(Opponent):
    img = Hunter.skins["gold"]

    def __init__(self, x, y, vector=1, weapon="random", weapon_status="common"):
        super().__init__(health=200, speed=7, waiting_attack=FPS//2, name=None, x=x, y=y, vector=vector, weapon=weapon, img=None)


class BlackOpponent(Opponent):
    img = Hunter.skins["black"]

    def __init__(self, x, y, vector=1, weapon="random", weapon_status="common"):
        super().__init__(health=300, speed=8, waiting_attack=FPS//2, name=None, x=x, y=y, vector=vector, weapon=weapon, img=None)


class Abstraction(Primitive):
    memory = []

    def __init__(self, x, y):
        super().__init__(x, y)
        Abstraction.memory.append(self)


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
                for item in group.memory:
                    if item is not self:
                        item.x += self.x - min(coordinates_my_master["x"])

            elif max(coordinates_my_master["x"]) > self.x+self.width:
                for item in group.memory:
                    if item is not self:
                        item.x += self.x+self.width - max(coordinates_my_master["x"])

            if min(coordinates_my_master["y"]) < self.y:
                for item in group.memory:
                    if item is not self:
                        item.y += self.y - min(coordinates_my_master["y"])

            elif max(coordinates_my_master["y"]) > self.y+self.height:
                for item in group.memory:
                    if item is not self:
                        item.y += self.y+self.height - max(coordinates_my_master["y"])

    def draw(self, surface):
        if debug_mode:
            pygame.draw.rect(surface, color["debug_mode"], (self.x, self.y, self.width, self.height), 1)
        else:
            pass


class GameZone(Wall):
    to_work_with_groups = [GameplayEntity, Static]

    def _working_with_objects_outside_of_self(self):
        for group in self.__class__.to_work_with_groups:
            for item in group.memory:
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


class Logger:
    def __init__(self):
        self.__logs = []

    def new_log(self, log_class, *atr):
        self.__logs.append(log_class(*atr))

    def show_all_logs(self):
        for log in self.__logs:
            print(log)

    def clear_my_logs(self):
        for log in self.__logs:
            self.__logs.remove(log)
            log.clear()

    @property
    def logs(self):
        return self.__logs


class GameLog:
    def __init__(self, *atr):
        self.update(*atr)

    def __str__(self):
        return f"{self.__prefix}. {self.__text} - {self.__time_of_creation}"

    def update(self, prefix, text, time_flag=True):
        self.__prefix = prefix
        self.__text = text
        self.__time_of_creation = datetime.now() if time_flag else None

    def clear(self):
        self.__dict__ = {}


class App:
    def __init__(self, size, icon, caption, music_catalog, FPS, time_to_exit, debugging):
        self.__caption = caption
        self.__size = size
        self.__debugging = debugging
        self.__time = True
        self.__time_to_exit = {"real": time_to_exit, "full": time_to_exit}
        self.__preparation_for_the_exit = False
        self.__FPS = FPS
        self.__icon = icon
        self.__music_catalog = music_catalog
        self.__logger = Logger()

    def __app_creation(self):
        self.__window = pygame.display.set_mode(self.__size)
        self.__clock = pygame.time.Clock()
        pygame.display.set_icon(self.__icon)
        pygame.display.set_caption(self.__caption)
        pygame.mixer.music.load(self.__music_catalog)

    def __set_start_scene(self):
        pygame.mixer.music.play(loops=-1)
        pygame.mixer.music.set_volume(0.5)

        for class_ in presence_in_inheritance(Primitive, "memory"):
            class_.memory = []

        self.__time_to_exit["real"] = self.__time_to_exit["full"]

        Player("Main Hero", tithe_win[0]*settings["factor_of_camera_width"], app_win[1]//2 - 40, speed=7, vector=3)

        Opponent.set_class_attributes()
        Opponent(app_win[0] - tithe_win[0]*settings["factor_of_camera_width"] - 80, app_win[1]//2 - 40, vector=7)

        GameZone(x=-plays_area[0]//2, y=-plays_area[1]//2, width=plays_area[0], height=plays_area[1])
        Camera(
            x=(app_win[0]-camera_area["width"])//2,
            y=(app_win[1]-camera_area["height"])//2,
            width=camera_area["width"],
            height=camera_area["height"],
            master=Player.hero
        )

        if settings["hud"]:
            Score(x=20, y=40, text="", movable=False, eternal=True, master=Player.hero)
            SelectedWeaponsIndex(x=20, y=15, text="", movable=False, eternal=True, master=Player.hero)

        if settings["plants"]: Plants.initialize_instances(amount=settings["number_of_plants"])

    def __button_maintenance(self):
        for action in pygame.event.get():
            if action.type == pygame.QUIT:
                self.stop()

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

                    if action.key in key["player"]["RUSH"]:
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
        for object in Primitive.memory:
            if self.__time:
                try:
                    object.verification()
                except Exception as error:
                    if not self.__preparation_for_the_exit:
                        self.__logger.new_log(
                            GameLog,
                            str(error.__class__).replace("<class ", "").replace(">", ""),
                            f"from verification{f' {object}' if 'name' in list(object.__dict__.keys()) else ''}: {error}"
                        )

    def __render(self):
        self.__window.fill((color["emptiness_of_map"]))
        for class_ in self.__draw_queue:
            for item in class_.memory:
                try:
                    item.draw(self.__window)
                    if self.__debugging and item.__class__ in presence_in_inheritance(GameplayEntity):
                        for hitbox in item.hitbox:
                            pygame.draw.rect(self.__window, color["debug_mode"], (hitbox[0], hitbox[1], 1, 1))
                except Exception as error:
                    if self.__debugging and not exit:
                        self.__logger.new_log(
                            GameLog,
                            str(error.__class__).replace("<class ", "").replace(">", ""),
                            f"from draw{f' {object}' if 'name' in list(object.__dict__.keys()) else ''}: {error}"
                        )

        if not self.__time:
            veil = pygame.Surface(app_win)
            veil.set_alpha(132)
            veil.fill((255, 255, 255))
            veil.blit(pygame.font.Font(f"{folder_root}/material/general/fonts/{settings['font']}", 80).render("Pause", False, color["text"]), (210, 150))
            self.__window.blit(veil, (0, 0))

        if Player.hero is None and self.__time_to_exit["real"]:
            print(f"{round(self.__time_to_exit['real']/FPS, 2)} seconds left until the game closes") if self.__debugging else None
            self.__window.blit(pygame.font.Font(f"{folder_root}/material/general/fonts/{settings['font']}", 80).render("The End", True, color["text"]), (176, 150))
            self.__window.blit(pygame.font.Font(f"{folder_root}/material/general/fonts/{settings['font']}", 21).render("Again?", True, color["text"]), (285, 235))
            self.__time_to_exit["real"] -= 1
            if self.__time_to_exit["real"] <= 0:
                self.stop()

        pygame.display.update()

    def run(self):
        self.__draw_queue = [Abstraction, Static, GameplayEntity, Hud]
        self.__app_creation()
        self.__set_start_scene()

        while True:
            self.__clock.tick(self.__FPS)
            self.__button_maintenance()
            self.__computation_for_all_objects()
            self.__render()

    def stop(self):
        if self.__debugging:
            print(f"\n{len(self.__logger.logs)} error's:")
            self.__logger.show_all_logs()

        pygame.quit()
        exit()
