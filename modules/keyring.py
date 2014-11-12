import getpass
import keyring
from halon.modules import Module

class KeyringStatusModule(Module):
    '''Checks the authorization status of all nodes'''
    
    def run(self, nodes, args):
        yield ('Cluster', 'Name', 'Address', 'Authorized?')
        
        for node, result in nodes.service.login().iteritems():
            if result[0] != 200:
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
        for node in nodes:
            prefix = "%s / %s (%s)" % (node.cluster.name, node.name, node.host)
            if not node.username:
                print prefix + " - No username configured for node or cluster"
                continue
            
            result = node.service.login()[0]
            if result == 0:
                print prefix + " - Node is unreachable :("
            elif result == 200:
                # Follow the good ol' rule of silence
                pass
            elif result == 401:
                print prefix + " - Enter password (blank to skip):"
                while True:
                    password = getpass.getpass("%s@%s> " % (node.username, node.host))
                    if password == "":
                        break
                    
                    # Try to use the same login for the entire cluster, but make
                    # sure to at least use it for this node
                    node.password = password
                    node.cluster.password = password
                    result = node.service.login()[0]
                    if result == 200:
                        keyring.set_password(node.host, node.username, password)
                        break
                    elif result == 401:
                        print "Invalid login, try again"
                    elif result == 0:
                        print "The node has gone away"
                        break
                    else:
                        print "An error occurred, code %s" % result
                        break
            else:
                print "An error occurred, code %s" % result

class KeyringLogoutModule(Module):
    '''Deletes stored credentials for the node(s)'''
    
    def run(self, nodes, args):
        pass

class KeyringModule(Module):
    '''Manages the keyring (credential store)'''
    
    submodules = {
        'status': KeyringStatusModule(),
        'login': KeyringLoginModule(),
        'logout': KeyringLogoutModule()
    }

module = KeyringModule()
