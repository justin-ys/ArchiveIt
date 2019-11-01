import keyring  # Remove if not being used for file locations.
from archiveit import hosts

# Insert the location of your config file here.
path = keyring.get_password("archiveit", "config")

# Insert the location of your private key file here.
privatekey = keyring.get_password("archiveit", "privatekey")


try:
    with open(path, 'r') as f:
        lines = f.read().split('\n')
except (FileNotFoundError, TypeError):
    raise FileNotFoundError(
        "Config file location not set. Please do so via keyring.")


try:
    useragent = lines[0]
    username = lines[1]
    password = lines[2]
    clientid = lines[3]
    clientsecret = lines[4]
except IndexError:
    raise FileNotFoundError(
                            "Bot configuration file corrupted or formatted improperly."
                            "See readme for setup instructions.")
try:
    _host_string = lines[5]
    host = hosts.hosts[_host_string]
except IndexError:
    default = list(hosts.hosts.keys())[0]
    print("WARNING: No hosting provider specified. Using default provider '%s'" % default)
    host = hosts.hosts[default]
except KeyError:
    raise ValueError("Hosting provider '%s' is not a valid host." % _host_string)
