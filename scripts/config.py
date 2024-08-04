import json
import os

CONFIG_LOC = 'data/config'

# Add Config containers below
config = {}

for file in os.listdir(CONFIG_LOC):
    if ".py" in file:
        continue
    f = open(CONFIG_LOC + '/' + file, 'r')
    config[file.split('.')[0]] = json.load(f)
    f.close()

