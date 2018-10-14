import keyring  # Remove if not being used for file locations.


# Insert the location of your config file here.
path = keyring.get_password("archiveit", "config")

# Insert the location of your private key file here.
kpath = keyring.get_password("archiveit", "privatekey")


try:
    with open(path, 'r') as f:
        lines = f.read().split('\n')
except FileNotFoundError:
    raise FileNotFoundError(
        "Config file not found. A config.txt file should be included in the same directory as the bot.")


def get_useragent():
    return lines[0]


def get_username():
    return lines[1]


def get_password():
    return lines[2]


def get_clientid():
    return lines[3]


def get_clientsecret():
    return lines[4]

def get_privatekey():
    return kpath