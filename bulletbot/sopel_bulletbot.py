# -*- coding: utf-8 -*-

"""
bulletbot.sopel_bulletbot
----------------------------------

BulletBot module for Sopel.

To use bulletbot with Sopel (formerly Willie) IRC bot, put the
following line in the file `~/.sopel/modules/sopel_bulletbot.py`

.. code-block:: python

    from bulletbot.sopel_bulletbot import *  # noqa

"""

from sopel.config.types import StaticSection, NO_DEFAULT, ValidatedAttribute
from sopel.module import rule, commands, require_privmsg

from bulletbot.driver import SQLAlchemyDriver
from bulletbot.bulletbot import BulletBot
from bulletbot.models import Base

import configargparse
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

HELP_MESSAGE = """

To use me, just talk to me throughout the day.  Each time you hit
enter, I'll add a bullet.  Bullets are sent out every evening.  If you
have any bullets that did not make the deadline, they will be sent the
following day.

Commands:
   .list                      - list unsent bullets
   .delete <no.> [<no. 2>]    - delete unsent bullets
   .register <name >          - register the name to use on your bullets

That's it!
""".strip()

SKIP_TRIGGERS = ['help', 'commands']


def setup(bot):
    bbot = BulletBot()
    bbot.db.create_all(bbot.db_settings)
    Base.metadata.create_all(bbot.db.engine)
    bot.memory['bbot'] = bbot


def shutdown(bot):
    pass


def bot_say(bot, text):
    """Wrapper around bot.say to turn newlines into IRC lines

    """
    for line in text.split('\n') if text else []:
        bot.say(line)


def strip_command(text):
    return ' '.join(text.strip().split(' ')[1:])


@commands('help')
@require_privmsg
def help(bot, trigger):
    bot_say(bot, HELP_MESSAGE)


@commands('list')
@commands('ls')
@require_privmsg
def list_bullets(bot, trigger, found_match=None):
    bbot = bot.memory['bbot']
    bot_say(bot, bbot.list_bullets(str(trigger.nick)))


@commands('delete')
@commands('rm')
@require_privmsg
def delete_bullets(bot, trigger, found_match=None):
    bbot = bot.memory['bbot']
    text = strip_command(trigger.match.string)
    bot_say(bot, bbot.delete_bullets(str(trigger.nick), text))


@commands('register')
@require_privmsg
def register(bot, trigger, found_match=None):
    bbot = bot.memory['bbot']
    realname = strip_command(trigger.match.string)
    bot_say(bot, bbot.register_nick(str(trigger.nick), realname))


@rule('^(?!\.)(.+)')
@require_privmsg
def new_bullet(bot, trigger, found_match=None):
    bbot = bot.memory['bbot']
    text = trigger.match.groups(0)[0]
    if text in SKIP_TRIGGERS:
        return
    bot_say(bot, bbot.create_bullet(str(trigger.nick), text))
