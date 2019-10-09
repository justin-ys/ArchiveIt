# ########### #
# ##imports## #
# ########### #

# local
from src import config, libformatter

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

# ############# #
# ##constants## #
# ############# #
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
    return Reddit(user_agent=config.get_useragent(),
                  username=config.get_username(),
                  password=config.get_password(),
                  client_id=config.get_clientid(),
                  client_secret=config.get_clientsecret()
                  )


# ############### #
# ##bot workers## #
# ############### #

def bot_formatter(args):
    """Formats a Reddit post.
    Arguments should be packed
    into a tuple, in the form
    (submission id, reddit instance
    to use, formatter type)."""

    post_id, rdt, formatter = args
    print(args)
    if formatter is not None:
        reply = formatter(rdt.submission(id=post_id)).out
    else:
        reply = "**Error**: the format you provided is not recognized."
    return reply


def run():
    reddits = [make_reddit()] * PROCESSES

    reddit = make_reddit()

    while True:
        flist = []
        mlist = []
        queue = []
        # ^is this pythonic? Probably not, find alternative
        for mention in reddit.inbox.mentions(limit=1):
            #if mention.new:
            formatter = libformatter.get_format("".join(mention.body.split("/u/%s" % config.get_username())))
            mlist.append(mention.submission.id)
            flist.append(formatter)
            queue.append(mention.id)
                #mention.mark_read()

        while len(mlist) > 0:
            with Pool(processes=PROCESSES) as pool:
                args = list(zip(mlist, reddits, flist))
                # Remove the replies this round of processing will take care of from our reply list.
                mlist = mlist[len(args):]
                # TODO: Change to pool.starmap so we don't have to pack arguments
                replies = pool.map(bot_formatter, args)

            for mention, rpl in enumerate(replies):
                try:
                    print(reddit.comment(id=queue[mention]))
                    reddit.comment(id=queue[mention]).reply("[Archived Thread](%s) | [Signed](%s)" %
                                                            (transfersh_upload(bytes(rpl, 'utf-8')),
                                                             transfersh_upload(
                                                                 bytes(
                                                                     str(
                                                                         crypto_sign(rpl, config.get_privatekey(),
                                                                                     None)),
                                                                     'utf-8')
                                                             )
                                                             )
                                                            + bottomtext
                                                            )

                except APIException:
                    print('Ratelimit hit, sleeping for 10 minutes.')
                    time.sleep(600)

                except Forbidden:
                    print("Can't reply to comment (maybe deleted?)")
                    pass
