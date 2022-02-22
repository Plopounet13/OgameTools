import json
from jsonschema import validate
import numpy as np
from enum import Enum

class Universe:
    universe_schema = {
        "name": {"type": "string"},
        "galaxy": {"type": "string"},
        "system": {"type": "string"},
        "warFleetSpeed": {"type": "number"},
        "peacefulFleetSpeed": {"type": "number"},
        "holdingFleetSpeed": {"type": "number"},
        "galaxies": {"type": "integer"},
        "fleet2debris": {"type": "number"},
        "def2debris": {"type": "number"},
        "deutCosts": {"type": "number"},
        "startDM": {"type": "integer"},
        "bonusFields": {"type": "integer"},
        "economySpeed": {"type": "number"},
        "researchSpeed": {"type": "number"},
        "ACS": {"type": "boolean"},
        "probeStorage": {"type": "integer"},
        "required": ["name", "galaxy", "system", "warFleetSpeed", "peacefulFleetSpeed", "holdingFleetSpeed", "galaxies",
                     "fleet2debris", "def2debris", "deutCosts", "startDM", "bonusFields", "economySpeed",
                     "researchSpeed",
                     "ACS", "probeStorage"]
    }

    def __init__(self):
        self.data = self.universe_schema

    def load(self, filename):
        with open(filename) as file:
            res = json.load(file)
            validate(instance=res, schema=self.universe_schema)
            self.data = res


def ressource2value(res):
    return res[0] + 1.5 * res[1] + 3 * res[2]


def energy_cost(lvl):
    return [75 * 1.5**(lvl-1), 30 * 1.5**(lvl-1), 0]



class Research:
    def __init__(self):
        self.energy = 0
        self.laser = 0
        self.ion = 0
        self.hyperspace = 0
        self.plasma = 0
        self.combustion_drive = 0
        self.impulse_drive = 0
        self.hyperspace_drive = 0
        self.espionage = 0
        self.computer = 0
        self.astrophysics = 0
        self.IRN = 0
        self.graviton = 0
        self.weapons = 0
        self.shielding = 0
        self.armour = 0


class Player:
    def __init__(self, player_class="None"):
        self.player_class = player_class
        self.mine_bonus = 0.0
        self.energy_bonus = 0.0
        if self.player_class == "Collector":
            self.mine_bonus = 0.25
            self.energy_bonus = 0.1


class Boost:
    def __init__(self, metal=0.0, crystal=0.0, deut=0.0, energy=0.0):
        self.stats = [metal, crystal, deut, energy]


bronze_metal_booster = Boost(metal=0.1)
bronze_crystal_booster = Boost(crystal=0.1)
bronze_deut_booster = Boost(deut=0.1)
bronze_energy_booster = Boost(energy=0.2)
engineer = Boost(energy=0.1)
geologist = Boost(metal=0.1, crystal=0.1, deut=0.1)
commanding_staff = Boost(metal=0.02, crystal=0.02, deut=0.02)


def get_base_deut_from_temp(temp):
    return np.array([0.0, 0.0, 20]) * (0.68 - 0.002 * temp)


class Resources(Enum):
    METAL = 0
    CRYSTAL = 1
    DEUTERIUM = 2
    ENERGY = 4


class Mine:
    all_cost=[[60, 15, 0], [48, 24, 0], [225, 75, 0]]
    all_base = [[30.0, 0.0, 0.0], [0.0, 15.0, 0.0], [0.0, 0.0, 0.0]]
    all_prod_base = [[30.0, 0.0, 0.0], [0.0, 20.0, 0.0], [0.0, 0.0, 20.0]]
    all_plasma = [0.01, 0.0066, 0.0033]
    all_energy = [10.0, 10.0, 20.0]

    def __init__(self, planet, lvl=0, resource=Resources.METAL):
        self.lvl = lvl
        self.planet = planet
        self.resource = resource
        self.planet_bonus = 0
        if self.resource == Resources.METAL:
            self.planet_bonus = self.planet.metal_bonus
        elif self.resource == Resources.CRYSTAL:
            self.planet_bonus = self.planet.crystal_bonus
        self.base = np.array(Mine.all_base[self.resource.value]) * (1 + self.planet_bonus) * self.planet.universe.data["economySpeed"]
        self.base_prod = np.array(Mine.all_prod_base[self.resource.value]) * (1 + self.planet_bonus) * self.planet.universe.data["economySpeed"]
        self.base_cost = np.array(Mine.all_cost[self.resource.value])
        self.base_energy = Mine.all_energy[self.resource.value]
        if self.resource == Resources.DEUTERIUM:
            self.base_prod *= (0.68 - 0.002 * planet.temp)

    def energy(self, lvl=None):
        if lvl is None:
            lvl = self.lvl
        return self.base_energy * lvl * 1.1 ** lvl

    def cost(self, lvl=None):
        if lvl is None:
            lvl = self.lvl
        return self.base_cost * lvl * 1.5**lvl

    def prod(self, lvl=None):
        if lvl is None:
            lvl = self.lvl
        return self.base_prod * lvl * 1.1**lvl

    def plasma(self, lvl=None):
        if lvl is None:
            lvl = self.lvl
        return self.prod(lvl) * (Mine.all_plasma[self.resource.value] * self.planet.research.plasma)

    def boost(self, lvl=None):
        if lvl is None:
            lvl = self.lvl
        res = 0
        for b in self.planet.boosts:
            res += b.stats[self.resource.value]
        return self.prod(lvl) * res

    def class_boost(self, lvl=None):
        if lvl is None:
            lvl = self.lvl
        return self.planet.player.mine_bonus * self.prod(lvl)

    def total(self, lvl=None):
        if lvl is None:
            lvl = self.lvl
        return self.base + self.prod(lvl) + self.plasma(lvl) + self.boost(lvl) + self.class_boost(lvl)



class Planet:
    metal_bonuses = 16*[0.0]
    metal_bonuses[8] = 0.35
    metal_bonuses[7] = metal_bonuses[9] = 0.23
    metal_bonuses[6] = metal_bonuses[10] = 0.17

    crystal_bonuses = 16*[0.0]
    crystal_bonuses[1] = 0.4
    crystal_bonuses[2] = 0.3
    crystal_bonuses[3] = 0.2

    def __init__(self, player=Player(), uni=Universe(), research=Research(), pos=8, temp=0, size=200, boosts=None):
        if boosts is None:
            boosts = []
        self.player = player
        self.boosts = boosts
        self.research = research
        self.universe = uni
        self.pos = pos
        self.temp = temp
        self.size = size
        self.metal_bonus = Planet.metal_bonuses[self.pos]
        self.crystal_bonus = Planet.crystal_bonuses[self.pos]

        self.metal_mine = Mine(self, 0, Resources.METAL)
        self.crystal_mine = Mine(self, 0, Resources.CRYSTAL)
        self.deuterium_synt = Mine(self, 0, Resources.DEUTERIUM)
