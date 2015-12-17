#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_bulletbot
----------------------------------

Tests for `bulletbot` module.
"""

import sys
import unittest

import bulletbot
from bulletbot.driver import SQLAlchemyDriver
from bulletbot.bulletbot import BulletBot

import logging
logging.root.setLevel(level=logging.DEBUG)


from bulletbot.models import (
    Recipient,
    User,
    Bullet,
)

db_settings = {
    'host': '',
    'user': 'test',
    'password': 'test',
    'database': '__test_bulletbot__',
}

db = SQLAlchemyDriver.from_settings(db_settings)
db.create_all(db_settings)
bulletbot.models.Base.metadata.create_all(db.engine)


class TestBulletbot(unittest.TestCase):

    test_bullets = [
        'bullet A',
        'test bullet B',
        'third',
    ]

    def setUp(self):
        with db.session() as s:
            s.query(Recipient).delete()
            s.query(Bullet).delete()
            s.query(User).delete()
        self.bot = BulletBot(db)
        self.bot.logger.level = logging.DEBUG
        self.create_bullets()

    def create_bullets(self):
        for bullet in self.test_bullets:
            self.bot.create_bullet('nick', bullet)

    def test_tokenize(self):
        self.assertEqual(self.bot.tokenize('1, 2 test'), ['1', '2', 'test'])

    def test_create(self):
        with db.session() as s:
            bullets = s.query(Bullet).all()
            self.assertEqual(3, len(bullets))
            for bullet in bullets:
                self.assertEqual(bullet.nick, 'nick')
                self.assertIn(bullet.bullet, self.test_bullets)

    def test_list(self):
        self.assertEqual(self.bot.list_bullets('nick'),
                         "0. bullet A\n1. test bullet B\n2. third")

    def test_delete_one(self):
        self.bot.delete_bullets('nick', '0')
        self.assertEqual(self.bot.list_bullets('nick'),
                         "0. test bullet B\n1. third")

    def test_delete_two(self):
        self.bot.delete_bullets('nick', '0, 2')
        self.assertEqual(self.bot.list_bullets('nick'),
                         "0. test bullet B")

    def test_delete_invalid(self):
        self.bot.delete_bullets('nick', 'first')
        self.bot.delete_bullets('nick', '')

    def test_delete_out_of_range(self):
        self.assertEqual(self.bot.delete_bullets('nick', '3'),
                         "Bullet 3 not found.")


if __name__ == '__main__':
    sys.exit(unittest.main())
