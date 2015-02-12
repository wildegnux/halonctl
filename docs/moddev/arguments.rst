Taking arguments
================

Being able to take arguments is good. I can argue for hours about stupid things on the internet, sometimes I even win.

What do you mean wrong kind of argument?

Anyways, to be able to take *commandline* arguments in a module, you simply have to define a function along the lines of this::

    def register_arguments(self, parser):
        parser.add_argument('--test',
            help=u"this is a test flag")
        parser.add_argument('-y', '--yes', action='store_true',
            help=u"don't ask, just do the thing")

Now, if you run ``halonctl mymodule --help``, you'll see these two new arguments listed. It's not harder than that.

To access the passed values, you can use the ``args`` parameter passed to ``run()``::

    def run(self, nodes, args):
        if not args.yes and not ask_confirm(u"Really do the thing?"):
            return
        
        print("Test is: {0}".format(args.test))

For more details, refer to `the python documentation for the argparse module <https://docs.python.org/2/library/argparse.html#the-add-argument-method>`_.
