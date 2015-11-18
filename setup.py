#!/usr/bin/python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(name='elotouch',
      version='0.1',
      description='Serial Elo touch driver (protocol E271-2210)',
      author='Sven Schlender',
      author_email='kontakt@mobacon.de',
      url='http://www.mobacon.de',
      packages = ['.'],
      install_requires = ['serial', 'uinput'],
      scripts = ['./elotouch.py'],
     )
