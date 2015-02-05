``status`` - Node Status
========================

The ``status`` module is used to quickly check the status of all configured nodes - if they're online, and their uptime.

::

    halonctl status [-v|--verbose]

Commandline Arguments
---------------------

.. option:: -v --verbose
    
    Generate verbose output - formatting for machine consumption and accuracy rather than human-friendly abstractions.
    
    This will cause timestamps to be printed as UNIX timestamps, and node statuses as their literal status codes, rather than interpretations.
