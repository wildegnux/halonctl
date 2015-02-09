``cmd`` - Run remote commands
=============================

::

   halonctl cmd [command...]

The ``cmd`` module runs a shell command. Halon runs FreeBSD (currently version 10.1) under the hood, and you should refer to `their man pages <https://www.freebsd.org/cgi/man.cgi>`_ for details on the invocation of these commands. Other \*nix flavors (such as Linux) may have subtle, but important, differences in command invocations.

The module will wait for the command to exit before printing any output, unless ``Ctrl+C`` is pressed, in which case it will send a SIGTERM to the remote process. If the command does not terminate in a timely fashion, you can press ``Ctrl+C`` again to forcibly terminate the remote process.

.. note::
   Everything after the ``cmd`` in the invocation of this module is passed straight to the command, normal escaping rules apply.

Available Commands
------------------

The most up-to-date list can always be viewed under ``System -> Commands`` in the web UI.

* `arp <https://www.freebsd.org/cgi/man.cgi?query=arp&manpath=FreeBSD+10.1-RELEASE>`_
* dns - legacy alias for `host <https://www.freebsd.org/cgi/man.cgi?query=host&manpath=FreeBSD+10.1-RELEASE>`_
* `nc <https://www.freebsd.org/cgi/man.cgi?query=nc&manpath=FreeBSD+10.1-RELEASE>`_
* `ping <https://www.freebsd.org/cgi/man.cgi?query=ping&manpath=FreeBSD+10.1-RELEASE>`_
* `ping6 <https://www.freebsd.org/cgi/man.cgi?query=ping6&manpath=FreeBSD+10.1-RELEASE>`_
* `smtpping <https://github.com/halonsecurity/smtpping>`_
* `traceroute <https://www.freebsd.org/cgi/man.cgi?query=traceroute&manpath=FreeBSD+10.1-RELEASE>`_
* `traceroute6 <https://www.freebsd.org/cgi/man.cgi?query=traceroute6&manpath=FreeBSD+10.1-RELEASE>`_
* `tcpdump <https://www.freebsd.org/cgi/man.cgi?query=tcpdump&manpath=FreeBSD+10.1-RELEASE>`_
* `telnet <https://www.freebsd.org/cgi/man.cgi?query=telnet&manpath=FreeBSD+10.1-RELEASE>`_
* `df <https://www.freebsd.org/cgi/man.cgi?query=df&manpath=FreeBSD+10.1-RELEASE>`_
* hsh - `HSL <http://wiki.halon.se/HSL>`_ shell
* `ifconfig <https://www.freebsd.org/cgi/man.cgi?query=ifconfig&manpath=FreeBSD+10.1-RELEASE>`_
* `iostat <https://www.freebsd.org/cgi/man.cgi?query=iostat&manpath=FreeBSD+10.1-RELEASE>`_
* `login <https://www.freebsd.org/cgi/man.cgi?query=login&manpath=FreeBSD+10.1-RELEASE>`_
* lostfiles - interactive recovery program [#lostfiles]_
* `mfiutil <https://www.freebsd.org/cgi/man.cgi?query=mfiutil&manpath=FreeBSD+10.1-RELEASE>`_
* `sysctl <https://www.freebsd.org/cgi/man.cgi?query=sysctl&manpath=FreeBSD+10.1-RELEASE>`_
* `top <https://www.freebsd.org/cgi/man.cgi?query=top&manpath=FreeBSD+10.1-RELEASE>`_
* truncsvn - truncates configuration history [#truncsvn]_

.. [#lostfiles] Typically run automatically in the background - you only have to invoke it manually in case of database corruption
.. [#truncsvn] This solves a very specific problem, and you will likely never to use it
