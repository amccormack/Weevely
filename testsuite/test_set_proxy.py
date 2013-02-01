from baseclasses import ProxyTestCase
from tempfile import NamedTemporaryFile
from os import path, remove
from commands import getstatusoutput
from test import conf
import PythonProxy
import os, sys
sys.path.append(os.path.abspath('..'))
import core.http.request

rc_file = """
:set shell.php proxy=http://localhost:%i
:shell.php echo(\'WE\'.\'EV\'.\'ELY\');
"""


class SetProxy(ProxyTestCase):
        
    def test_proxy(self):
        
        ## Runtime test
        self.assertRegexpMatches(self._warn(':set shell.php proxy=http://localhost:%i' % self.__class__.proxyport), 'proxy=\'http://localhost:%i\'' % self.__class__.proxyport)
        self.assertEqual(PythonProxy.proxy_counts,0)
        self.assertEqual(self._outp(':shell.php echo(1+1);'), '2')
        self.assertGreater(PythonProxy.proxy_counts,0)
        
        ## Rc load at start test
        PythonProxy.proxy_counts=0
        rcfile = open(self.__class__.rcpath,'w')
        rcfile.write(rc_file % self.__class__.proxyport) 
        rcfile.close()
        
        command = '%s %s %s %s' % (conf['cmd'], conf['url'], conf['pwd'], 'echo')
        self.assertEqual(PythonProxy.proxy_counts,0)
        status, output = getstatusoutput(command)
        self.assertRegexpMatches(output, '\nWEEVELY')  
        self.assertGreater(PythonProxy.proxy_counts,0)
        
        # Verify that final socket is never contacted without proxy 
        PythonProxy.proxy_counts=0
        fake_url = 'http://localhost:%i/fakebd.php' % self.__class__.dummyserverport
        command = '%s %s %s %s' % (conf['cmd'], fake_url, conf['pwd'], 'echo')
        self.assertEqual(PythonProxy.proxy_counts,0)
        self.assertEqual(PythonProxy.dummy_counts,0)
        status, output = getstatusoutput(command)
        self.assertGreater(PythonProxy.proxy_counts,0)
        self.assertGreater(PythonProxy.dummy_counts,0)
        
        # Count that Client never connect to final dummy endpoint without passing through proxy
        self.assertGreaterEqual(PythonProxy.proxy_counts, PythonProxy.dummy_counts)
            
        
        self.assertRegexpMatches(self._warn(':set shell.php proxy=wrong://localhost:%i' % self.__class__.proxyport), 'proxy=\'wrong://localhost:%i\'' % self.__class__.proxyport)
        self.assertRegexpMatches(self._warn(':shell.php echo(1+1);'), core.http.request.WARN_UNCORRECT_PROXY)
        
        