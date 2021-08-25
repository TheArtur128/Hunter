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
        memory.append(self)
        self.name = name
        self.x = x
        self.y = y

    #Красиво упакованные данные для функции pygame'a для прорисовки
    def drawing_data(self):
        return [self.img[str(self.vector)], (self.x, self.y)]

    def __repr__(self):
        return f"#{self.name}"


class Weapon(Primitive):
    def __init__(self, name, img, damage=10, speed=FPS, x=0, y=0, vector=1, master=None):
        super().__init__(name, x, y)
        #Атрибуты описывающие оружие непосредственно
        self.damage = damage
        self.speed = speed
        #Ссылка на персонажа держущего оружие
        self.master = master
        #Атрибуты действия
        self.action = [self.__class__.speed, 0, 0]
        #Положение
        self.vector = vector
        #Штраф при расположении под углом
        self.coordinates = self.default_coordinates()
        #Графическая чать оружия
        self.img = self.__class__.img

    def __update_coordinates(self):
        if self.master is not None:
            self.vector = self.master.vector + self.action[1]
            self.vector = check_vector(self.vector)
            self.x = self.master.x + self.coordinates[self.vector-1][0]
            self.y = self.master.y + self.coordinates[self.vector-1][1]

    @staticmethod
    def default_coordinates():
        '''Штраф распоожения для векторов. Первый индекс штрафа
        равняеться положению 1 (up), последний (7) равен вектору "left-up" (8)'''
        return [[81, 8], [38, 48], [-8, 81], [-25, 35], [-5, 8], [-5, -27], [8, -5], [45, -15]]

    def verification(self):
        self.__update_coordinates()


class Katana(Weapon):
    img = katana_image
    #TO DO...
    with open(f"{folder_root}/material/sound/Steel-arms-voiced.ogg", "rb") as file:
        light_hitting_sound = pygame.mixer.Sound(file.read())
    speed = FPS // 10
    def __init__(self, name="katana", damage=10, speed=speed, x=0, y=0, vector=1, master=None):
        super().__init__(name, katana_image, damage, speed, x, y, vector, master)


#Персонажи как класс
class Hunter(Primitive):
    def __init__(self, name, x, y, health=100, vector=1):
        self.img = cricle_image
        self.health = health
        self.__speed = 5
        super().__init__(name, x, y)
        self.__size = 81
        self.vector = vector
        self.action = "calmness"
        self.movement = {
            "left": [False, random_pole()],
            "right": [False, random_pole()],
            "up": [False, random_pole()],
            "down": [False, random_pole()]
        }
        self.weapon = Katana(master=self)

    def __attack(self):
        if self.weapon is not None:
            #Уменьшаем счётчик до момента удара
            self.weapon.action[0] -= 1
            if self.weapon.action[0] <= 0:
                #При первой итерации удара включаем звук удара
                if self.weapon.action[2] == 0:
                    self.weapon.__class__.light_hitting_sound.play()
                self.weapon.action[0] = self.weapon.__class__.speed #Обновляем счётчик до следуещего удара
                self.weapon.action[1] -= 1 #перемещаем оружие
                self.weapon.action[2] += 1 #Устанавливаем точное кол. итераций

                #Завершаем удар
                if self.weapon.action[2] > 3:
                    self.weapon.__class__.light_hitting_sound.stop()
                    #Ставим атрибуты на свои места
                    self.weapon.action[1] = 0
                    self.weapon.action[2] = 0
                    self.weapon.coordinates = self.weapon.default_coordinates()
                    #Убираем состояние атаки и также убираем вызов метода
                    self.action = "calmness"

        self.weapon.vector = check_vector(self.weapon.vector)

    def verification(self):
        #Вызываем функию состояния
        if self.action == "attack":
            self.__attack()

        #Движение
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
            if self.x + self.size < window_dimensions[0]:
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
            if self.y + self.size < window_dimensions[1]:
                self.y += self.speed
            if not vector_ban:
                if self.vector == 1:
                    self.vector += self.movement["down"][1]
                elif self.vector in [2, 3, 4]:
                    self.vector += 1
                elif self.vector in [6, 7, 8]:
                    self.vector -= 1

        self.vector = check_vector(self.vector)

    @property
    def speed(self): return self.__speed
    @property
    def size(self): return self.__size

#Сущность которой мы можем управлять
Hero = Hunter("Arthur", 200, 200)

print(memory)

#Главный цикл
world_is_life = True
while world_is_life:
    clock.tick(FPS)

    for action in pygame.event.get():
        if action.type == pygame.QUIT:
            world_is_life = False

        if action.type == pygame.MOUSEBUTTONDOWN:
            if action.button == 1:
                if Hero.action != "attack":
                    Hero.action = "attack"

        if action.type == pygame.KEYDOWN:
            if action.key == pygame.K_z:
                if Hero.action != "attack":
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

    #Рисуем
    app.blit(fone_image["one"], (0, 0))

    #Работа с хранилищем
    for item in memory:
        item.verification() #Для каждого обьекта проводим его личную проверку
        app.blit(*item.drawing_data()) #Рисуем обькт из упакованных данных

    pygame.display.update()
