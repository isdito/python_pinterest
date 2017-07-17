#!/usr/bin/env python
# -*- coding: utf8 -*-

"""
BSD 2-Clause License

Copyright (c) 2017 Ilker Temir with original code by Andrey Nikishaev

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import time
import urllib
import urllib2
import re
import cookielib
import cStringIO
import gzip
import sys
import json

class Pinterest(object):
    def __init__(self,cookie=None):
        self.cookieJar           = cookie
        self.csrfmiddlewaretoken = None
        self.http_timeout        = 15
        
    def getCookies(self):
        return self.cookieJar
        
    def login(self,login,password):
        url = 'https://www.pinterest.com/'
        try:
            res,headers,cookies = self.request(url)
        except Exception as e:
            raise NotLogged(e)

        post_data = urllib.urlencode({
            'source_url':'/',
            'data':json.dumps({
                "options": {
                    "username_or_email":login,
                    "password":password
                },
                "context": {}
            }),
        })
        url = 'https://www.pinterest.com/resource/UserSessionResource/create/'
        res,headers,cookies = self.request(url,
                                           post_data,
                                           referrer='https://www.pinterest.com/',
                                           ajax=True)

        post_data = urllib.urlencode({
            'source_url':'/',
            'data':json.dumps({
                "options": {
                    "actions":[
                        {"name":"login.referrer.unauth_home_react_page.email"},
                        {"name":"login.container.home_page.email"},
                        {"name":"login.type.email"}
                    ]
                },
                "context":{}
            }),
        })
        url = 'https://www.pinterest.com/resource/UserRegisterTrackActionResource/update/'
        res,headers,cookies = self.request(url,
                                           post_data,
                                           referrer='https://www.pinterest.com/',
                                           ajax=True)
        data = json.loads(res)
        logged_in =  data['client_context']['is_authenticated']
        if logged_in:
            return True
        else:
            raise NotLogged('Authentication failure. Check your credentials.')

    def getBoards(self):
        post_data = urllib.urlencode({
            'source_url':'/pin/create/bookmarklet/',
            'data': json.dumps({
                'options': {
                    'filter': 'all',
                    'field_set_key': 'board_picker',
                    'allow_stale': True,
                    'from':"app"
                },
                "context":{}
            }),
        })
        referrer = 'https://www.pinterest.com/resource/PinResource/create/'
        url = 'https://www.pinterest.com/resource/BoardPickerBoardsResource/get/'
        res,header,query = self.request(url,
                                        post_data,
                                        referrer=referrer,
                                        ajax=True)
        boards = json.loads(res)['resource_response']['data']['all_boards']
        boards_dict={}
        for board in boards:
            name = board.pop('name')
            boards_dict[name]=board
        return boards_dict

    def createBoard(self, name, description='', category='other', 
                    privacy='public'):
        post_data = urllib.urlencode({
            'source_url':'/',
            'data': json.dumps({
                'options': {
                    'name': name,
                    'description': description,
                    'category': category,
                    'privacy': privacy,
                    'collab_board_email': True,
                    'collaborator_invites_enabled': True
                },
                'context': {}
          }),
        })
        referrer = 'https://www.pinterest.com/'
        url = 'https://www.pinterest.com/resource/BoardResource/create/'
        try:
            res,header,query = self.request(url,
                                            post_data,
                                            referrer = referrer,
                                            ajax = True)
            response = json.loads(res)
        except Exception as e:
            raise CantCreateBoard(e)
        else:
            return response['resource_response']['data']['id']
            raise CantCreatePin('Cant create pin. Cant find PinResource in response')

   
    def createPin(self, board_id, url, image_url, description):
        post_data = urllib.urlencode({
            'source_url':'/pin/create/bookmarklet/',
            'data': json.dumps({
                'options': {
                    'description': description,
                    'link': url,
                    'board_id': board_id,
                    'method': 'bookmarklet',
                    'image_url': image_url,
                    'share_facebook': False,
                    'share_twitter': False
                },
                "context":{}
            }),
        })
        referrer = 'https://www.pinterest.com/resource/PinResource/create/'
        url = 'https://www.pinterest.com/resource/PinResource/create/'
        try:
            res,header,query = self.request(url,
                                            post_data,
                                            referrer = referrer,
                                            ajax = True)
        except Exception as e:
            raise CantCreatePin(e)
        else:
            if 'PinResource' in res:
                return True
            raise CantCreatePin('Cant create pin. Cant find PinResource in response')

           
    def request(self,url,post_data=None,referrer='http://google.com/',ajax=False):
        """Donwload url with urllib2.
        
           Return downloaded data
        """
        handlers = []
        
        urllib2.HTTPRedirectHandler.max_redirections = 10
        
        if not self.cookieJar:
            self.cookieJar = cookielib.CookieJar()
        
        cookie_handler = urllib2.HTTPCookieProcessor(self.cookieJar)
        handlers.append(cookie_handler)
            
        opener = urllib2.build_opener(*handlers)

        opener.addheaders = [
            ('User-Agent', 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.1 \
                      (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1'),
            ('Accept', 'image/png,image/*;q=0.8,*/*;q=0.5'),
            ('Accept-Language', 'en-us,en;q=0.5'),
            ('Accept-Encoding', 'gzip,deflate'),
            ('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.7'),
            ('Keep-Alive', '3600'),
            ('Host','www.pinterest.com'),
            ('Origin','http://www.pinterest.com'),
            ('Connection', 'keep-alive'),
            ('Referer', referrer),
            ('X-NEW-APP','1')
        ]
        if ajax:
            opener.addheaders.append(('X-Requested-With','XMLHttpRequest'))
        if self.csrfmiddlewaretoken:
            opener.addheaders.append(('X-CSRFToken',self.csrfmiddlewaretoken))
        error_happen = False
        html = ''
        try:
            req = urllib2.Request(url, post_data)
            r = opener.open(req,timeout=self.http_timeout)
            html = r.read() 
        except DownloadTimeoutException,e:
            sys.exc_clear()
            error_happen = e
        except Exception,e:
            sys.exc_clear()
            error_happen = e
            
        if error_happen:
            return error_happen,{},{}

        headers = r.info()
        # If we get gzipped data the unzip it
        if ('Content-Encoding' in headers.keys() and headers['Content-Encoding']=='gzip') or \
           ('content-encoding' in headers.keys() and headers['content-encoding']=='gzip'):
            data = cStringIO.StringIO(html)
            gzipper = gzip.GzipFile(fileobj=data)
            # Some servers may return gzip header, but not zip data.
            try:
                html_unzipped = gzipper.read()
            except:
                sys.exc_clear()    
            else:
                html = html_unzipped

        cookies = {cookie.name:cookie.value for cookie in self.cookieJar}
        self.csrfmiddlewaretoken = cookies['csrftoken']
           
        return html,headers,cookies
         
            
class DownloadTimeoutException(Exception):
    pass
    
class NotLogged(Exception):
    pass

class CantCreateBoard(Exception):
    pass

class CantCreatePin(Exception):
    pass
    
