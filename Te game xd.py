
import arcade
import math
from arcade.experimental.lights import Light, LightLayer
import random


SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 960
SCREEN_TITLE = "crackrooms"
RIGHT_FACING = 0
LEFT_FACING = 1
CHARACTER_SCALING = 0.4
CURSOR_SCALING = 0.2
PLAYER_MOVEMENT_SPEED = 3
AMBIENT_COLOR = (0, 0, 0)
TILE_SCALING = 0.4
SPRINT_SPEED = 2
SPRITE_SPEED = 3


def load_texture_pair(filename):
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True),
    ]


class PlayerCharacter(arcade.Sprite):

    """ Player Sprite"""

    def __init__(self, **kwargs):
        super().__init__()
        self.character_face_direction = RIGHT_FACING
        self.cur_texture = 0
        self.scale = CHARACTER_SCALING
        self.idle_texture_pair = load_texture_pair(f"./legs/idle.png")
        self.stamina = 100

        self.walk_textures = []
        for i in range(14):
            for j in range(6):
                texture = load_texture_pair(f"./legs/legs_{i}.png")
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
        self.stamina += 0.1
        if self.stamina > 100:
            self.stamina
        self.update_animation()


    def on_draw(self):
        return
        
class Faceling(arcade.Sprite):

    def follow_sprite(self, player_sprite):
        if self.center_y < player_sprite.center_y:
            self.center_y += min(SPRITE_SPEED, player_sprite.center_y - self.center_y)
        elif self.center_y > player_sprite.center_y:
            self.center_y -= min(SPRITE_SPEED, self.center_y - player_sprite.center_y)

        if self.center_x < player_sprite.center_x:
            self.center_x += min(SPRITE_SPEED,player_sprite.center_x - self.center_x)
        elif self.center_x > player_sprite.center_x:
            self.center_x -= min(SPRITE_SPEED, self.center_x - player_sprite.center_x)
    


class MyGame(arcade.Window):
    def __init__(self, width, height, title):

        super().__init__(width, height, title,)
        
        self.player_list = None
        self.faceling_list = None
        self.torso_list = None
        self.torso_sprite = None
        self.faceling_sprite = None
        self.cursor_list = None
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.shift_pressed = False
        self.light_layer = None
        self.player_light = None
        self.sprinting = False
        self.scene = None
        self.physics = None
        self.camera = None
        self.HUD_camera = None
        self.sprint_bar = None
        

        arcade.set_background_color(arcade.color_from_hex_string("#7b692f"))


    def setup(self):

        layer_options = {
            "spawn": {"custom_class":PlayerCharacter, "custom_class_args": {}}
        }
        tile_map = arcade.load_tilemap("Level 4 assets\lvl4.tmx", TILE_SCALING,layer_options=layer_options)
        
        self.scene = arcade.Scene.from_tilemap(tile_map)
        self.player_list = arcade.SpriteList()
        self.faceling_list = arcade.SpriteList()
        self.scene.add_sprite_list('player_list')
        self.scene.add_sprite_list('torso_list')
        self.scene.add_sprite_list('faceling_list')
        self.cursor_list = arcade.SpriteList()
        faceling = (f"./assets/faceling.png")
        self.faceling_sprite = Faceling(faceling, CHARACTER_SCALING)
        self.faceling_sprite.center_x = 512
        self.faceling_sprite.center_y = 512
        self.faceling_list.append(self.faceling_sprite)
        self.scene['faceling_list'].append(self.faceling_sprite)
        torso = (f"./assets/dude.png")
        self.torso_sprite = arcade.Sprite(torso, CHARACTER_SCALING)
        self.scene['torso_list'].append(self.torso_sprite)
        self.torso_sprite.angle = 180
        cursor = (f"./assets/cursor.png")
        self.cursor_sprite = arcade.Sprite(cursor, CURSOR_SCALING)
        self.cursor_list.append(self.cursor_sprite)
        self.player_sprite = self.scene['spawn'][0]
        self.scene['player_list'].append(self.player_sprite)
        self.set_mouse_visible(False)
        self.light_layer = LightLayer(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite, walls=self.scene["walls"])
        self.faceling_physics_engine = arcade.PhysicsEngineSimple(self.faceling_sprite, walls=self.scene["walls"])
        

        self.camera = arcade.Camera(self.width, self.height)
        self.HUD_camera = arcade.Camera(self.width, self.height)

        for sprite in self.scene['lights']:
            light = Light(sprite.center_x , sprite.center_y , sprite.properties['radius'], color=sprite.properties['color'][:3], mode='soft')
            self.light_layer.add(light)

        radius = 300
        mode = 'soft'
        color = arcade.color_from_hex_string("#363636")
        self.player_light = Light(self.torso_sprite.center_x, self.torso_sprite.center_y, radius, color, mode)
        self.light_layer.add(self.player_light)
        self.sprint_bar= arcade.SpriteList()

        
    def on_draw(self):
        
        self.clear()

        self.camera.use()
        with self.light_layer:
            self.clear()
            self.scene.draw()
        
        self.light_layer.draw(ambient_color=AMBIENT_COLOR)
        
        self.HUD_camera.use()
        self.sprint_bar.draw()
        self.cursor_list.draw()
        
        self.HUD_camera.use()
        self.sprint_bar.draw()




        arcade.draw_lrtb_rectangle_filled(0, SCREEN_WIDTH*self.player_sprite.stamina/100, 20, 0, arcade.color.BABY_BLUE)

    def on_resize(self, width, height):
        self.light_layer.resize(width, height)
        
    def process_keychange(self):
        angle = 0
        sprint_speed = SPRINT_SPEED

        if self.player_sprite.stamina <= 10:
            sprint_speed = 0
        
        if self.up_pressed and not self.down_pressed:
            self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED + sprint_speed * self.sprinting
            self.player_sprite.angle = 90
        elif self.down_pressed and not self.up_pressed:
            self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED + -sprint_speed * self.sprinting
            self.player_sprite.angle = -90
        else:
            self.player_sprite.change_y = 0
        if self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED + sprint_speed * self.sprinting
            self.player_sprite.angle = 0
        elif self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED + -sprint_speed * self.sprinting
            self.player_sprite.angle = 0
        else:
            self.player_sprite.change_x = 0


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
<<<<<<< HEAD

