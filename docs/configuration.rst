Configuration
=============

The very first step to using ``halonctl`` is to write a configuration file, so that the program knows how to connect to your servers. Configuration files are normal JSON files, and a sample configuration file (provided with the source as ``halonctl.sample.json``) looks like this::

    {
        "nodes": {
            "n1": "admin@10.2.0.30",
            "n2": "10.2.0.31"
        },
        "clusters": {
            "mycluster": [ "n1", "n2" ]
        }
    }

Configuration files are conventionally named ``halonctl.json``, though you may keep multiple configuration files and specify which one to use with the ``-C/--config`` flag at runtime, if you prefer. For instance, if you're a contractor for multiple companies using Halon nodes, it may be convenient to have one configuration file per client.

By default, if that flag is not used, it will try the following locations in order (where ``~`` refers to your home directory, eg. ``/Users/yourusername/`` or ``/home/yourusername/``):

#. ``/path/to/halonctl/halonctl.json``
#. ``~/.config/halonctl.json``
#. ``~/halonctl.json``
#. ``~/.halonctl.json``
#. ``/etc/halonctl.json``

Nodes
-----

The most essential part of the configuration file is the ``nodes`` entry. This lists all available nodes, and everything you need to connect to it. Each entry has the following format, where all parts in brackets are optional::

    "nodename": "[scheme://][user[:pass]@]hostname"

.. option:: nodename
   
   An arbitrary name for the node. This can be anything, as it's only used by ``halonctl`` itself to identify nodes. The only restriction is that two nodes obviously must not share the same name, or it'd be impossible to tell which one you meant.
   
   To group multiple nodes together, see Clusters below.

.. option:: scheme
   
   The URL scheme (protocol) to connect over - ``http`` or ``https``.
   
   Defaults to ``http``, but ``https`` is recommended.

.. option:: user
   
   The username used to connect to the server.
   
   Note that you do not have to specify this for all nodes; if they're configured in a cluster (see below), all included nodes can share credentials.
   
.. option:: pass
   
   The corresponding password for the server. Has the same behavior in clusters as the username.
   
   Note that it's not recommended to specify passwords in your configuration file, instead, use the ``keyring`` module to securely store passwords in your system's usual key store.
   
.. option:: hostname
   
   The hostname the node can be reached at. Can be either a DNS name (like ``a.mydomain.com``) or an IP (``10.2.0.30``).
   
   Note that passwords are keyed to the hostname when the ``keyring`` module is used, as they're not expected to change often.

Clusters
--------

An entirely optional, but higly recommended, part of the configuration is the one for Clusters. If you have your nodes set up in a cluster, you can use this to target entire clusters at once. If you have only a handful of nodes in none or a single cluster, this may not be of too much use, but if you manage more than one cluster, this may be of interest to you.

As an aside, configured clusters do not necessarily have to describe actual, server-side clusters, and thus they can be used simply for grouping related nodes and orchestrating them as one unit. A node should not belong to more than one cluster, however.

Each cluster entry can actually be specified in one of two ways, either in list form::

    "name": [ "node1", "node2", "node3" ]

Or in dictionary form::

    "name": {
        "nodes": [ "node1", "node2", "node3" ],
        "username": "admin",
        "password": "password"
    }

Usernames and passwords for nodes belonging to clusters try to do something clever:

* If a node lacks either a username or password, but the cluster doesn't, the cluster's credentials are used
* If a node or its cluster has a username, but neither has a password, it will attempt to load it from the user's keyring (see the ``keyring`` module for more information)
* If a cluster doesn't have a username or password, but a contained node does, the first found set of credentials are used for the entire cluster
* The node's individual credentials always take priority over the cluster's

Due to this, you can either specify a username (and password) on the cluster or on one of the contained nodes, and it will attempt to do the right thing. Again, specifying a password in a configuration file is not recommended, but the possibility is there.

.. option:: name
   
   An arbitrary, unique name for a cluster. This can be anything, but must be unique.
   
.. option:: nodes
   
   A list of node names that belong to the cluster.
   
.. option:: username
   
   A username used for all nodes in the cluster, unless they provide their own.
   
   Falls back to the username for the first found node that provides one.
   
.. option:: password
   
   A password used for all nodes in the cluster, behaves just like username.
   
   You're probably tired of seeing this by now, but you really should use the ``keyring`` module over this.

Others
------

Other configuration settings can be added at the end of the file. These are all optional, and have default values - which also means you won't get an error if you mistype the key name, it'll just not take effect.

.. option:: verify_ssl
   
   Enable or disable verification of SSL certificates. Defaults to ``true``.
   
   This can also be set to a string, which should be a path to a .pem file from which a trusted certificate is loaded. This is useful especially if you're using self-signed certificates.
