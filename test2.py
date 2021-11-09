import json


with open('/mnt/c/Program Files (x86)/Steam/steamapps/common/Kerbal Space Program/PartDatabase.cfg') as t:
    test = t.read()

parts = test.split("\n")

parts2=[x[7:] for x in parts if x.startswith('	url = ')]
exDict={}

for i in parts2:
    path = "/mnt/c/Program Files (x86)/Steam/steamapps/common/Kerbal Space Program/GameData/"+(str((i.rsplit("/",1))[0])+".cfg")
    with open(path) as f:
        test2 = f.read()
    components = test2.replace("\t","").strip().replace("			","").replace("    ","").replace("  ","").split("\n")
    a=(str([x for x in components if x.startswith('name = ') or x.startswith('name= ')][0])).rsplit("= ",1)[-1]
    b=[x for x in components if x.startswith('entryCost =') or x.startswith('entryCost= ')]
    b=(b[0]).rsplit("= ",1)[-1]
    c=(str([x for x in components if x.startswith('cost = ') or x.startswith('cost= ')])).rsplit("= ",1)[-1][:-2]
    d=(str([x for x in components if x.startswith('title =') or x.startswith('title= ')][0]))
    d=((d.rsplit("//")[-1]).rsplit("=",1)[-1]).strip()
    inDict={'entry':b,'cost':c,'name':d.strip()}
    exDict.update({a:inDict})


with open('test.json','w') as r:
    json.dump(exDict,r)
