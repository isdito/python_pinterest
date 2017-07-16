#!/usr/bin/env python
from pinterest import *

USERNAME = '<email>'
PASSWORD = '<password>'

p = Pinterest()
logged_in = p.login(USERNAME, PASSWORD)

if logged_in:
    boards = p.getBoards()
    print 'Your boards:', ', '.join(boards.keys())
    res = p.createPin(
        boards['Historical Photos']['id'],
        'https://imgur.com/oOXOc8x',
        'https://i.imgur.com/oOXOc8x.png',
        'Two wounded first world war soldiers - a Canadian and a German - light cigarettes on the muddy Passchendaele battlefield in Belgium in 1917'
    )
    if res:
        print 'Successfully pinned'
