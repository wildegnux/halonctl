``update`` - Run system updates
===============================

::

    halonctl update [subcommand]

The ``update`` module downloads and installs system updates.

.. warning::
   Installing an update causes the node to reboot. You probably don't want all of your nodes to reboot at once - instead, use slicing and stepping to update a few at a time. See :doc:`/basics`.

``update status`` - Check update status
---------------------------------------

::

    halonctl update status

This will print update status for each node, eg. current version and installation progress.

.. note::
   There is currently no way for halonctl to see if an update is available - check the web UI instead.

``update download`` - Starts downloading an update
--------------------------------------------------

::

    halonctl update download

This will make the node(s) start downloading an update. Use ``halonctl update status`` to monitor their progress.

Note that telling an up-to-date node to download an update will cause it to redownload the latest version. This allows you to reinstall a malfunctioning node, and is a feature, not a bug.

``update cancel`` - Aborts an update
------------------------------------

::

    halonctl update cancel

This will make the node(s) abort an ongoing update download, and delete any downloaded data.

``update install`` - Installs an update
---------------------------------------

::

    halonctl update install

Starts the installation process. This can not be aborted until the installation is finished, and the node(s) will drop offline for a few minutes while they reboot to apply it. Use ``halonctl update status`` to check if they're done.
