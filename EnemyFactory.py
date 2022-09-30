from msilib.schema import Error
import arcade
from Enemy import Enemy
from Wretch import Wretch
from Skin import Skin


def enemy_factory(spawn_sprite: arcade.Sprite):
    '''goes through each enemy spawn in the tiled map and creates the specified enemy at that spawn. if an enemy is not specified then a custom error will be raised'''
    try:
        spawn_sprite.properties['type']
    except KeyError:
        raise Error("Tiled enemy does not have the 'type' property")
    if spawn_sprite.properties['type'] == 'faceling':
        return Enemy(spawn_sprite.center_x, spawn_sprite.center_y)
    elif spawn_sprite.properties['type'] == 'wretch':
        return Wretch(spawn_sprite.center_x, spawn_sprite.center_y)
    elif spawn_sprite.properties['type'] == 'skin':
        return Skin(spawn_sprite.center_x, spawn_sprite.center_y)
    else:
        raise NotImplementedError(
            "Tiled enemy sprite currently has a enemy type that does not exist yet")
