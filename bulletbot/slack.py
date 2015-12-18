# -*- coding: utf-8 -*-

"""
bulletbot.slack
----------------------------------

BulletBot module for Slack.

To use, run ``bin/slack_bulletbot``

"""

from slackclient import SlackClient

import simplejson

from .bulletbot import BulletBot


HELP_MESSAGE = """

To use me, just talk to me throughout the day.  Each time you hit
enter, I'll add a bullet.  Bullets are sent out every evening.  If you
have any bullets that did not make the deadline, they will be sent the
following day.

Commands:
   .list                      - list unsent bullets
   .delete <no.> [<no. 2>]    - delete unsent bullets

That's it!
""".strip()


class SlackBulletBot(BulletBot):
    """BulletBot for class for RTM Slack

    """

    def __init__(self, db=None, token=None):
        super(SlackBulletBot, self).__init__(db)
        self.sc = SlackClient(token or self.args.token)

    def listen(self):
        """Connect a websocket and read/parse incoming events.

        """
        if self.sc.rtm_connect():
            self.sc.server.websocket.sock.setblocking(True)
            while True:
                try:
                    self._parse_reads(self.sc.rtm_read())
                except Exception as e:
                    self.logger.exception(e)
        else:
            print("Connection Failed, invalid token?")

    def _parse_reads(self, reads):
        """Loop over events read from the websocket

        :param list read: List of JSON reads

        """

        for read in reads:
            self._parse_read(read)

    def say(self, channel, text):
        """Send text to channel

        :param str channel: slack channel key
        :param str text: free form text

        """

        self.sc.server.channels.find(channel).send_message(text)

    def get_user_info(self, user):
        """Given user key, return user info dict

        :param str user: User key

        """

        user_info_str = self.sc.api_call('users.info', user=user)
        self.logger.debug('User info: {}'.format(user_info_str))
        user_info = simplejson.loads(user_info_str)
        assert user_info['ok'], 'Failed to get info on user {}'.format(user)
        return user_info['user']

    def _parse_read(self, read):
        """Parse a read and if it looks like a command, execute the command

        :param dict read: JSON read from websocket

        """

        channel = read.get('channel')
        text = read.get('text', '').strip()
        user = read.get('user')
        tokens = text.split(' ')

        if not channel:
            return self.logger.info('Non channel read: {}'.format(read))

        if not text:
            return self.logger.debug('Non text read: {}'.format(read))

        if not tokens:
            return self.logger.debug('Non token read: {}'.format(read))

        if self.sc.server.channels.find(channel).members:
            return self.logger.debug('Non privmsg read: {}'.format(read))

        self.logger.info("New command: '{}'".format(text))

        user_info = self.get_user_info(user)
        nick = user_info['name']
        realname = user_info.get('real_name', None)

        if user_info['is_bot']:
            return self.logger.debug('Bot message read: {}'.format(read))

        cmd = tokens[0]
        text = ' '.join(tokens[1:])

        self.execute(channel, nick, cmd, text, realname=realname)

    def execute(self, channel, nick, cmd, text, realname=None):
        """Given a nick on a channel execute a command.  If :param:`realname`
        is provided, perform a registration using it.

        :param str channel: Slack channel key
        :param str nick: Slack user `name`
        :param str cmd: first token in input text
        :param str text: all of input text that's not the first token
        :param str realname: Slack user `real_name`

        """
        self.merge_nick(nick, realname)

        self.logger.info('Command [{}]: {}'.format(cmd, text))

        if cmd in ['.ls', '.list']:
            self.say(channel, self.list_bullets(nick))

        elif cmd in ['.help', 'help', '.comands', 'commands']:
            self.say(channel, HELP_MESSAGE)

        elif cmd in ['.delete', '.rm']:
            self.say(channel, self.delete_bullets(nick, text))

        elif cmd.startswith('.'):
            self.say(channel, "Sorry :sweat_smile: I don't know that command")
            self.say(channel, HELP_MESSAGE)

        else:
            bullet = '{} {}'.format(cmd, text)
            self.say(channel, self.create_bullet(nick, bullet))
