Data Roles
==========

Sometimes, a piece of data has an obvious meaning - if you have a ``datetime`` object, there's a good chance that it is indeed a point in time.

Other times, however, it's not so easy: if you have a number, how do you tell the difference between an HTTP status code and a UNIX timestamp?

The problem
-----------

Sometimes, we need to get such a value on the screen, in a way that makes sense to a human. But it also has to be machine-readable, because script output should be usable with other programs.

One approach is to compromise - ``2015-02-12T14:04:21.978946+00:00`` is fairly readable to a human, and also machine-parseable. But it's not all that easy to read for a human, and more verbose than a machine needs.

Another approach is to have the module check whether the intended audience is human or machine, but then you wouldn't have the module and formatter decoupled anymore, and bloat the module at that.

Enter: Roles
------------

Roles allow us to assign context to a context-sensitive value::

    from halonctl.roles import HTTPStatus
    
    # ...
    
    code = 200
    yield (node, node.cluster, HTTPStatus(code))

By default, the third column will read "OK". But when machine-readable output is requested with the ``--raw`` flag, it will instead read ``200`` - you can try it out yourself with the ``status`` module.

Roles for fun and profit
------------------------

To use a Role, you simply have to emit a value wrapped in one. If the built-in roles (see the documentation for :mod:`halonctl.roles`) don't suit your needs, you can easily make your own by subclassing :class:`halonctl.roles.Role`::

    from halonctl.roles import Role
    
    class Color(Role):
        def __init__(self, r, g, b):
            self.r = r
            self.g = g
            self.b = b
        
        def raw(self):
            return u"rgb({r}, {g}, {b})".format(r=self.r, g=self.g, b=self.b)
        
        def human(self):
            if self.r > self.g and self.r > self.b:
                return u"Red"
            elif self.g > self.r and self.g > self.b:
                return u"Green"
            elif self.b > self.r and self.b > self.g:
                return u"Blue"
            return u"Gray"

This is a simple Role, that (really inaccurately) prints a color name for humans, and the exact color in rgb(r, g, b) form for machines. Now, this is completely useless, but it does demonstrate just how simple Roles are. Wrap your thing in a Role, and there's your model/view decoupling.

Got a status code?
------------------

Status codes are actually so common that they got their own convenience class to inherit from::

    from halonctl.roles import StatusCode
    
    class OSA(StatusCode):
        codes = {
            0: u"No",
            1: u"Yes",
            2: u"Maybe"
        }

That's it. If you need to do something more advanced for the default case, see this example from the ``update`` module, where 1-100 is instead percent progress::

    from halonctl.roles import StatusCode
    
    class UpdateStatusCode(StatusCode):
        codes = {
            101: u"Checksumming...",
            102: u"Ready to install!",
            103: u"Installing...",
            None: u"No pending update"
        }
        
        def get_default(self, code):
            if code <= 100:
                return u"Downloading: {0}%%".format(code)
            return super(UpdateStatusModule, self).get_default(code)
