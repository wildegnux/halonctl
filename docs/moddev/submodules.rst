Submodules
===========

Sometimes, it makes sense to split out different pieces of related functionality into *submodules*. See the :doc:`update module <../modules/update>` for example - ``halonctl update status``, ``halonctl update download``, etc.

Registering your own submodules is easy::

    class MyFirstSubmodule(Module):
        '''An example submodule'''
        
        def run(self, nodes, args):
            print(u"Hi")
    
    class MySecondSubmodule(Module):
        '''And this is another one'''
        
        def run(self, nodes, args):
            print(u"(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧")
    
    class MyModule(Module):
        '''A module with submodules'''
        
        submodules = {
            'first': MyFirstSubmodule(),
            'second': MySecondSubmodule()
        }
    
    module = MyModule()

Submodules behave just like normal modules, they can register their own arguments, etc.
