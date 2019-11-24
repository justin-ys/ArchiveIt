from archiveit import libformatter, config
from archiveit.hosts import HostException

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes

from praw import Reddit
from praw.exceptions import APIException
from prawcore.exceptions import Forbidden
import requests
from multiprocessing import Pool
import time

import logging
logger = logging.getLogger("archiveit.bot")

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


def make_reddit():
    return Reddit(user_agent=config.useragent,
                  username=config.username,
                  password=config.password,
                  client_id=config.clientid,
                  client_secret=config.clientsecret
                  )


def bot_formatter(args):
    """Formats a Reddit post.
    Arguments should be packed
    into a tuple, in the form
    (submission id, reddit instance
    to use, formatter type)."""

    post_id, rdt, formatter = args
    if formatter is not None:
        formatter_active = formatter(rdt.submission(id=post_id))
        reply = formatter_active.out()
    else:
        return None
    return {'text': reply, 'filetype': formatter_active.filetype}


def run():
    logger.info("Bot started")

    reddits = [make_reddit()] * PROCESSES
    reddit = make_reddit()
    host = config.host()

    while True:
        flist = []
        mlist = []
        queue = []
        for mention in reddit.inbox.mentions(limit=3):
            if mention.new:
                logging.info("Archive request received from /u/%s" % mention.author.name)
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
                    if rpl['text'] is None:
                        reply = "**Error**: Invalid filetype provided."
                    else:
                        url_file = host.upload(bytes(rpl['text'], 'utf-8'), name=str(queue[mention]) + rpl['filetype'])
                        reply = "[Archived Thread](%s)" % url_file
                        if config.privatekey is not None:
                            signed = bytes(str(crypto_sign(rpl['text'], config.privatekey, None)), 'utf-8')
                            url_signed = host.upload(signed, name=str(queue[mention]) + '.signed')
                            reply += " | [Signed](%s)" % url_signed
                        reply += bottomtext
                    reddit.comment(id=queue[mention]).reply(reply)



                except APIException:
                    logging.error("Ratelimit hit or Reddit API experiencing outage. Sleeping for 10 minutes")
                    time.sleep(600)
                    logging.info("Bot restarted")

                except Forbidden:
                    logging.warning("Comment invalid, could not reply")

                except HostException:
                    logging.error("Host error, sleeping for 10 minutes")
                    time.sleep(600)
                    logging.info("Bot restarted")
