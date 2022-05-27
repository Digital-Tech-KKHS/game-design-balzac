
import arcade
import math
from arcade.experimental.lights import Light, LightLayer
import random
from PlayerCharacter import PlayerCharacter
from constants import *
from Enemy import Enemy
from EnemyFactroy import enemy_factory

#-=loading our texture pair=-
def load_texture_pair(filename):
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True),
    ]

class MyGame(arcade.Window):
    def __init__(self, width, height, title):

        super().__init__(width, height, title,)
        
        self.player_list = None
        self.enemy_list = None
        self.torso_list = None
        self.torso_sprite = None
        self.cursor_list = None
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.shift_pressed = False
        self.light_layer = None
        self.player_light = None
        self.scene = None
        self.physics = None
        self.camera = None
        self.HUD_camera = None
        self.sprint_bar = None
        

        arcade.set_background_color(arcade.color_from_hex_string("#7b692f"))


    def setup(self):
        layer_options = {
            "spawn": {"custom_class": PlayerCharacter, "custom_class_args": {}}, 
            "walls": {"use_spatial_hash": True},
        }

        tile_map = arcade.load_tilemap("Level 4 assets\lvl4.tmx", TILE_SCALING, layer_options=layer_options)
        self.scene = arcade.Scene.from_tilemap(tile_map)
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.scene.add_sprite_list('player_list')
        self.scene.add_sprite_list('torso_list')
        self.scene.add_sprite_list('enemy_list')
        self.cursor_list = arcade.SpriteList()

        for spawn_point in self.scene['enemy_spawn']:
            self.scene['enemy_list'].append(enemy_factory(spawn_point))

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
        self.enemy_physics_engine = arcade.PhysicsEngineSimple(self.scene["enemy_list"][0], walls=self.scene["walls"])
        self.enemy_physics_engine_secrets = arcade.PhysicsEngineSimple(self.scene["enemy_list"][0], walls=self.scene["secrets"])
        

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

        
    def on_draw(self):
        
        self.clear()

        self.camera.use()
        with self.light_layer:
            self.clear()
            self.scene.draw()
        
        self.light_layer.draw(ambient_color=AMBIENT_COLOR)
        
        self.HUD_camera.use()
        self.cursor_list.draw()

        sprint_bar_color = arcade.color.BABY_BLUE
        if self.player_sprite.resting:
            sprint_bar_color = arcade.color.LIGHT_RED_OCHRE
        arcade.draw_lrtb_rectangle_filled(0, 20, 100+ (SCREEN_HEIGHT-600) *self.player_sprite.stamina/100, 0, sprint_bar_color)
        
        self.camera.use()
        for enemy in self.enemy_list:
            if arcade.has_line_of_sight(self.player_sprite.position , enemy.position , self.scene["walls"]):

                color = arcade.color.RED
            else:
                color = arcade.color.WHITE
            arcade.draw_line(self.player_sprite.center_x,
                                self.player_sprite.center_y,
                                enemy.center_x,
                                enemy.center_y,
                                color,
                                2)



    def on_resize(self, width, height):
        self.light_layer.resize(width, height)
        
    def process_keychange(self):
        angle = 0
        sprint_speed = SPRINT_SPEED

        if self.player_sprite.resting:
            self.player_sprite.sprinting = False
        
        if self.up_pressed and not self.down_pressed:
            self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED + sprint_speed * self.player_sprite.sprinting
            self.player_sprite.angle = 90
        elif self.down_pressed and not self.up_pressed:
            self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED + -sprint_speed * self.player_sprite.sprinting
            self.player_sprite.angle = -90
        else:
            self.player_sprite.change_y = 0
        if self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED + sprint_speed * self.player_sprite.sprinting
            self.player_sprite.angle = 0
        elif self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED + -sprint_speed * self.player_sprite.sprinting
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
        
        # bitwise and of modifier keys. See https://api.arcade.academy/en/latest/keyboard.html#keyboard-modifiers 
        self.player_sprite.sprinting = modifiers and arcade.key.MOD_SHIFT
        
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
        
        # bitwise and of modifier keys. See https://api.arcade.academy/en/latest/keyboard.html#keyboard-modifiers 
        self.player_sprite.sprinting = modifiers and arcade.key.MOD_SHIFT

        self.process_keychange()
    
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
        self.player_sprite.update(delta_time)


        self.cursor_sprite.center_x = self._mouse_x 
        self.cursor_sprite.center_y = self._mouse_y

        self.enemy_physics_engine.update()
        self.enemy_physics_engine_secrets.update()
        
        start_x = self.torso_sprite.center_x
        start_y = self.torso_sprite.center_y
        dest_x = self.camera.position.x + self._mouse_x
        dest_y = self.camera.position.y + self._mouse_y
        x_diff = dest_x - start_x
        y_diff = dest_y - start_y
        angle = math.atan2(y_diff, x_diff)
        self.torso_sprite.angle = math.degrees(angle) - 90
 

        for enemy in self.scene['enemy_list']:
            start_x = enemy.center_x
            start_y = enemy.center_y
            dest_x = self.torso_sprite.center_x
            dest_y = self.torso_sprite.center_y
            x_diff = dest_x - start_x
            y_diff = dest_y - start_y
            angle = math.atan2(y_diff, x_diff)
            enemy.angle = math.degrees(angle) - 90
        
        self.player_light.position = self.torso_sprite.position

        self.physics_engine.update()

def main():

    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()