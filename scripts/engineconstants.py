# all entities that are to be instantiated need to be imported here

from entity.player_entities.player import Player
from entity.decals.decal import *
from entity.meta.door import Door
from scripts.particle_presets import *
from scripts.wave import Wave
from scripts.rope import ParticleRope

# defines where resources are located inside the project
RESOURCEPATHS = {
    "animations": 'data/sprites/animations',
    "thumbnails": 'data/sprites/thumbnails',
    "sprites": 'data/sprites',
    "rooms": 'data/ogmodata',
    "backgrounds": 'data/sprites/backgrounds'
}

# defines which dataformats are supported for loading images
SUPPORTED_IMAGE_FORMATS = [
    'png',
    'jpg',
    'jpeg'
]

# defines the framerate at which the game is allowed to run at
GLOBAL_FRAMERATE = 60

# defines a list of entities the entitymanager is allowed to dynamically instantiate
INSTANTIABLE_OBJECTS = {"Player": Player,
                        "Decals": Decals,
                        "ActorDecals": ActorDecals,
                        "WindParticle": WindParticle,
                        "Door": Door,
                        "Wave": Wave,
                        "ParticleRope": ParticleRope}
