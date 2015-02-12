Module Developer's Guide
========================

.. note::
   This document assumes that you have read :doc:`general`.

What is a module?
-----------------

A module in halonctl is something that can be called as a subcommand, that executes actions and/or produces some kind of output. A module may have subcommands in themselves, where it makes sense (eg. the :doc:`update <../modules/update>` module).

A good module should
''''''''''''''''''''

*Do one thing, and do it well*
   
   Feature bloat is bad. If your module grows to encompass too many responsibilities, consider splitting it up into multiple, smaller modules.

*Produce structured output, and indicate failures gracefully*
   
   Behaving well is important. Scripts as well as humans should be able to use your module, and interpret its output (with some exceptions, such as the :doc:`keyring <../modules/keyring>` module, which would make no sense to script). Prefer using ``yield`` to ``print``, and use exit codes to indicate failures.

A good module should NOT
''''''''''''''''''''''''

*Concern itself with output formatting in any way*
   
   A module should only produce data, it's up to a :doc:`Formatter <formatters>` to make this data take the desired form - this decoupling is what makes it possible to produce optimal output for any format.

*Produce both structured and unstructured output*
   
   This may make sense to a human consumer, but not so much to a machine. If you ``print()`` something, then ``yield`` something else, but JSON output is requested, the yielded data will be rendered as JSON, but the printed data will preceed it and turn it all into garbage in a parser's eyes.

A basic module
--------------------

The base structure for a module looks like this - feel free to use it as a template.

::

	from __future__ import print_function
	import six
	from halonctl.modapi import Module
	
	class MyFancyModule(Module):
	    '''A short description of what it does'''
	    
	    def run(self, nodes, args):
	        yield (u"Cluster", u"Name", u"Result")
	        for node, (code, result) in six.iteritems(nodes.service.someSoapCall()):
	            if code != 200:
	                self.partial = True
	                continue
	            
	            yield (node.cluster, node, result)
	
	module = MyFancyModule()

Breaking it down
----------------

If you understood all of that, feel free to skip this section. If not, here we go::

    from __future__ import print_function
    import six

We support both Python 2 and Python 3. The first line will make ``print()`` a function on Python 2 as well, the second imports the `six <https://pythonhosted.org/six/>`_ library, which helps smooth over some differences between the two - such as Python 3 renaming ``dict.iteritems()`` to ``dict.items()``, removing the old copy-based ``dict.items()`` from the dark days before iterators were a thing.

::

    from halonctl.modapi import Module
    
    class MyFancyModule(Module):
        '''A short description of what it does'''

All modules are expected to inherit from the :class:`Module <halonctl.modapi.Module>` class, which takes care of a lot of basic functionality, most importantly subcommand delegation. It will also help ensuring backwards compatibility.

The description here is called a *docstring* - basically, a string (conventionally triple-quoted to allow for newlines) placed on its own right after a class- or function definition, is assigned to the ``__doc__`` attribute of it. The docstring of a Module, in particular, is used as the description of the module for ``halonctl --help``.

::

    def run(self, nodes, args):

The :func:`run() <halonctl.modapi.Module.run>` function is the main entry point for your module. It's given two arguments: a :class:`NodeList <halonctl.models.NodeList>` of all nodes the user has targeted, and an object containing all registered commandline arguments - see below for more on these.

::

    yield (u"Cluster", u"Name", u"Result")

A module can output either structured or unstructured data. A module that emits structured data should begin by yielding a header for the outputted columns, then yield any number of rows.

As a general rule, always use Unicode strings (``u""``) rather than ASCII strings when outputting something - this may prevent headaches later on.

::

    for node, (code, result) in six.iteritems(nodes.service.someSoapCall()):

This one looks really complicated, but it's really rather simple.

First off, it uses :attr:`nodes.service <halonctl.models.NodeList.service>` (a :class:`SOAP proxy <halonctl.proxies.NodeListSoapProxy>` object for the contained nodes) to make a call to the Halon SOAP API. This returns a dictionary in the form: ``{ node: (code, result) }``, where ``node`` is the node whose response this is, ``code`` is the HTTP status code returned, and ``result`` is the response object.

Typically, ``code`` is one of:

* 200 - All is well, ``result`` is what the API documents
* 403 - Your credentials are invalid, or not allowed to do this
* 404 - There's no such function
* 500 - There was an error
* 0 - The node is unreachable, ``result`` is ``None``

For all statuses except 0 and 200, ``result`` is a SoapFault describing the exact error.

Now, to process this dictionary, it uses ``six.iteritems(d)`` - which calls either ``d.items()`` on Python 3, or ``d.iteritems()`` on Python 2. This will yield a stream of ``(key, value)`` tuples.

These tuples can then be unpacked by specifying the structure, and what to unpack it into. By specifying ``node, (code, result)``, the first item will be put into the ``node`` variable, then the second item will be split into the ``code`` and ``result`` variables.

::

    if code != 200:
        self.partial = True
        continue

This is an important part: if the ``code`` is anything but 200 (success), mark the result at partial, and skip over this node. Marking partial results as such is important, as it allows scripts to properly handle this case!

::

    yield (node.cluster, node, result)

This is an example of yielding a row of output. The items should match the headers emitted at the start of ``run()``.

::

   module = MyFancyModule()

Because a single file may define multiple submodules, you must set a variable named ``module`` to an instance of your main module. If you forget this, halonctl will tell you so.
