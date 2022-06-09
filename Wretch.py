import arcade
import math
import random
from constants import *

class Wretch(arcade.Sprite):
    def __init__(self, x, y):
        img = (f"./assets/wretch.png")
        super().__init__(img, CHARACTER_SCALING)
        self.center_x = x
        self.center_y = y
        self.destination_look = 0
        self.turn_threshold = 0.1

    def follow_sprite(self, player_sprite):
        if self.center_y < player_sprite.center_y:
            self.center_y += min(SPRITE_SPEED, player_sprite.center_y - self.center_y)
        elif self.center_y > player_sprite.center_y:
            self.center_y -= min(SPRITE_SPEED, self.center_y - player_sprite.center_y)

        if self.center_x < player_sprite.center_x:
            self.center_x += min(SPRITE_SPEED,player_sprite.center_x - self.center_x)
        elif self.center_x > player_sprite.center_x:
            self.center_x -= min(SPRITE_SPEED, self.center_x - player_sprite.center_x)
<<<<<<< HEAD


    def random_look(self):
=======
    def random_look(self):

>>>>>>> b52559b5dc626636182909017d0cdb2473ec6ec9
        if abs(self.angle - self.destination_look) < self.turn_threshold:
            self.destination_look = +- random.randrange(360)
        self.angle = arcade.utils.lerp(self.angle, self.destination_look, 0.1)

    def random_move(self):
        self.random_look()
        self.center_x += 2 * math.cos(math.radians(self.angle + 90))
        self.center_y += 2 * math.sin(math.radians(self.angle + 90))
<<<<<<< HEAD

            
        
=======
>>>>>>> b52559b5dc626636182909017d0cdb2473ec6ec9
