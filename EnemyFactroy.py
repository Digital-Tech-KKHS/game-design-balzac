import arcade
from constants import *
from Enemy import Enemy

def enemy_factory(spawn_sprite: arcade.Sprite):
    if spawn_sprite.properties['type'] == 'faceling':
        return Enemy(spawn_sprite.center_x, spawn_sprite.center_y)