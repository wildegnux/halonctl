halonctl
========

A commandline utility for managing Halon SP nodes and clusters.

*Currently, only Python 2.7 is supported, 3.x support is coming.*

Installation from PyPI (recommended)
------------------------------------

Simply install the ``halonctl`` package from pip::

   sudo pip install halonctl

Installation from Git (development)
-----------------------------------

If you want to develop your own modules, or work on the ``halonctl`` core, this is the option you want. If you simply want to use ``halonctl`` with the built-in modules, you probably want to install from ``pip``, as described above.

#. Install ``virtualenv`` (may need to be prefixed with ``sudo``)::
   
      pip install virtualenv

#. Set up a virtualenv in the source directory::
   
      virtualenv .

#. Activate the virtualenv; you need to do this once per terminal/tab, and will
   put you in ``halonctl``'s isolated little world, with its own packages, etc::
   
      . bin/activate
   
   To deactivate it again, just run::
   
      deactivate
   
#. Install requirements; you need to do this again if you see the file
   ``requirements.txt`` change, or if you see errors about missing modules::
   
      pip install -r requirements.txt
   
   Make sure to do this with an activated ``virtualenv``, or all dependencies
   will incorrectly be installed globally, where they may cause conflicts!

#. Run `halonctl` - again, make sure to have an activated ``virtualenv``, or it
   won't find its dependencies::
   
      ./halonctl.py --help`
