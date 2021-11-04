from classes import *


def set_game_scene():
    pygame.mixer.music.play(loops=-1)
    pygame.mixer.music.set_volume(0.5)

    global exit
    exit = False

    global time_to_exit
    time_to_exit = FPS * settings["seconds_to_exit"]

    for class_ in presence_in_inheritance(Primitive, "memory"):
        class_.memory = []

    #Сущность которой мы будем управлять
    global Hero
    Hero = Player("Main Hero", tithe_win[0]*settings["factor_of_camera_width"], app_win[1]//2 - 40, speed=7, vector=3)

    Opponent.sum_all = 0
    Opponent.level = 1
    Opponent.score_for_next_level = -1
    Opponent(app_win[0] - tithe_win[0]*settings["factor_of_camera_width"] - 80, app_win[1]//2 - 40, vector=7)

    GameZone(x=-plays_area[0]//2, y=-plays_area[1]//2, width=plays_area[0], height=plays_area[1])
    Camera(
        x=(app_win[0]-camera_area["width"])//2,
        y=(app_win[1]-camera_area["height"])//2,
        width=camera_area["width"],
        height=camera_area["height"],
        master=Hero
    )

    if settings["hud"]:
        Score(x=20, y=40, text="", movable=False, eternal=True, master=Hero)
        LevelOfOpponent(x=app_win[0]-185, y=15, text="", movable=False, eternal=True)
        SelectedWeaponsIndex(x=20, y=15, text="", movable=False, eternal=True, master=Hero)

    if settings["plants"]: Plants.initialize_instances()


draw_queue = [Abstraction, Static, GameplayEntity, Hud]
log = []

app = pygame.display.set_mode(app_win)
icon = pygame.image.load(f"{folder_root}\material\general\graphix\icon.ico")
pygame.display.set_icon(icon)
pygame.display.set_caption("Lonely Hunter")
pygame.mixer.music.load(f"{folder_root}/material/general/soundtracks/tougenkyou alien.mp3")
clock = pygame.time.Clock()

#Создаём отделную, прозрачную поверхность для паузы
veil = pygame.Surface(app_win)
veil.set_alpha(132)
veil.fill((255, 255, 255))
veil.blit(pygame.font.Font(f"{folder_root}/material/general/fonts/{settings['font']}", 80).render("Pause", False, color["text"]), (210, 150))

set_game_scene()

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
                if action.button == 3:
                    Hero.action = "dash"

            if action.type == pygame.KEYDOWN:
                if action.key in key["player"]["ATTACK"]:
                    Hero.action = "chop"

                if action.key in key["player"]["PAUSE"]:
                    if time:
                        time = False
                        pygame.mixer.music.pause()
                    else:
                        time = True
                        pygame.mixer.music.unpause()

                if action.key in key["player"]["RUSH"]:
                    Hero.action = "dash"

                if action.key in key["player"]["WEAPON_CHANGE"]:
                    Hero.action = "weapon-change"

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
        else:
            if action.type == pygame.KEYDOWN:
                if action.key in key["menu"]["AGAIN"]:
                    set_game_scene()

    app.fill((color["emptiness_of_map"]))

    #Самоличностные вычисления
    for item in Primitive.memory:
        if time:
            try:
                item.verification()
            except Exception as error:
                if debug_mode and not exit:
                    try: log.append(f"from verification, {item}: {type(error)} {error}")
                    except AttributeError: log.append(f"from verification: {type(error)} {error}")

    #Рендер
    for class_ in draw_queue:
        for item in class_.memory:
            try:
                item.draw(app)
                if debug_mode and item.__class__ in presence_in_inheritance(GameplayEntity):
                    for hitbox in item.hitbox:
                        pygame.draw.rect(app, color["debug_mode"], (hitbox[0], hitbox[1], 1, 1))
            except Exception as error:
                if debug_mode and not exit:
                    try: log.append(f"from draw, {item}: {type(error)} {error}")
                    except AttributeError: log.append(f"from draw: {type(error)} {error}")

    if not time:
        app.blit(veil, (0, 0))

    if (exit and time_to_exit) or not Hero in Primitive.memory:
        if debug_mode: print(f"{round(time_to_exit/FPS, 2)} seconds left until the game closes")
        app.blit(pygame.font.Font(f"{folder_root}/material/general/fonts/{settings['font']}", 80).render("The End", True, color["text"]), (176, 150))
        app.blit(pygame.font.Font(f"{folder_root}/material/general/fonts/{settings['font']}", 21).render("Again?", True, color["text"]), (285, 235))
        time_to_exit -= 1
        if time_to_exit <= 0:
            game = False

    pygame.display.update()


if debug_mode:
    print(f"\nGameplayEntity.memory has {len(GameplayEntity.memory)} objects: {GameplayEntity.memory}\nHud.memory has {len(Hud.memory)} objects: {Hud.memory}\nStatic.memory has {len(Static.memory)} objects: {Static.memory}")
    print(f"\nEXCLUSION ZONE, {len(log)} errors")
    for error in log:
        print(error)
