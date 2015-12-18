===============================
BulletBot
===============================

.. image:: https://img.shields.io/travis/millerjs/bulletbot.svg
        :target: https://travis-ci.org/millerjs/bulletbot
        :alt: Travis

Chat bot for logging what employee completed tasks.

* Free software: ISC license

Install
-------


* Requirements

  - Python3_
  - pip_

.. _Python3: https://www.python.org/download/releases/3.0/
.. _pip: https://pip.pypa.io/en/stable/installing/


* Ubuntu::

     sudo apt-get update
     # install python requirements
     sudo apt-get install libxml2-dev libxslt1-dev python3-dev libenchant1c2a
     # install postgres
     sudo apt-get install postgresql-X.Y postgresql-server-dev-9.4
     sudo apt-get install

Note: You'll have to edit `pg_hba.conf` to trust local connections to setup the database.

* Setup `virtualenv`::

   $ mkdir ~/.venvs
   $ virtualenv ~/.venvs/bulletbot --python=$(which python3)
   $ source ~/.venvs/bulletbot/bin/activate

* Install bulletbot

.. codeblock:: bash

   $ git clone https://github.com/millerjs/bulletbot.git
   $ cd bulletbot
   $ python setup.py develop

Slack
=====

Put this in ``~/.bullebot.ini`` and replace ``<X>``::

    [database]
    name = <DATABASE NAME>
    user = <USER>
    password = <PASSWORD>
    host = <POSTGRESQL HOST>

    [slack]
    token = <TOKEN>

Execute::

   $ ./bin/slack_bulletbot


IRC
===

Execute and follow config::

   $ sopel -w
   $ echo """from bulletbot.sopel_bulletbot import *  # noqa""" > cat ~/.sopel/modules/sopel_bulletbot.py

Then append this to ``~/.sopel/default.cfg``::

    [core]
    enable = sopel_bulletbot,admin,reload

    [bulletbot]
    host = <POSTGRESQL HOST>
    user = <USER>
    password = <PASSWORD>
    database = <DATABASE NAME>

Execute::

   $ sopel -w


Features
--------

* IRC
* TODO: Slack
