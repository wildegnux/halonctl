halonctl
========

A commandline utility for managing Halon SP nodes and clusters.

*Currently, only Python 2.7 is supported, 3.x support is coming.*

Installation from PyPI (recommended)
------------------------------------

Simply install the ``halonctl`` package from pip::

   sudo pip install halonctl

If it complains about your ``setuptools`` being too old, simply upgrade it, then try again::

   sudo easy_install -U setuptools
   sudo pip install halonctl

Installation from Git (development)
-----------------------------------

If you want to develop your own modules, or work on the ``halonctl`` core, do this:

#. Clone this repo somewhere, and enter it::
   
      git clone https://github.com/HalonSecurity/halonctl
      cd halonctl

#. Install ``halonctl`` in development mode::
   
      pip install -e .
   
   You are strongly recommended to use a `virtualenv <http://virtualenv.readthedocs.org/en/latest/>`_.

Links
-----

* `Documentation <http://halonctl.readthedocs.org/en/latest/>`
* `Issues <https://github.com/HalonSecurity/halonctl/issues>`
