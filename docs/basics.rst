Basic Usage
===========

Once halonctl is :doc:`configured <configuration>`, you can start using it right away. The general syntax for a halonctl invocation is::

    halonctl [--global-flag] command [--flag]

Note that there is a distinction between global- and command flags: global ones must be given before the command name, while command flags are given after it.

Authentication
--------------

Before you can do anything with your nodes, you must authenticate with them. While it is possible to enter your password for each node in the configuration file, halonctl provides a more secure means of storing it: your system's keychain, through the ``keyring`` module.

To use this, remove any passwords you may have entered in your configuration file, and run::

    halonctl keyring login

This will cause it to go through each of your configured nodes, and ask for your password. If you've forgotten the password for a node, feel free to just press enter, and it will be skipped.

However, since entering your password over and over isn't a lot of fun, and because clusters generally use the same login credentials throughout, it's a bit smarter than that: it will ask for your password once per cluster, then attempt to log in with the same ones to the other nodes in it, only asking again for nodes that reject this login. This means you can have a hundred nodes all using the same login, yet only have to enter your password once.

Now, to verify that your login works for all your nodes, run the following::

    halonctl keyring status

If all went well, you should see a list of all of your nodes, with the last column saying "Yes" (or possibly "Error" if one of them is down). If you add a new node to your configuration file, which uses a different set of credentials from the others, that node will say "No" until you've logged in to it.

Finally, if you want to delete your credentials for a node, simply run::

    halonctl keyring logout

This will ask you for each node if you'd like to delete the stored credentials. Again, as credentials are shared throughout a cluster, you only have to delete shared credentials once.

Selecting Nodes
---------------

By default, commands will run against all available nodes. But what if you want to run a command against only a subset of your available nodes? Maybe you want to roll out an update, but you want to test it on a single node first to make sure it works at all.

Enter: the ``--node`` (``-n``) and ``--cluster`` (``-c``) flags.

To run the ``status`` command against the ``n1`` and ``n3`` nodes, you would do something like this::

    halonctl -n n1 -n n3 status

And to run it against all nodes in the cluster ``c1``, leaving your other clusters alone::

    halonctl -c c1 status

They can be combined - you could target all nodes in ``c2`` as well as ``n1``::

    halonctl -c c2 -n n1 status

Dry Runs
--------

If you want to see which nodes would be affected by a command without actually executing it, you can use the ``--dry`` (``-d``) flag::

    $ halonctl --dry status
    This action would have affected:
      - n1 (c1)
      - n2 (c1)

Useful if you want to perfect your filters before executing a potentially dangerous operation.

Slicing
-------

So far so good. But what if I want to do something with the first five nodes of the ``c1`` cluster?

You could list them all, but that would end up in a lot of typing. Instead, halonctl lets you apply a "slice" to the selected nodes, to cut the selection any way you like. The slice consists of up to three parts, separated by a ``:``, inspired by Python's slice operator.

.. note::
   There's one big difference compared to Python's slice operator: **indices start at 1**. This is to allow the slices to be read more naturally by non-programmers.

The simplest form of a slice is a single number. This will execute the ``status`` command against the first node::

    halonctl -s 1 status

It can also be combined with the ``-c`` flag - this will target the 3rd node of the ``c2`` cluster::

    halonctl -c c2 -s 3 status

For targeting multiple nodes, you can use a range; these are both equivalent, and will target the first, second and third configured nodes - the 1 is implicit here::

    halonctl -s 1:3 status
    halonctl -s :3 status

This will instead start with the 3rd node, and continue until the last one::

    halonctl -s 3:

Obviously, you can also do this to skip the first 3, and target the 4th, 5th and 6th node::

    halonctl -s 4:6 status

Stepping
--------

The slice actually has a less known third member: the step. By default, this is ``1``, which will make it go through your nodes in the order ``1, 2, 3, ...`` - exactly how you'd expect it to. But this can be changed::

    halonctl -s ::-1 status

This will cause it to go through each of your nodes... backwards. While this is not particularly useful, setting it to something like 2 can be - this will skip over every other node::

    halonctl -s ::2 status

Why would you ever want this? Well, imagine you were rolling out an update. You'd first start by doing::

    halonctl -c mycluster update download

Now, you obviously don't want to take down your entire cluster by restarting all nodes for updates at once. Instead, use the Step to update every *other* node::

    halonctl -c mycluster -s ::2 update install

When they've all rebooted and are up and running again, you can skip the first node (start on the 2nd), and update the other half::

    halonctl -c mycluster -s 2::2 update install

Choosing an output format
-------------------------

As you may have noticed, most commands will print a neat little ASCII art table. But this isn't the only output format available - currently, halonctl ships with three formatters:

* ``table`` - An ASCII table (default)
* ``json`` - Good ol' `JSON <http://en.wikipedia.org/wiki/JSON>`_ blobs
* ``csv`` - `CSV <http://en.wikipedia.org/wiki/Comma-separated_values>`_, for MS Excel and the like

You can pick an output format with the ``-f`` flag. [#statusv]_ ::

    $ halonctl status
    Cluster  Name  Address    Uptime   Status
    c1       n1    10.2.0.30  5 hours  OK
    c1       n2    10.2.0.31  8 days   OK

::

    $ halonctl -f json status -v
    [
        {
            "address": "10.2.0.30",
            "cluster": "c1",
            "name": "n1",
            "status": 200,
            "uptime": 20601
        },
        {
            "address": "10.2.0.31",
            "cluster": "c1",
            "name": "n2",
            "status": 200,
            "uptime": 710652
        }
    ]

::

    $ halonctl -f csv status -v
    Cluster,Name,Address,Uptime,Status
    c1,n1,10.2.0.30,20640,200
    c1,n2,10.2.0.31,710691,200

If you want output in a format not (yet) supported, writing an output formatter is rather simple (TODO: Document this).

.. [#statusv] ``-v`` is a ``status``-specific flag, that makes it output machine-readable rather than human-readable data
