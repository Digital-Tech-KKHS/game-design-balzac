from msilib.schema import Error
import arcade
from constants import *
from Enemy import Enemy
from Wretch import Wretch

def enemy_factory(spawn_sprite: arcade.Sprite):
    try:
        spawn_sprite.properties['type']
    except KeyError:
        raise Error("Tiled enemy does not have the 'type' property")
    if spawn_sprite.properties['type'] == 'faceling':
        return Enemy(spawn_sprite.center_x, spawn_sprite.center_y)
    elif spawn_sprite.properties['type'] == 'wretch':
        return Wretch(spawn_sprite.center_x, spawn_sprite.center_y)
    else:
        raise NotImplemented("Tiled enemy sprite currently has a enemy type that does not exist yet")