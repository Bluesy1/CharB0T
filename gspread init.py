import gspread

gc = gspread.service_account()

sh = gc.open("Example spreadsheet")

print(sh.sheet1.get('A1'))