=======
    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        print (self.camera.position.x + self._mouse_x ,self.camera.position.y + self._mouse_y)
>>>>>>> 2a55440902f04ee9bbe451034ef72f1e2e6ccbc3
    def center_camera_to_player(self):

        screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)

        screen_center_y = self.player_sprite.center_y - (

            self.camera.viewport_height / 2

        )
        player_centered = screen_center_x, screen_center_y
        self.camera.move_to(player_centered)

    def on_update(self, delta_time):
        self.center_camera_to_player()

        self.torso_sprite.center_x = self.player_sprite.center_x
        self.torso_sprite.center_y = self.player_sprite.center_y
        self.torso_sprite.update()
        self.faceling_sprite.update()
<<<<<<< HEAD
        for faceling_sprite in self.faceling_list:
            faceling_sprite.follow_sprite(self.player_sprite)
=======
        #for faceling_sprite in self.faceling_list:
           # faceling_sprite.follow_sprite(self.player_sprite)
>>>>>>> 2a55440902f04ee9bbe451034ef72f1e2e6ccbc3
        self.player_sprite.update(delta_time)


        self.cursor_sprite.center_x = self._mouse_x 
        self.cursor_sprite.center_y = self._mouse_y

        self.faceling_physics_engine.update()
        
        start_x = self.torso_sprite.center_x
        start_y = self.torso_sprite.center_y
        dest_x = self.camera.position.x + self._mouse_x
        dest_y = self.camera.position.y + self._mouse_y
        x_diff = dest_x - start_x
        y_diff = dest_y - start_y
        angle = math.atan2(y_diff, x_diff)
        self.torso_sprite.angle = math.degrees(angle) - 90
<<<<<<< HEAD
        print(f"{start_x=} {start_y=} {dest_x=} {dest_y=} {self.camera.position.x=} {self.camera.position.y=} {angle=}")
=======
>>>>>>> 2a55440902f04ee9bbe451034ef72f1e2e6ccbc3
 

        for enemy in self.faceling_list:
            start_x = self.faceling_sprite.center_x
            start_y = self.faceling_sprite.center_y
            dest_x = self.torso_sprite.center_x
            dest_y = self.torso_sprite.center_y
            x_diff = dest_x - start_x
            y_diff = dest_y - start_y
            angle = math.atan2(y_diff, x_diff)
            self.faceling_sprite.angle = math.degrees(angle) - 90
        
        self.player_light.position = self.torso_sprite.position

        self.physics_engine.update()

def main():

    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
