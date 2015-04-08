halonctl
========

A commandline utility for managing Halon nodes and clusters.

Requirements
------------

* Python 2.7+ or 3.3+

Installation
------------

Simply install the ``halonctl`` package from pip::

   sudo pip install halonctl

Development
-----------

To write your own modules or work on the ``halonctl`` core, clone this repo, and install it in development mode::

   pip install -e .
   
You are strongly recommended to use a `virtualenv <http://virtualenv.readthedocs.org/en/latest/>`_ to create an isolated environment for development.

Links
-----

* `Documentation <http://docs.halon.se/halonctl/>`_
* `Issues <https://github.com/HalonSecurity/halonctl/issues>`_

Changelog
---------

1.4.0 [unreleased]
##################

**Added:**

* ``stat`` module, replacing the old ``queue`` module

**Removed:**

* The ``queue`` module - use ``halonctl queue mail-queue-count`` instead

1.3.2
#####

**Added:**

* ``--version`` flag for checking the program version

**Fixed:**

* A typo causing a crash when an interactive session was resized

1.3.1
#####

**Fixed:**

* The ``cmd`` module's interactive mode not working on Python 2.7

1.3.0
#####

**Added:**

* Native support for Python 3! No more 2to3 nonsense!
* `Full documentation, including docs for module development! <http://halonctl.readthedocs.org/en/latest/>`_
* Interactive mode for the ``cmd`` module - you can now run ``top`` and ``hsh``!
* History querying and printing specific fields with the ``query`` module
* A new "grouped" output mode, usable with the JSON formatter
* A ``--raw`` flag for requesting machine-readable rather than human-readable output
* The ability to "dry run", to test slicing expressions without actually executing anything
* ``--clear-cache`` module for clearing the WSDL cache after node updates

**Changed:**

* Startup is SO MUCH FASTER, especially with lots of nodes
* Slices now start at 1, for ease of use - update your scripts!
* Nodes are now sliced in the order they're listed in the configuration
* Modules and formatters are now a whole lot simpler to build

**Fixed:**

* Occasional 'ghosting' in the ``cmd`` module
* Inconsistent output from the ``query`` module in some circumstances
* A bunch of bugs with the WSDL cache causing the strangest bugs

1.2.2
#####

**Added:**

* More useful error messages for invalid configuration files
* More useful error messages for invalid SSL certificates
* The ability to disable verification of SSL certificates

1.2.1
#####

**Fixed:**

* Crashes when ``query`` got an email with no subject line, or invalid UTF-8

1.2.0
#####

**Added:**

* ``--debug-hql`` flag to the ``query`` module, which prints executed queries
* Errors from non-action ``query`` calls are now printed

**Fixed:**

* Some ``query`` flags not working properly
* ``query`` statements with multiple timestamps not being parsed correctly

1.1.2
#####

**Fixed:**

* A bug sometimes preventing WSDL files from being downloaded

1.1.1
#####

**Fixed:**

* A bug preventing non-ASCII content from being displayed properly on Python 2

1.1.0
#####

**Added:**

* Python 3 support!

**Changed:**

* TextTable dropped for PrettyTable - in other words, tables look different

1.0.4
#####

**Improved:**

* Startup time is now constant, rather than linearly increasing with the number of configured nodes
* Sending Ctrl+C's to commands run through the ``cmd`` module now only takes as long as the slowest node

**Fixed:**

* An awful bug that caused all nodes to report the same data

1.0.3
#####

**Added:**

* ``cmd`` module allowing direct execution of remote shell commmands

**Improved:**

* Performance and reliability in asynchronous dispatches
* WSDL download errors are now reported at startup

1.0.2
#####

**Fixed:**

* Stupid bug preventing dict-style cluster initialization from working

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
