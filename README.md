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

By default, logging warnings to the console is enabled and the default logging level is `WARNING`. To change this, use 
the command line argument `--ll` for run.py. Available logging levels are `DEBUG, INFO, WARNING, ERROR, CRITICAL`.
To save logs to a file, specify the logfile path via the `--log_file` argument.

Hosts 
---
ArchiveIt has support for several file hosting services for archived posts to be stored. The default host is `0x0.st`. 
Other hosts can be set in the configuration file.

Some hosts may require their own configuration file; to set these up, create a .txt file with the same name as that
specified in the host's ''Name to use in config.txt' cell in the table below, then within it write each configuration 
setting on a new line. 

A list of available hosts is as follows:

| Host name | Name to use in config.txt | Free | Storage duration per file | Configuration settings
| ------------- | ------------- | ------------- | ------------- | ------------- |
| 0x0.st  | 0x0  | Y | ~300 days (depends on filesize) | N/A
| Local storage  | local  | Y | N/A | • Directory to save in (relative to root directory by default)






Planned features
--- 
- [ ] HTML output  
- [ ] Easy verification of signatures
- [ ] Self-hosted file server for archives 