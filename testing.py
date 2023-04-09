import configparser

config = configparser.ConfigParser()
config.read("user_credentials.ini")
username = config["DEFAULT"]["username"]
password = config["DEFAULT"]["password"]
print(username)
print(password)
