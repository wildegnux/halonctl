``shell`` - Interactive Python shell
====================================

::

    halonctl shell

The ``shell`` module opens an interactive Python interpreter, in the same context as :func:`Module.run() <halonctl.modapi.Module.run>`.

Provided variables
------------------

* ``nodes`` - a :class:`NodeList <halonctl.models.NodeList>` containing all matched nodes
* ``args`` - passed commandline arguments
