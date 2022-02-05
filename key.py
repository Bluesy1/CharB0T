from cryptography.fernet import Fernet

with open('filekey.key', 'rb') as file:
    key = file.read()

# this opens your json and reads its data into a new variable called 'data'
with open('tickets.json', 'rb') as f:
    data = f.read()

# this encrypts the data read from your json and stores it in 'encrypted'
fernet = Fernet(key)
encrypted = fernet.encrypt(data)

# print(json.loads(encrypted))
# this writes your new, encrypted data into a new JSON file
with open('tickets.json', 'wb') as f:
    f.write(encrypted)
    # json.dump(json.loads(encrypted),f)
