
# ##imports## #

# local
from archiveit import libformatter, config

# crypto
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes

# others
from praw import Reddit
from praw.exceptions import APIException
from prawcore.exceptions import Forbidden
import requests
from multiprocessing import Pool
import time


# ##constants## #

PROCESSES = 2
bottomtext = ("\n\n---\n\n^^[About]"
              "(https://www.reddit.com/r/archiveit/"
              "comments/9ltg4x/what_is_archiveit_and"
              "_faq/)&#32;|&#32;by&#32;/u/jman005"
              )


def crypto_sign(msg, key, psw):
    """Signs utf-8 string with provided private key,
    returns bytes"""
    with open(key, "rb") as key1:
        pemkey = serialization.load_pem_private_key(key1.read(), password=psw, backend=default_backend())
    return pemkey.sign(
        bytes(msg, 'utf-8'),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )


def transfersh_upload(fl):
    """Uploads bytes to transfer.sh, returns
    a link of uploaded file"""

    r = requests.put("https://transfer.sh/archive.txt", files={"archive.txt": fl})
    return r.text


def make_reddit():
    return Reddit(user_agent=config.useragent,
                  username=config.username,
                  password=config.password,
                  client_id=config.clientid,
                  client_secret=config.clientsecret
                  )



# ##bot workers## #


def bot_formatter(args):
    """Formats a Reddit post.
    Arguments should be packed
    into a tuple, in the form
    (submission id, reddit instance
    to use, formatter type)."""

    post_id, rdt, formatter = args
    if formatter is not None:
        reply = formatter(rdt.submission(id=post_id)).out()
    else:
        reply = "**Error**: Invalid format."
    return reply


def run():
    reddits = [make_reddit()] * PROCESSES

    reddit = make_reddit()

    host = config.host()

    while True:
        flist = []
        mlist = []
        queue = []
        for mention in reddit.inbox.mentions(limit=1):
            if mention.new:
                formatter = libformatter.get_format(mention.body.split("/u/%s" % config.username)[-1])
                mlist.append(mention.submission.id)
                flist.append(formatter)
                queue.append(mention.id)
                mention.mark_read()

        while len(mlist) > 0:
            with Pool(processes=PROCESSES) as pool:
                args = list(zip(mlist, reddits, flist))
                # Remove the replies this round of processing will take care of from our reply list.
                mlist = mlist[len(args):]
                replies = pool.map(bot_formatter, args)

            for mention, rpl in enumerate(replies):
                try:
                    url_file = host.upload(bytes(rpl, 'utf-8'))
                    url_signed = host.upload(bytes(str(crypto_sign(rpl, config.privatekey, None)),'utf-8'))

                    reddit.comment(id=queue[mention]).reply(
                        "[Archived Thread](%s) | [Signed](%s)" % (url_file, url_signed) + bottomtext)



                except APIException:
                    print('Ratelimit hit, sleeping for 10 minutes.')
                    time.sleep(600)

                except Forbidden:
                    print("Can't reply to comment (maybe deleted?)")
                    pass
