import signal
import inspect
import socket
from collections import OrderedDict
from base64 import b64encode, b64decode
from natsort import natsorted
from tornado.ioloop import IOLoop
from tornado.concurrent import *
from concurrent.futures import ThreadPoolExecutor
from tornado import gen
from tornado.httpclient import *

thread_pool_executor = ThreadPoolExecutor(64)



class NodeSoapProxy(object):
    '''SOAP call proxy.
    
    This allows you to make SOAP calls as easily as calling a normal Python
    function.'''
    
    def __init__(self, node):
        self.node = node
    
    def __getattr__(self, name):
        def _soap_proxy_executor(*args, **kwargs):
            context = self.node.make_request(name, *args, **kwargs)
            if not context:
                return (0, "Couldn't connect")
            
            http_client = HTTPClient()
            request = self.node.make_tornado_request(context)
            try:
                result = http_client.fetch(request)
                return context.process_reply(result.body, result.code, result.reason)
            except HTTPError as e:
                return context.process_reply(e.response.body if getattr(e, 'response', None) else None, e.code, e.message)
            except socket.error as e:
                return (0, e.message)
            finally:
                http_client.close()
        
        return _soap_proxy_executor

class NodeListSoapProxy(object):
    '''Multi-node SOAP call proxy.
    
    Similar to NodeSoapProxy, this allows you to easily make SOAP calls, but
    additionally, these calls are made asynchronously to any number of nodes.
    
    Compared to looping through a list of nodes, this effectively reduces call
    time from O(n) to O(1).'''

    def __init__(self, nodelist):
        self.nodelist = nodelist

    def __getattr__(self, name):
        def _soap_proxy_executor(*args, **kwargs):
            @gen.coroutine
            def _inner():
                results = yield {
                    node: thread_pool_executor.submit(getattr(node.service, name), *args, **kwargs)
                    for node in self.nodelist
                }
                raise gen.Return(OrderedDict(natsorted(results.items(), key=lambda t: [t[0].cluster.name, t[0].name])))
            return IOLoop.instance().run_sync(_inner)
        return _soap_proxy_executor

class CommandProxy(object):
    '''Proxy for a command executing on a remote server.
    
    This abstracts away all the messy commandRun()/commandPoll() logic, letting
    you treat a remote process as an interactive iterator.'''
    
    def __init__(self, node, cid):
        self.node = node
        self.cid = cid
    
    def __iter__(self):
        return self
    
    # Python 3 compatibility
    def __next__(self):
        return self.next()
    
    def next(self):
        while True:
            code, data = self.node.service.commandPoll(commandid=self.cid)
            
            if code == 200:
                # If the process is still running, but hasn't given any output
                # since we asked last time, try again until something happens
                if not hasattr(data, 'item'):
                    continue
                
                return ''.join([b64decode(item) for item in data.item])
            else:
                raise StopIteration()
    
    def all(self):
        '''Waits for the process to exit, and returns all of its output.'''
        
        return ''.join(self)
    
    def write(self, data):
        '''Writes some data to the remote process' stdin.'''
        
        return self.node.service.commandPush(commandid=self.cid, data=b64encode(data))
    
    def signal(self, sigid):
        '''Sends a signal to the remote process.'''
        
        try:
            # This will throw a ValueError if the string is not numeric
            sig = int(sigid)
        except ValueError:
            # If it's not, try to get the signal by name from the signal module
            sig = int(getattr(signal, sigid.upper()))
        
        return self.node.service.commandSignal(commandid=self.cid, signal=sig)
    
    def stop(self):
        '''Terminates the remote process.'''
        
        return self.node.service.commandStop(commandid=self.cid)
    
    def __str__(self):
        return self.all()
