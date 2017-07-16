Pinterest Module for Python
==

This is a Pinterest module for Python that is based on [Andrey Nikishaev](https://github.com/creotiv)'s earlier work. Pinterest changed their system pretty significantly since Andrey's code was developed, so all essential functions were rewritten and search method has been removed.

Pinterest has an API, which is the proper way to access their service for anything serious. However that API has requirements that are not easy to meet, like multiple collaborators, seemingly long approval cycles for apps, etc. These make sense for full scale projects but are an overkill for a simple one-time project that requires a basic interaction with Pinterest to manage your own account.

I didn't see anything explicit in Pinterest's [Terms of Service](https://policy.pinterest.com/en/terms-of-service) that would prevent access in a programtic way as it is done with this mdoule. However, my interpretation of their ToS may not be correct or things may change. You’re responsible for following all laws, regulations and industry codes, as well as their terms and policies. Responsibility is yours, use this module at your own risk.

And finally, this module requires you to put your credentials into the code, which is inherently insecure.


Example of use:
```
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
```
