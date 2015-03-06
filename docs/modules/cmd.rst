``cmd`` - Run remote commands
=============================

::

   halonctl cmd [-i|--interactive] [command...]

The ``cmd`` module runs a shell command. Refer to the individual commands' manuals for details on their flags and invocations.

Halon runs FreeBSD (currently version 10.1) under the hood. Other \*nix flavors (such as Linux) may have subtle, but important, differences in command invocations.

The module will wait for the command to exit before printing any output, unless ``Ctrl+C`` is pressed, in which case it will send a SIGTERM to the remote process. If the command does not terminate in a timely fashion, you can press ``Ctrl+C`` again to forcibly terminate the remote process.

.. note::
   Everything after the ``cmd`` in the invocation of this module is passed straight to the commandline. Normal escaping rules apply.

Interactive Mode
----------------

.. warning::
   Due to technical limitations, Interactive Mode is not available on Windows.

By default, the ``cmd`` module will run the command on each matched node, and print the results, node-by-node. But some commands don't work this way - they let you interact with them, and thus need an interactive session. This is what the ``-i`` (``--interactive``) flag is for.

In Interactive Mode, you can only target a single node - if your filters match several, you're presented with a menu from which you can use your arrow keys to choose which one to use.

Output from the remote command in Interactive Mode will be piped directly to your terminal, which will be kept informed of the size of your window, and your input is sent directly. This means that Ctrl+C and the like will not work as it does in noninteractive mode - it will instead be sent to the other side, and will trigger the signal there.

Input **will** have some amount of latency, so give your keypresses a moment to register before treating them as lost.

Available Commands
------------------

The most up-to-date list can always be viewed under ``System -> Commands`` in the web UI.

* `arp <https://www.freebsd.org/cgi/man.cgi?query=arp&manpath=FreeBSD+10.1-RELEASE>`_
* `host <https://www.freebsd.org/cgi/man.cgi?query=host&manpath=FreeBSD+10.1-RELEASE>`_
* `ping <https://www.freebsd.org/cgi/man.cgi?query=ping&manpath=FreeBSD+10.1-RELEASE>`_
* `ping6 <https://www.freebsd.org/cgi/man.cgi?query=ping6&manpath=FreeBSD+10.1-RELEASE>`_
* `smtpping <https://github.com/halonsecurity/smtpping>`_
* `traceroute <https://www.freebsd.org/cgi/man.cgi?query=traceroute&manpath=FreeBSD+10.1-RELEASE>`_
* `traceroute6 <https://www.freebsd.org/cgi/man.cgi?query=traceroute6&manpath=FreeBSD+10.1-RELEASE>`_
* `tcpdump <https://www.freebsd.org/cgi/man.cgi?query=tcpdump&manpath=FreeBSD+10.1-RELEASE>`_
* `df <https://www.freebsd.org/cgi/man.cgi?query=df&manpath=FreeBSD+10.1-RELEASE>`_
* `ifconfig <https://www.freebsd.org/cgi/man.cgi?query=ifconfig&manpath=FreeBSD+10.1-RELEASE>`_
* `iostat <https://www.freebsd.org/cgi/man.cgi?query=iostat&manpath=FreeBSD+10.1-RELEASE>`_
* `mfiutil <https://www.freebsd.org/cgi/man.cgi?query=mfiutil&manpath=FreeBSD+10.1-RELEASE>`_
* `sysctl <https://www.freebsd.org/cgi/man.cgi?query=sysctl&manpath=FreeBSD+10.1-RELEASE>`_

Interactive Commands
--------------------

These commands are interactive, and will only work properly when run in interactive mode.

* `nc <https://www.freebsd.org/cgi/man.cgi?query=nc&manpath=FreeBSD+10.1-RELEASE>`_
* `telnet <https://www.freebsd.org/cgi/man.cgi?query=telnet&manpath=FreeBSD+10.1-RELEASE>`_
* hsh - `HSL <http://wiki.halon.se/HSL>`_ shell
* `login <https://www.freebsd.org/cgi/man.cgi?query=login&manpath=FreeBSD+10.1-RELEASE>`_
* `top <https://www.freebsd.org/cgi/man.cgi?query=top&manpath=FreeBSD+10.1-RELEASE>`_

Support Commands
----------------

These are internal tools to solve very specific problems, and should generally not be used.

* lostfiles - interactive recovery program
* truncsvn - truncates configuration history
