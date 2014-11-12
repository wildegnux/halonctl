from halon.modules import Module

class KeyringStatusModule(Module):
    '''Checks the authorization status of all nodes'''
    
    def run(self, nodes, args):
        yield ('Cluster', 'Name', 'Address', 'Authorized?')
        
        for node, result in nodes.service.login().iteritems():
            if result[0] != 0:
                self.partial = True
            
            if result[0] == 200:
                status = "Yes"
            elif result[0] == 401:
                status = "No"
            else:
                status = "-"
            
            yield (node.cluster.name, node.name, node.host, status)

class KeyringLoginModule(Module):
    '''Attempts to log in to the node(s)'''
    
    def run(self, nodes, args):
        pass

class KeyringLogoutModule(Module):
    '''Deletes stored credentials for the node(s)'''
    
    def run(self, nodes, args):
        pass

class KeyringModule(Module):
    '''Manages the keyring (credential store)'''
    
    submodules = {
        'status': KeyringStatusModule(),
        'login': KeyringLoginModule()
    }

module = KeyringModule()
