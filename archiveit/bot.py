from archiveit import libformatter, config
from archiveit.hosts import HostException

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes

from praw import Reddit
from praw.exceptions import APIException, ClientException
from prawcore.exceptions import Forbidden, NotFound
from praw.models import Message
import requests
import time

import logging
logger = logging.getLogger("archiveit.bot")

# constants
PROCESSES = 2
bottomtext = ("\n\n---\n\n^^[About]"
              "(https://www.reddit.com/r/archiveit/"
              "comments/9ltg4x/what_is_archiveit_and"
              "_faq/)&#32;|&#32;by&#32;/u/jman005"
              )
host = config.host()
#                                                     #

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


def bot_formatter(post_id, reddit, formatter):
    """Formats a Reddit post.
    Arguments should be packed
    into a tuple, in the form
    (submission id, reddit instance
    to use, formatter type)."""

    if formatter is not None:
        formatter_active = formatter(reddit.submission(id=post_id))
        reply = formatter_active.out()
    else:
        return None
    return {'text': reply, 'filetype': formatter_active.filetype}


def task_worker(task, reddit):
    logger.info("Archive request received from /u/%s - ID %s" % (task.author.name, task.id))
    try:

        if type(task) is Message:
            formatter = libformatter.get_format(task.body.split(" ")[1])
            submission = reddit.submission(url=task.body.split(" ")[0])
        else:
            formatter = libformatter.get_format(task.body.split("/u/%s" % config.username)[-1])
            submission = task.submission

        body = bot_formatter(submission.id, reddit, formatter)
        task.mark_read()

    except (ClientException, NotFound):
        task.reply("**Error**: Your query is invalid or the post you have provided is no longer available.")
        task.mark_read()
        return False

    except IndexError:
        task.reply("**Error**: No filetype was provided.")
        task.mark_read()
        return False

    if body['text'] is None:
        reply = "**Error**: Invalid filetype given for archival."
    else:
        url_file = host.upload(bytes(body['text'], 'utf-8'), name=task.id + body['filetype'])
        reply = "[Archived Thread](%s)" % url_file
        if config.privatekey is not None:
            signed = bytes(str(crypto_sign(body['text'], config.privatekey, None)), 'utf-8')
            url_signed = host.upload(signed, name=str(task.id) + '.signed')
            reply += " | [Signed](%s)" % url_signed
        reply += bottomtext
    if type(task) is Message:
        task.reply(reply)
    else:
        reddit.comment(id=task.id).reply(reply)

    return True


def run():
    logger.info("Bot started")
    reddit = make_reddit()

    while True:
        try:

            for message in reddit.inbox.unread(limit=None):
                if message.new:
                    task_worker(message, reddit)

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