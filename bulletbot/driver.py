# -*- coding: utf-8 -*-

"""
bulletbot.driver
----------------------------------

Defines :class:`.SQLAlchemyDriver`.
"""

from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import logging
import sqlalchemy as sa

from .models import Base


class SQLAlchemyDriver(object):
    """Layer for interacting with the database."""

    logger = logging.getLogger(__name__)

    def __init__(self, host, user, password, database, backend='postgresql',
                 con_args={}, **kwargs):
        """Create a new SQLAlchemy interface for making things easer"""

        self.host = host
        self.user = user
        self.database = database
        self.backend = backend
        self.engine = create_engine(
            self._connection_string(password),
            encoding='latin1',
            connect_args=con_args,
            **kwargs
        )
        self.session_maker = sessionmaker(bind=self.engine)

    def create_all(self, settings, root_user='postgres', backend='postgresql'):
        engine = create_engine("{backend}://{user}@{host}/postgres".format(
            backend=backend, user=root_user, host=settings['host']))
        conn = engine.connect()
        conn.execute("commit")

        def try_execute(statement):
            try:
                conn.execute(statement)
            except sa.exc.ProgrammingError as e:
                print(e)
            finally:
                conn.execute("commit")

        user = settings['user']
        database = settings['database']
        password = settings['password']
        self.logger.info("creating database '{}'".format(database))
        try_execute('CREATE DATABASE "{database}"'.format(database=database))
        self.logger.info("creating user '{}'".format(user))
        try_execute("CREATE USER {user} WITH PASSWORD '{password}'"
                    .format(user=user, password=password))

        Base.metadata.create_all(engine)

    @classmethod
    def from_settings(cls, settings):
        return cls(
            settings.get('host'),
            settings.get('user'),
            settings.get('password'),
            settings.get('database'),
            backend=settings.get('backend', 'postgresql'),
            con_args=settings.get('connect_args', {}),
        )

    def _connection_string(self, password):
        """Generate the SQLAlchemy connection string"""

        return '{backend}://{user}:{password}@{host}/{database}'.format(
            backend=self.backend,
            user=self.user,
            password=password,
            host=self.host,
            database=self.database
        )

    @contextmanager
    def session(self):
        """Make working with a session even easier"""

        session = self.session_maker()
        try:
            yield session
            session.commit()
        except Exception as msg:
            self.logger.error('Rolling back session {}'.format(msg))
            session.rollback()
            raise
        finally:
            session.expunge_all()
            session.close()
