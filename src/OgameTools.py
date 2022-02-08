import json
from jsonschema import validate

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
  "probeStorage": {"type": "integer"}
}

def loadUniverse(filename):
  with open(filename) as file:
    res = json.load(file)
    validate(instance=res, schema=universe_schema)
    return res