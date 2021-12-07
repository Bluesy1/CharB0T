import json

with open('test.json') as r:
    jsonDict = json.load(r)


path = "/mnt/c/Program Files (x86)/Steam/steamapps/common/Kerbal Space Program/GameData/SCANsat/Resources/Localization/en-us/Parts.cfg"
with open(path) as f:
    test2 = f.read()
components = test2.replace("\t","").strip().replace("			","").replace("    ","").replace("  ","").split("\n")

for key in list(jsonDict.keys()):
    for item in components:
        if item.startswith(jsonDict[key]['name']):
            itemParts = item.split(' = ')
            jsonDict[key]['name'] = itemParts[-1]

with open('test.json','w') as r:
    json.dump(jsonDict,r)