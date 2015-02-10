from __future__ import print_function
import six

class Module(object):
	'''Base class for all modules.
	
	:ivar int exitcode: Change the program's exit code, to signal an error. (default: 0)
	:ivar bool partial: Set to True if the results are partial, will cause the program to exit with code 99 unless ``--ignore-partial`` is specified on the commandline.
	:ivar dict submodules: If this module has any submodules of its own, specify them as ``{ 'name': ModuleInstance() }``, and do not reimplement :func:`register_arguments` or :func:`run`.
	'''
	
	exitcode = 0
	partial = False
	
	submodules = {}
	
	def register_arguments(self, parser):
		'''Subclass hook for registering commandline arguments.
		
		Every module has its own subparser, and thus does not have to worry
		about clobbering other modules' arguments by accident, but should avoid
		registering arguments that conflict with halonctl's own arguments.
		
		Example::
		
		    def register_arguments(self, parser):
		        parser.add_argument('-t', '--test',
		            help="Lorem ipsum dolor sit amet")
		
		See Python's argparse_ module for more information, particularly the
		part about subcommands_.
		
		The default implementation registers any subcommands present.
		
		:param argparse.ArgumentParser parser: The Argument Parser arguments should be registered on
		
		.. _argparse: https://docs.python.org/2/library/argparse.html
		.. _subcommands: https://docs.python.org/2/library/argparse.html#sub-commands
		'''
		if self.submodules:
			subparsers = parser.add_subparsers(dest=type(self).__name__ + '_mod_name', metavar='subcommand')
			subparsers.required = True
			for name, mod in six.iteritems(self.submodules):
				p = subparsers.add_parser(name, help=mod.__doc__)
				p.set_defaults(**{type(self).__name__ + '_mod': mod})
				mod.register_arguments(p)
	
	def run(self, nodes, args):
		'''
		Invoked when halonctl is run with the module's name as an argument, and
		should contain the actual command logic.
		
		To output data, the preferred way is to ``yield`` a table, one row at a
		time, with the first row being the header. This will, by default,
		output an ASCII art table, but will also allow other formatters to
		correctly process the data::
		
		    def run(self, nodes, args):
		        # First, yield a header...
		        yield (u"Cluster", u"Node", u"Result")
		        
		        # Make a call on all given nodes
		        for node, result in six.iteritems(nodes.service.someCall(arg=123)):
		            # Mark the results as partial if a node isn't responding
		            if result[0] != 200:
		                self.partial = True
		                continue
		            
		            # Yield a row with the response
		            yield (node.cluster.name, node.name, results[1])
		
		Of course, if your command's purpose isn't to retrieve data, you should
		not do this, and instead adhere to the "rule of silence"; use prints,
		and say nothing unless there's an error::
		
		    def run(self, nodes, args):
		        for node, result in six.iteritems(nodes.service.someCall(arg=123)):
		            if result[0] != 200:
		                print "Failure on {node}: {result}".format(node=node, result=result[1])
		
		The default implementation simply delegates to a subcommand.
		'''
		
		if self.submodules:
			return getattr(args, type(self).__name__ + '_mod').run(nodes, args)

class Formatter(object):
	'''Base class for all formatters.
	
	:ivar bool raw: Whether the output should be machine- rather than human-friendly
	'''
	
	raw = False
	
	def run(self, data):
		'''
		Calls :func:`format` with data prepared by :func:`format_item`.
		
		Override if you'd like to customize the entire formatting process, such
		as if you'd prefer to work with another data structure than a
		two-dimensional list.
		'''
		
		return self.format([[self.format_item(item) for item in row] for row in data])
	
	def format(self, data):
		'''
		Takes a blob of data, and transforms it into the desired form.
		
		What exactly this entrails is obviously up to the formatter, but it
		should return a string one way or another.
		
		Should be overridden in subclasses.
		'''
		
		raise NotImplementedError()
	
	def format_item(self, item):
		'''
		Takes an emitted item, and returns a more output-friendly form.
		
		The default implementation does the following transformations:
		
		* If self.raw is True, no transformations are made
		* None is transformed into "-"
		* Booleans are transformed into "Yes"/"No"
		* Everything else is stringified
		'''
		
		if self.raw:
			return item
		elif item is None:
			return u"-"
		elif item is True:
			return u"Yes"
		elif item is False:
			return u"No"
		return six.text_type(item)

class DictFormatter(Formatter):
	'''
	Convenience subclass of :class:`Formatter` that works with dicts.
	
	The :func:`run() <Formatter.run>` method is customized to use a list of
	dicts, rather than lists. The dict's keys are generated from the headers,
	using the new :func:`format_key` method.
	'''
	
	def run(self, data):
		keys = [self.format_key(header) for header in data[0]]
		return self.format([{keys[i]: row[i] for i in six.moves.xrange(len(row))} for row in data[1:]])
	
	def format_key(self, header):
		'''
		Takes a header, and returns the key it should map to in the dictionary.
		
		The default implementation simply calls :func:`format_item()
		<Formatter.format_item>`.
		'''
		return self.format_item(header)
