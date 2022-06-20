
import arcade
import math
import arcade.gui
from arcade.experimental.lights import Light, LightLayer
import random
from PlayerCharacter import PlayerCharacter
from constants import *
from Enemy import Enemy
from EnemyFactory import enemy_factory

#-=loading our texture pair=-
def load_texture_pair(filename):
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True),
    ]

    
class QuitButton(arcade.gui.UIFlatButton):
    def on_click(self, event: arcade.gui.UIOnClickEvent):
        arcade.exit()


class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.background = None
        self.text = "Level.Null()"
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.v_box = arcade.gui.UIBoxLayout()
        start_button = arcade.gui.UIFlatButton(text="Start Game", width=150)
        self.v_box.add(start_button.with_space_around(bottom=20))
        quit_button = QuitButton(text="Quit", width=150)
        self.v_box.add(quit_button)
        start_button.on_click = self.on_click_start


        # Create a widget to hold the v_box widget, that will center the buttons
        self.manager.add(
            arcade.gui.UIAnchorWidget(
                allign_x=SCREEN_WIDTH/2,
                allign_y=SCREEN_HEIGHT/2 - 400,
                child=self.v_box)
        )

    def setup(self):
        self.window.set_mouse_visible(True)

    def on_click_start(self, event):
        print("Start:", event)
        self.window.show_view(self.game_view)

    

    def on_show_view(self):
        self.background = arcade.load_texture("assets\menu.png")
        self.game_view = MyGame()
        self.game_view.setup()

    def on_draw(self):
        self.clear()
        
        arcade.draw_lrwh_rectangle_textured(0, 0,
                                            SCREEN_WIDTH, SCREEN_HEIGHT,
                                            self.background)
        arcade.draw_text(self.text, SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 150, arcade.color.WHITE, font_size=56, font_name = 'Kenney Pixel', anchor_x="center")
        self.manager.draw()
    
        

class LoseView(arcade.View):
    def __init__(self):
        super().__init__()
        self.text = "Game Over"
        self.background = None

    def on_show_view(self):
        self.background = arcade.load_texture("assets\SPOOKY GAME OVER.png")
        self.game_view = MyGame()
        self.game_view.setup()

    def on_draw(self):
        self.clear()
        arcade.draw_lrwh_rectangle_textured(0, 0,
                                            SCREEN_WIDTH, SCREEN_HEIGHT,
                                            self.background)
        arcade.draw_text(self.text, SCREEN_WIDTH/2, SCREEN_HEIGHT/2, arcade.color.WHITE, font_size=30, anchor_x="center")
        

    def on_mouse_press(self, _x,  _y, _button, _modifiers):
        self.window.show_view(self.game_view)


    

