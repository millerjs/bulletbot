# -*- coding: utf-8 -*-

"""
bulletbot.models
----------------------------------

Defines :class:`.Recipient`, :class:`.User`, :class:`.Bullet`.
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    text,
)


Base = declarative_base()


class Recipient(Base):
    """People who are receiving bullets"""

    __tablename__ = 'recipients'

    email = Column(String, primary_key=True)
    is_addressee = Column(Boolean, default=False)

    def __repr__(self):
        return ('<Recipient({})>'.format(self.email))


class Bullet(Base):
    """A bullet is a note of what was done during the day"""

    __tablename__ = 'bullets'

    id = Column(Integer, primary_key=True)
    bullet = Column(String)
    last_sent = Column(DateTime)
    nick = Column(String, ForeignKey('users.nick'))

    datetime = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text('now()'),
    )

    user = relationship("User", back_populates="bullets")

    def __repr__(self):
        return ("<Bullet({}, {}, '{}...')>"
                .format(self.id, self.nick, self.bullet[:15]))


class User(Base):
    """People who are submitting bullets"""

    __tablename__ = 'users'

    nick = Column(String, primary_key=True)
    realname = Column(String)
    password = Column(String)

    bullets = relationship(
        "Bullet",
        order_by=Bullet.datetime,
        back_populates='user',
    )

    def __repr__(self):
        return ('<User({})>'.format(self.nick))
