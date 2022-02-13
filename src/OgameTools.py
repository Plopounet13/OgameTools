import json
from jsonschema import validate
import numpy as np

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


def metal_cost(lvl):
    return [60 * 1.5**(lvl-1), 15 * 1.5**(lvl-1), 0]


def crystal_cost(lvl):
    return [48 * 1.5**(lvl-1), 24 * 1.5**(lvl-1), 0]


def deut_cost(lvl):
    return [225 * 1.5**(lvl-1), 75 * 1.5**(lvl-1), 0]


def energy_cost(lvl):
    return [75 * 1.5**(lvl-1), 30 * 1.5**(lvl-1), 0]


def metal_energy(lvl):
    return int(10*lvl*1.1**lvl)


def crystal_energy(lvl):
    return int(10*lvl*1.1**lvl)


def deut_energy(lvl):
    return int(20*lvl*1.1**lvl)


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
    def __init__(self, player_class):
        self.player_class = player_class
        self.mine_bonus = 0.0
        self.energy_bonus = 0.0
        if self.player_class == "Collector":
            self.mine_bonus = 0.25
            self.energy_bonus = 0.1


class Boost:
    def __init__(self, metal=0.0, crystal=0.0, deut=0.0, energy=0.0):
        self.metal = metal
        self.crystal = crystal
        self.deut = deut
        self.energy = energy


bronze_metal_booster = Boost(metal=0.1)
bronze_crystal_booster = Boost(crystal=0.1)
bronze_deut_booster = Boost(deut=0.1)
bronze_energy_booster = Boost(energy=0.2)
engineer = Boost(energy=0.1)
geologist = Boost(metal=0.1, crystal=0.1, deut=0.1)
commanding_staff = Boost(metal=0.02, crystal=0.02, deut=0.02)

class Planet:
    metal_bonus = 16*[1.0]
    metal_bonus[8] = 1.35
    metal_bonus[7] = metal_bonus[9] = 1.23
    metal_bonus[6] = metal_bonus[10] = 1.17

    crystal_bonus = 16*[0.0]
    crystal_bonus[1] = 0.4
    crystal_bonus[2] = 0.3
    crystal_bonus[3] = 0.2

    def __init__(self, uni, player, pos, temp, size, research, boosts):
        self.boosts = boosts
        self.research = research
        self.uni = uni
        self.pos = pos
        self.temp = temp
        self.size = size
        self.metal_factor = 1 + 0.01 * research.plasma + player.mine_bonus
        self.crystal_factor = 1 + 0.0066 * research.plasma + player.mine_bonus + self.crystal_bonus[pos]
        self.deut_factor = 1 + 0.0033 * research.plasma + player.mine_bonus
        self.energy_factor = 20.0
        for b in self.boosts:
            self.crystal_factor += b.crystal
            self.metal_factor += b.metal
            self.deut_factor += b.deut
            self.energy_factor += b.energy

    def base_metal(self):
        return np.array([30., 0.0, 0.0]) * self.metal_bonus[self.pos] * self.uni.data["economySpeed"]

    def metal_prod(self, lvl):
        return self.base_metal() * (1 + self.metal_factor * lvl * 1.1**lvl)

    def crystal_prod(self, lvl):
        return np.array([0.0, 20, 0.0]) * self.uni.data["economySpeed"] * self.crystal_factor * lvl * 1.1**lvl

    def deut_prod(self, lvl):
        return np.array([0.0, 0.0, 20]) * self.uni.data["economySpeed"] * (0.68 - 0.002 * self.temp) * self.deut_factor * lvl * 1.1**lvl
