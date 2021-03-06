from texty.builtins.characters import Monster
import random

class Zombie(Monster):

    name = 'a %s zombie'
    nouns = 'zombie'
    shortname = 'zombie'
    adjectives = 'crumbling decaying disgusting fetid foul grotesque hideous horrible lumbering '
    adjectives += 'mutilated overripe putrid rancid ravenous rotting shambling slobering'

    description = "Yet another member of the walking dead. At first you had trouble killing these creatures "
    description += "who so closely resembled your friends, your co-workers... your family. In time, "
    description += "you realized that these rotten corpses have no connection to your former "
    description += "loved ones, no matter how much they look alike. Kill them all."

    def __init__(self):
        adjs = random.sample(self.adjectives, 1)
        super(Zombie, self).__init__(self.__class__.name % str.join(', ', adjs))
        self.adjectives = set(adjs)

