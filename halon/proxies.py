from tornado.ioloop import IOLoop
from tornado.concurrent import *
from concurrent.futures import ThreadPoolExecutor
from tornado import gen
from tornado.httpclient import *

thread_pool_executor = ThreadPoolExecutor(64)



class NodeSoapProxy(object):
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
    '''Proxy for a NodeList that allows grouped SOAP calls.'''

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
                raise gen.Return(results)
            return IOLoop.instance().run_sync(_inner)
        return _soap_proxy_executor
