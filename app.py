from classes import *

App(
    app_win,
    pygame.image.load(f"{folder_root}\material\general\graphix\icon.ico"),
    "Hunter",
    f"{folder_root}/material/general/soundtracks/tougenkyou alien.mp3",
    FPS,
    time_to_exit
).run()
