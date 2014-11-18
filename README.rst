halonctl
========

A commandline utility for managing Halon SP nodes and clusters.

Currently, only Python 2.7 is supported, 3.x support is coming.

Installation
------------

Simply install the ``halonctl`` package from pip::

   sudo pip install halonctl

Development
-----------

To write your own modules or work on the ``halonctl`` core, clone this repo, and install it in development mode::

   pip install -e .
   
You are strongly recommended to use a `virtualenv <http://virtualenv.readthedocs.org/en/latest/>`_ to create an isolated environment for development.

Changelog
---------

1.0.1
#####

**Improved:**

* WSDL files are now cached, which shaves off a good couple of seconds *per node* from program startup.

**Fixed:**

* Cluster logins now work as intended, even when username and password are gotten from different nodes.
* The Keychain module no longer reports incorrect authentication status in some cases.

1.0.0
#####
  
* Initial release

Links
-----

* `Documentation <http://halonctl.readthedocs.org/en/latest/>`_
* `Issues <https://github.com/HalonSecurity/halonctl/issues>`_
