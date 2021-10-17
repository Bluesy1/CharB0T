import gspread

gc = gspread.service_account()

sh = gc.open("the BANK sheet")

print(sh.sheet1.get('A1'))