# -*- coding: utf-8 -*-
from charbot_rust import Game

from PIL import Image

game = Game.expert()
game.reveal()
game.quit()
base_bytes, size = game.draw()

img = Image.frombytes("RGB", size, bytes(base_bytes))

img.show()

"""disp = game.display_test()

img = Image.frombytes("RGB", (300, 300), bytes(disp))
img.show()"""
