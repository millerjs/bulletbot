# coding=utf8
"""BulletBot module for Sopel"""

from sopel.config.types import StaticSection, NO_DEFAULT, ValidatedAttribute
from sopel.module import rule, commands, example, require_privmsg
import sopel.module
import re

from bulletbot.driver import SQLAlchemyDriver
from bulletbot.bulletbot import BulletBot
from bulletbot.models import Base


HELP_MESSAGE = """

To use the bullet bot, just talk to it throughout the day Each
time you hit enter, I'll add a bullet.

Other commands:
   .list                      - will list bullets from today
   .delete <no.> [<no. 2>]    - will delete a bullet from today
   .register <name >          - register the name to use on your bullets

That's it!
""".strip()

SKIP_TRIGGERS = ['help', 'commands']


class BulletBotSection(StaticSection):
    host = ValidatedAttribute('host', default='localhost')
    user = ValidatedAttribute('user', default=NO_DEFAULT)
    password = ValidatedAttribute('password', default=NO_DEFAULT)
    database = ValidatedAttribute('database', default='bullets')


def configure(config):
    config.define_section('bulletbot', BulletBotSection, validate=False)
    config.bulletbot.configure_setting(
        'host', 'Enter the SQL host for bullet database.')
    config.bulletbot.configure_setting(
        'user', 'Enter the SQL user for bullet database.')
    config.bulletbot.configure_setting(
        'password', 'Enter the SQL password for bullet database.')
    config.bulletbot.configure_setting(
        'database', 'Enter the SQL database name for bullet database.')


def setup(bot):
    bot.config.define_section('bulletbot', BulletBotSection, validate=False)
    db_settings = dict(
        host=bot.config.bulletbot.host,
        user=bot.config.bulletbot.user,
        password=bot.config.bulletbot.password,
        database=bot.config.bulletbot.database,
    )
    db = SQLAlchemyDriver.from_settings(db_settings)
    db.create_all(db_settings)
    Base.metadata.create_all(db.engine)
    bot.memory['bbot'] = BulletBot(db)


def shutdown(bot):
    pass


def bot_say(bot, text):
    if not text:
        return
    for line in text.split('\n'):
        bot.say(line)


def strip_command(text):
    return ' '.join(text.strip().split(' ')[1:])


@rule('[help|commands]')
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


@rule('^(?!\.)(.+)')
@require_privmsg
def new_bullets(bot, trigger, found_match=None):
    bbot = bot.memory['bbot']
    text = strip_command(trigger.match.groups(0))
    if text in SKIP_TRIGGERS:
        return
    bot_say(bot, bbot.create_bullet(str(trigger.nick), text))


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
