General Information
===================

Here follows some information you should probably know before you start developing your own module.

What is a module?
-----------------

A module in halonctl is something that can be called as a subcommand, that executes actions and/or produces some kind of output. A module may have subcommands in themselves, where it makes sense (eg. the :doc:`update <../modules/update>` module).

A few things to keep in mind:

**DO: One thing, and do it well**
   
   Feature bloat is bad. If your module grows to encompass too many responsibilities, consider splitting it up into multiple, smaller modules.

**DO: Produce structured output, and indicate failures gracefully**
   
   Behaving well is important. Scripts as well as humans should be able to use your module, and interpret its output (with some exceptions, such as the :doc:`keyring <../modules/keyring>` module, which would make no sense to script). Prefer using ``yield`` to ``print``, and use exit codes to indicate failures.

**DON'T: Concern yourself with output formatting in any way**
   
   A module should only produce data, it's up to a Formatter to make this data take the desired form - this decoupling is what makes it possible to produce optimal output for any format.

**DON'T: Produce both structured and unstructured output**
   
   This may make sense to a human consumer, but not so much to a machine. If you ``print()`` something, then ``yield`` something else, but JSON output is requested, the yielded data will be rendered as JSON, but the printed data will preceed it and turn it all into garbage in a parser's eyes.

Understanding Module Loading
----------------------------

Before you can get started, it'll help if you understand how module loading is done.

At startup, halonctl searches through three paths for directories named ``modules`` and ``formatters``. It then goes through each of these, and loads any python files it can find.

Modules are registered using their module name (filename without extension) as their ID, with one exception: if the name has trailing underscores (``_``), they will be stripped. This is useful for such modules as the built-in ``json`` formatter, which is defined in a file named ``json_.py``, to avoid a collission with Python's built-in ``json`` module.

.. warning::
   There's a caveat to this: if any of these directories contain files which are recognized as Python modules (files ending with ``.py``, and directories containing a ``__init__.py``), but that contain syntax errors or garbage, the program will fail to start.

The paths currently searched are:

* Halonctl's installation directory (thus built-in formatters and modules are registered first)
* ``~/halonctl``
* ``~/.halonctl`` (hidden on \*nix-like systems)

Developing personal modules
---------------------------

To develop a module for personal use, simply drop a ``.py`` file into one of the directories listed above, in a subdirectory named after the type, and start working. If the module doesn't contain garbage, it should be immediately picked up.

If it does not appear to be picked up (not listed in ``halonctl --help``), make sure you're placing it in the right place: for instance, a module called ``hello_world`` could, on Mac OS X, go in ``/Users/myusername/halonctl/modules/hello_world.py``.

Getting your module into the core
---------------------------------

If you've developed a module, that does something useful and doesn't destroy everything in the process, you may want to consider pushing it into the core. We'll be happy to accept it - simply fork `the repository <https://github.com/HalonSecurity/halonctl>`_ and send a pull request that includes it.

However, before doing so, there are a few basic rules you should adhere to:

**Thou shalt provide adequate guidance**

	Documentation is important.
	
	Write a quick guide explaining how to use your module - no need to write an essay, just enough to understand how it works. Remember that your audience is fairly technical systems administrators, so feel free to use technical language where appropriate.
	
	Just as important is that you use comments in your code where appropriate. Don't comment every line, that's just annoying, but if something looks unclear, a quick comment might help.

**Thou shalt not abandon thy past nor future**

	We support both Python 2 and 3, and we'd like to continue doing so for the foreseeable future.
	
	We use ``from __future__ import print_function`` to transform the ``print`` statement into a function, and use the excellent `six <https://pythonhosted.org/six/>`_ library to smooth over most of the remaining differences between the two versions.
	
	Please test your module briefly with both versions, if at all possible.

**Thou shalt avoid causing unpleasantries**

	Needless to say, your module should make a best effort to avoid destroying the user's data, even by accident.
	
	A good way to do this is to not actually touch anything unless certain commandline flags are specified, and default to just printing things out - or complaining about the lack of a flag, if that wouldn't make any sense. You may also choose to ask for permission before performing destructive operations.
	
	If you opt for the latter, make sure you include a flag (by convention ``-y|--yes``) that assumes "Yes" to all input. This helps a bunch when scripting.

**Thou shalt not announce falsehoods**

	Make sure your command provides accurate output and, just as importantly, exit codes. The latter is especially easy to forget - are you setting ``self.exitcode`` if the command fails for whatever reason, and ``self.partial`` if you couldn't get all the information you asked for?
	
	Exit codes are important when scripting, because it lets you tell very easily if an operation succeeded, and handle gracefully cases where it does not.
