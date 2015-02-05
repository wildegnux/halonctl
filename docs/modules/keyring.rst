``keyring`` - Securely authenticate with nodes
==============================================

::

    halonctl keyring [subcommand]

The ``keyring`` module is a bit special in that it doesn't really affect your nodes at all - rather, it's an interface to halonctl's own keyring facilities. This uses your system's password storage to store credentials more securely than it would be to enter them in your configuration files.

It uses the excellent `keyring <https://bitbucket.org/kang/python-keyring-lib>`_ library, which picks the best available out of a number of backends - OSX's Keychain, Windows' Credential Vault, Linux's Secret Service, GNOME Keyring, KDE's kwallet, etc.

.. warning::
   On Linux, if you do not have either *GNOME Keyring*, *kwallet* or another Secret Service-compatible facility available, it will fall back to storing credentials in an encrypted file. This is not quite as secure, but still better than plaintext.

``keyring status`` - Checking authentication status
---------------------------------------------------

::

    halonctl keyring status

The ``status`` subcommand will attempt to authenticate against each configured node, and simply print a yes/no for if each accepted your credentials.

``keyring login`` - Logging into nodes
--------------------------------------

::

    halonctl keyring login

The ``login`` subcommand will go through all of your configured nodes, and ask for a password for any it can't authenticate against.

Note that it will not typically, ask for your password for every node - nodes that are configured as a cluster will share credentials, and they will only be stored once for the first node it. If one node in an otherwise configured cluster rejects your credentials, it will, however, ask for that one node - nodes' individual configuration will override those of the cluster.

``keyring logout`` - Logging out of nodes
-----------------------------------------

::

    halonctl keyring logout

The ``logout`` subcommand will go through all stored credentials, and ask to delete each entry.

.. option:: -y --yes
   
   Don't ask for each node, just delete everything.