class MyGame(arcade.View):
    def __init__(self):

        super().__init__()

        self.obj_alpha = 0
        self.text_alpha = 255
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
        self.sprintbarback = None
        self.sprintbarfore = None
        enemy_physics_engine = 0
        self.level = 3

        self.subtitle = None
        self.facesound = arcade.load_sound("assets\sounds\gacelingsound.mp3")
        self.lvl1mus = arcade.load_sound("assets\sounds\Level.Null.mp3")
        arcade.set_background_color(arcade.color_from_hex_string("#7b692f"))


    def setup(self):
        layer_options = {
            "spawn": {"custom_class": PlayerCharacter, "custom_class_args": {}}, 
            "walls": {"use_spatial_hash": True},
            "floor": {"use_spatial_hash": True},
            "details": {"use_spatial_hash": True},
            "lights": {"use_spatial_hash": True},
        }

        tile_map = arcade.load_tilemap(f"Level {self.level} assets\lvl{self.level}.tmx", TILE_SCALING, layer_options=layer_options)
        self.scene = arcade.Scene.from_tilemap(tile_map)
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.scene.add_sprite_list('player_list')
        self.scene.add_sprite_list('torso_list')
        self.scene.add_sprite_list('enemy_list')
        self.cursor_list = arcade.SpriteList()
        if self.level == 1:
            arcade.play_sound(self.lvl1mus, 0.2, looping=True)
        self.sprintbarback = arcade.load_texture('assets/sprintbarback.png')
        self.sprintbarfore = arcade.load_texture('assets/sprintbarfore.png')
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
        self.light_layer = LightLayer(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite, walls=self.scene["walls"])
        self.enemy_physics_engines = []
        for enemy in self.scene["enemy_list"]:
            engine = arcade.PhysicsEngineSimple(enemy, walls=[self.scene["walls"], self.scene["secrets"]])
            self.enemy_physics_engines.append(engine)
        
        for sprite in self.scene['exit']:
           

            self.camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
            self.HUD_camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

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

        sprint_bar_color = arcade.color_from_hex_string("#bdbdbd")
        if self.player_sprite.resting:
            sprint_bar_color = arcade.color_from_hex_string("#703832")
        arcade.draw_lrwh_rectangle_textured(6, 6, 28, 357, self.sprintbarback)
        arcade.draw_lrtb_rectangle_filled(10, 30, 100 + (SCREEN_HEIGHT-700) *self.player_sprite.stamina/100, 10, sprint_bar_color)
        arcade.draw_lrwh_rectangle_textured(6, 6, 26, 357, self.sprintbarfore)
        
        self.text_alpha = int(arcade.utils.lerp(self.text_alpha, 0, 0.005))
        self.obj_alpha = int(arcade.utils.lerp(self.obj_alpha, 255, 0.01))
        
        arcade.draw_text(
            f"Level {self.level-1} : {self.subtitle}",
            SCREEN_WIDTH/2,
            SCREEN_HEIGHT/2 + 125,
            color=(255, 255, 255, self.text_alpha), 
            font_size=36,
             anchor_x="center",
              font_name = 'Kenney Pixel'
        )
        
        arcade.draw_text(
            'Objective - Escape', 
            SCREEN_WIDTH - 1270, SCREEN_HEIGHT - 30, 
            color=(255, 255, 255, self.obj_alpha),
            font_size=28, 
            font_name = 'Kenney Pixel'
        )

        if self.level == 1:
            self.subtitle = "'The Lobby'"
        if self.level == 2:
            self.subtitle = "'Habitable Zone'"
        if self.level ==3:
            self.subtitle = "'Pipe Dreams'"
        if self.level == 4:
            self.subtitle = "'Electrical Station'"


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
    
    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        objects = arcade.check_for_collision_with_list(self.player_sprite, self.scene['Interactables'])
        for obj in objects:
            # obj.interact()
            print('a')
            
    
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


        self.cursor_sprite.center_x = self.window._mouse_x 
        self.cursor_sprite.center_y = self.window._mouse_y
    
        for engine in self.enemy_physics_engines:
            engine.update()
        
        if arcade.check_for_collision_with_list(self.player_sprite, self.scene['enemy_list']):
            print('ourch')
            self.window.show_view(self.window.lose_view)

        
        if arcade.check_for_collision_with_list(self.player_sprite, self.scene["exit"], method=1):
            self.level += 1
            self.text_alpha = 255
            self.setup()

        start_x = self.torso_sprite.center_x
        start_y = self.torso_sprite.center_y
        dest_x = self.camera.position.x + self.window._mouse_x
        dest_y = self.camera.position.y + self.window._mouse_y
        x_diff = dest_x - start_x
        y_diff = dest_y - start_y
        angle = math.atan2(y_diff, x_diff)
        self.torso_sprite.angle = math.degrees(angle) -90
 

        for enemy in self.scene['enemy_list']:
            if arcade.has_line_of_sight(self.player_sprite.position , enemy.position , self.scene["walls"], 350):
                enemy.follow_sprite(self.player_sprite)
                arcade.play_sound(self.facesound, volume=0.2)
                start_x = enemy.center_x
                start_y = enemy.center_y
                dest_x = self.torso_sprite.center_x
                dest_y = self.torso_sprite.center_y
                x_diff = dest_x - start_x
                y_diff = dest_y - start_y
                angle = math.atan2(y_diff, x_diff)
                enemy.angle = math.degrees(angle) - 90
                enemy.change_x = math.cos(angle) * SPRITE_SPEED
                enemy.change_y = math.sin(angle) * SPRITE_SPEED
            else:
                enemy.change_x = 0
                enemy.change_y = 0
                enemy.random_move()
        
        self.player_light.position = self.torso_sprite.position

        self.physics_engine.update()

def main():

    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE) 
    window.menu_view = MenuView()
    window.lose_view = LoseView()
    window.show_view(window.menu_view)
    arcade.run()


if __name__ == "__main__":
    main()