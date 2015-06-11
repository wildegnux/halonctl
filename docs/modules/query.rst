``query`` - Query messages
==========================
::

    halonctl query [HQL query]

The ``query`` module queries mail, either from the queue (default) or history, and optionally performs actions on them. For more information about HQL query syntax, see `this wiki page <http://wiki.halon.se/Search_filter>`_.

General
-------

.. option:: -r --history
   
   Query the message history, rather than queued messages.

.. option:: -n --limit n
   
   Show a maximum of *n* results.
   
   The shorthand form is ``-n`` rather than ``-l`` to mimic the ``tail`` command.

.. option:: -o --offset n
   
   Skip *n* results. Useful in conjunction with ``--limit``.

.. option:: -c --count
   
   Show total number of results (not restricted by ``--limit``).

Timestamps
----------

Aside from taking times as UTC UNIX Timestamps, ``halonctl`` offers a simpler way to specify timestamps::

    {YYYY-mm-dd HH:mm:ss}

Note that for safety reasons, you must specify which timezone you're referring to when using this format - it'd be pretty bad if you ended up targeting the wrong set of data, because the server and your computer are in different timezones.

.. option:: -t --timezone
   
   Any placeholders in the query are in this timezone, specified as a UTC offset.
   
   Example: ``-t 1`` would mean the timestamp is in UTC+1/GMT+1 (Sweden, Germany, ...)

.. option:: -u --utc
   
   Alias for ``-t 0``.

Actions
-------

You can specify an action to be taken on the matched messages, instead of just displaying a list of them. Only one action can be used at a time.

.. option:: --delete
   
   Delete all matched messages on the spot.
   
   There is no way to un-delete a deleted message, so use this with caution.

.. option:: --deliver
   
   Attempt to deliver all matched messages immediately.

.. option:: --deliver-duplicate
   
   Attempt to deliver all matched messages immediately, but keep a copy in the queue.
   
   Useful for certain kinds of quarantine or backup/archive setups.

.. option:: -y --yes
   
   Don't ask for confirmation before performing actions on **all** messages.
   
   Only use this if you're absolutely sure what you're doing.

Formatting
----------

.. option:: -f --fields f1,f2,f3,...
   
   Display the given fields (columns), separated by comma (``,``).
   
   The special value ``-`` will display ALL available fields, including ones hidden by default.

Others
------

.. option:: --debug-hql
   
   When this is specified, the full, timestamp-expanded HQL query is printed to the console. Nothing is executed.
   
   Useful mainly for debugging.
