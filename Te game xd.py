from re import X
from tkinter import Y
import arcade
import math
from arcade.experimental.lights import Light, LightLayer

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 960
SCREEN_TITLE = "crackrooms"
RIGHT_FACING = 0
LEFT_FACING = 1
CHARACTER_SCALING = 0.4
CURSOR_SCALING = 0.2
PLAYER_MOVEMENT_SPEED = 7
AMBIENT_COLOR = (1, 1, 1)

SPRINT_SPEED = 3



def load_texture_pair(filename):
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True),
    ]

class Lights(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__("Level 0 assets\Flourescent lights.png", center_x=x, center_y=y)
        x = 100
        y = 200
        radius = 500
        mode = 'soft'
        color = arcade.csscolor.GRAY
        light = Light(x, y, radius, color, mode)
        self.light_layer.add(light)


class PlayerCharacter(arcade.Sprite):

    """ Player Sprite"""

    def __init__(self):
        super().__init__()
        self.character_face_direction = RIGHT_FACING
        self.cur_texture = 0
        self.scale = CHARACTER_SCALING
        self.idle_texture_pair = load_texture_pair(f"./legs/idle.png")

        self.walk_textures = []
        for i in range(14):
            for j in range(5):
                texture = load_texture_pair(f"./legs/legs_{i}.png")
                self.walk_textures.append(texture)

        self.texture = self.idle_texture_pair[0]

    def update_animation(self, delta_time: float = 1 / 60):

        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING
        if self.change_y < 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING
        elif self.change_y > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        elif self.change_x == 0:
            self.texture = self.idle_texture_pair[self.character_face_direction]

        elif self.change_y == 0:
            self.texture = self.idle_texture_pair[self.character_face_direction]

        if self.change_x != 0:
            self.cur_texture += 1
            if self.cur_texture > len(self.walk_textures) - 1:
                self.cur_texture = 0
            self.texture = self.walk_textures[self.cur_texture][
                self.character_face_direction
            ]
        if self.change_y != 0:
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

        self.update_animation()
        
class Enemy(arcade.Sprite):
    def __init__(self):
        super().__init__()
        self.scale = CHARACTER_SCALING
    
    


class MyGame(arcade.Window):
    def __init__(self, width, height, title):

        super().__init__(width, height, title,)
        
    
        self.player_list = None
        self.enemy_list = None
        self.legs_list = None
        self.player_sprite = None
        self.enemy_sprite = None
        self.cursor_list = None
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.shift_pressed = False
        self.light_layer = None
        self.player_light = None
        self.sprinting = False

        arcade.set_background_color(arcade.color_from_hex_string("#7b692f"))

    def setup(self):

        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.cursor_list = arcade.SpriteList()
        self.legs_list = arcade.SpriteList()
        self.floor = arcade.load_texture("floor.png")
        player = "dude.png"
        
        enemy = "faceling.png"
        self.enemy_sprite = arcade.Sprite(enemy, CHARACTER_SCALING)
        self.enemy_sprite.center_x = 320
        self.enemy_sprite.center_y = 240
        self.enemy_list.append(self.enemy_sprite)
        
        self.player_sprite = arcade.Sprite(player, CHARACTER_SCALING)
        self.player_sprite.center_x = 320
        self.player_sprite.center_y = 240
        self.player_list.append(self.player_sprite)
        self.player_sprite.angle = 180
        cursor = "cursor.png"
        self.cursor_sprite = arcade.Sprite(cursor, CURSOR_SCALING)
        self.cursor_list.append(self.cursor_sprite)
        self.legs_sprite = PlayerCharacter()
        self.legs_sprite.center_x = self.player_sprite.center_x
        self.legs_sprite.center_y = self.player_sprite.center_y
        self.legs_list.append(self.legs_sprite)
        self.set_mouse_visible(False)

        self.light_layer = LightLayer(SCREEN_WIDTH, SCREEN_HEIGHT)

        x = 100
        y = 200
        radius = 500
        mode = 'soft'
        color = arcade.csscolor.GRAY
        light = Light(x, y, radius, color, mode)
        self.light_layer.add(light)

        radius = 300
        mode = 'soft'
        color = arcade.color_from_hex_string("#363636")
        self.player_light = Light(self.player_sprite.center_x, self.player_sprite.center_y, radius, color, mode)
        self.light_layer.add(self.player_light)

    def on_draw(self):

        self.clear()
        self.legs_list.draw()
        self.player_list.draw()
        self.enemy_list.draw()

        with self.light_layer:
            self.clear()
            arcade.draw_lrwh_rectangle_textured(0,0,1280,960,self.floor)
            self.legs_list.draw()
            self.player_list.draw()
            self.enemy_list.draw()

        self.light_layer.draw(ambient_color=AMBIENT_COLOR)
        self.cursor_list.draw()
        

    def on_resize(self, width, height):
        self.light_layer.resize(width, height)
        
    def process_keychange(self):
        angle = 0
        
        if self.up_pressed and not self.down_pressed:
            self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED + SPRINT_SPEED * self.sprinting
            self.legs_sprite.change_y = PLAYER_MOVEMENT_SPEED + SPRINT_SPEED * self.sprinting
            self.legs_sprite.angle = 90
        elif self.down_pressed and not self.up_pressed:
            self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED + -SPRINT_SPEED * self.sprinting
            self.legs_sprite.change_y = -PLAYER_MOVEMENT_SPEED + -SPRINT_SPEED * self.sprinting
            self.legs_sprite.angle = -90
        else:
            self.player_sprite.change_y = 0
            self.legs_sprite.change_y = 0
        if self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED + SPRINT_SPEED * self.sprinting
            self.legs_sprite.change_x = PLAYER_MOVEMENT_SPEED + SPRINT_SPEED * self.sprinting
            self.legs_sprite.angle = 0
        elif self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED + -SPRINT_SPEED * self.sprinting
            self.legs_sprite.change_x = -PLAYER_MOVEMENT_SPEED + -SPRINT_SPEED * self.sprinting
            self.legs_sprite.angle = 0
        

        else:
            self.player_sprite.change_x = 0
            self.legs_sprite.change_x = 0

    def on_key_press(self, key, modifiers):
        if key == arcade.key.W:
            self.up_pressed = True
        elif key == arcade.key.S:
            self.down_pressed = True
        elif key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.D:
            self.right_pressed = True
        
        self.sprinting = modifiers and arcade.key.MOD_SHIFT
        
        self.process_keychange()
        if key == arcade.key.SPACE:
            if self.player_light in self.light_layer:
                self.light_layer.remove(self.player_light)
            else:
                self.light_layer.add(self.player_light)

    def on_key_release(self, key, modifiers):
        if key == arcade.key.W:
            self.up_pressed = False
        if key == arcade.key.S:
            self.down_pressed = False
        elif key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.D:
            self.right_pressed = False
        
        self.sprinting = modifiers and arcade.key.MOD_SHIFT

        self.process_keychange()
 
    def on_update(self, delta_time):
        self.set_viewport(self.legs_sprite.center_x - SCREEN_WIDTH/2, self.legs_sprite.center_x + SCREEN_WIDTH/2,
                          self.legs_sprite.center_y - SCREEN_HEIGHT/2, self.legs_sprite.center_y + SCREEN_HEIGHT/2)
        self.player_sprite.update()
        self.enemy_sprite.update()
        self.cursor_sprite.update()
        self.legs_sprite.update(delta_time)
        self.cursor_sprite.center_x = self._mouse_x + self.get_viewport()[0]
        self.cursor_sprite.center_y = self._mouse_y + self.get_viewport()[2]
        for player in self.player_list:
            start_x = self.player_sprite.center_x
            start_y = self.player_sprite.center_y
            dest_x = self.cursor_sprite.center_x
            dest_y = self.cursor_sprite.center_y
            x_diff = dest_x - start_x
            y_diff = dest_y - start_y
            angle = math.atan2(y_diff, x_diff)
            self.player_sprite.angle = math.degrees(angle) - 90

        for emeny in self.enemy_list:
            start_x = self.enemy_sprite.center_x
            start_y = self.enemy_sprite.center_y
            dest_x = self.player_sprite.center_x
            dest_y = self.player_sprite.center_y
            x_diff = dest_x - start_x
            y_diff = dest_y - start_y
            angle = math.atan2(y_diff, x_diff)
            self.enemy_sprite.angle = math.degrees(angle) - 90

        self.player_light.position = self.player_sprite.position


def main():

    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
