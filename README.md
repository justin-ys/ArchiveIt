# ArchiveIt - A Reddit post archiver 
/u/archiveitbot, by /u/jman005, is a bot made to format Reddit posts into a savable filetypes. You can summon it anywhere by commenting:

```/u/archiveitbot [format]``` 

Where [format] is the filetype you'd like it to output. Currently,```text``` is the only supported format, but I plan to add html (and maybe even XML?) support in the near future. 
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
```

Then, create an RSA keypair and save the private key as a `.pem` file.

Now, go to src/config.py. Set the `path` variable to the location of your config.txt file, and set the kpath variable to the location of your private key .pem file. To run the bot, go to `/src/` and run `python bot.py`.


Planned features
--- 
- [] HTML output  
- [] Easy verification of signatures
- [] Self-hosted file server for archives 