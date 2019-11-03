# ArchiveIt - The Reddit Post Archiver 
ArchiveIt is a Reddit bot created  to format Reddit posts into a savable filetypes. 
You can see it in action by visitng /u/archiveitbot on Reddit. 

**Please note ArchiveIt is currently in the alpha stage.** That means that much of the core functionality has not been
implemented yet, and so the bot should not be deployed until the project becomes more substantial. 


Currently, the only supported format is `text`. I plan to add HTML (and more?) support in the near future. 
See [the FAQ](https://www.reddit.com/r/archiveit/comments/9ltg4x/what_is_archiveit_and_faq/) for more information.

Running the bot 
---
First, create a ```config.txt``` file with your bot credentials in this format:

```
User agent
Reddit username
Reddit password
Client ID
Client Secret
Host (Optional, see "Hosts" section)
```

Optionally, create an RSA keypair and save your private key as a `.pem` file.

Install the keyring package via pip (`pip install keyring`) and set these two keys:

```
keyring.set_password("archiveit", "config", [path to config file])
# if you have an RSA key
keyring.set_password("archiveit", "privatekey", [path to .pem file])
```
The above can be ran in any Python terminal. 

To run the bot, clone this repository and type `python3 run.py`in the root directory.

Hosts 
---
ArchiveIt has support for several file hosting services for archived posts to be stored. The default host is `0x0.st`. 
Other hosts can be set in the configuration file. A list of available hosts is as follows:

| Host name | Name to use in config.txt | Free | Storage duration per file
| ------------- | ------------- | ------------- | ------------- |
| 0x0.st  | 0x0  | Y | ~300 days (depends on filesize)






Planned features
--- 
- [ ] HTML output  
- [ ] Easy verification of signatures
- [ ] Self-hosted file server for archives 