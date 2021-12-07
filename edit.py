import pandas
import auxone

userInfo = auxone.userInfo.readUserInfo()

Copper = 470021089104494598 #copper
Stealth = 718188351508971542 #stealth
Lukas = 754719299326836868#lukas
Dino = 287990529461846017#dino
print(userInfo.loc[str(Copper)])
print(userInfo.loc[str(Stealth)])
print(userInfo.loc[str(Lukas)])
print(userInfo.loc[str(Dino)])
"""
userInfo.loc[str(Copper),"RPO"] = 'CP'
userInfo.loc[str(Stealth),"RPO"] = 'CP'
userInfo.loc[str(Lukas),"RPO"] = 'CP'
userInfo.loc[str(Dino),"RPO"] = 'CP'
auxone.userInfo.writeUserInfo(userInfo)
print("Edit done:")
print(userInfo.loc[str(Copper)])
print(userInfo.loc[str(Stealth)])
print(userInfo.loc[str(Lukas)])
print(userInfo.loc[str(Dino)])
"""