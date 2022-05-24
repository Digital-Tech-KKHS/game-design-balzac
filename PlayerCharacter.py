import arcade
from constants import *


#-=our player class, everything relating to the player will go here=-
class PlayerCharacter(arcade.Sprite):

    """ Player Sprite"""

    def __init__(self, **kwargs):
        super().__init__()
        self.character_face_direction = RIGHT_FACING
        self.cur_texture = 0
        self.scale = CHARACTER_SCALING
        self.idle_texture_pair = arcade.load_texture_pair(f"./legs/idle.png")
        self.stamina = 100
        self.sprinting = False
        self.resting = False

        self.walk_textures = []
        for i in range(14):
            for j in range(6):
                texture = arcade.load_texture_pair(f"./legs/legs_{i}.png")
                self.walk_textures.append(texture)

        self.texture = self.idle_texture_pair[0]

    def update_animation(self, delta_time: float = 1 / 60):

        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING
        if self.change_y != 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING
        if self.change_y != 0 and self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING



        elif self.change_x == 0:
            self.texture = self.idle_texture_pair[self.character_face_direction]

        elif self.change_y == 0:
            self.texture = self.idle_texture_pair[self.character_face_direction]

        if self.change_x or self.change_y != 0:
            self.cur_texture += 1
            if self.cur_texture > len(self.walk_textures) - 1:
                self.cur_texture = 0
            self.texture = self.walk_textures[self.cur_texture][
                self.character_face_direction
            ]

        return

    def update(self, dt):
        self.center_x += self.change_x
        self.center_y += self.change_y
        self.set_hit_box((-20, -20), (-20, 20), (20, -20), (20, 20))

        # test to see if the player is walking or standing still
        if not (self.change_x or self.change_y):
            self.stamina += 0.2
        elif not self.sprinting:
            self.stamina += 0.1
        else:
            self.stamina -= 0.4

        if self.stamina >= 100:
            self.stamina = 100
            self.resting = False

        # make sure stamina bar has some width
        if self.stamina <= 1/20:
            self.resting = True
            self.sprinting = False

        self.update_animation()


    def on_draw(self):
        return