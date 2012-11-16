#!/usr/bin/env python
import sys, os
sys.path.append(os.path.abspath('..'))
import core.terminal
from core.modulehandler import ModHandler
from core.moduleexception import ModuleException
from ConfigParser import ConfigParser
import unittest, shlex
import modules.shell.php
from string import Template
import pexpect


confpath = 'conf.ini'

class SimpleTestCase(unittest.TestCase):
    
    def setUp(self):
        
        config = ConfigParser()
        config.read(confpath)
        self.conf = config._sections['global']

        self._setenv()        
        self.term = core.terminal.Terminal (ModHandler(self.conf['url'], self.conf['pwd']))

    def _setenv(self):
        pass

    def __run_quietly(self, command):
        stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')  
        self.term.run_cmd_line(shlex.split(command))
        sys.stdout = stdout
        

    def _outp(self, command):
        
        self.__run_quietly(command)
        return self.term._last_output

    def _warn(self, command):
        self.__run_quietly(command)
        return self.term._last_warns

class ShellsTestCase(SimpleTestCase):

#    def _setenv(self):
#        cmd = Template(self.conf['shell_copy_file']).safe_substitute(frompath=frompath, topath=topath)
#        child = pexpect.spawn(cmd)
#        child.interact()

    def test_php(self):
        
        self.assertEqual(self._outp(':shell.php echo(1+1);'), '2')
        self.assertRegexpMatches(self._warn(':shell.php echo(1+1)'), '%s' % modules.shell.php.WARN_TRAILING_SEMICOLON )
        self.assertRegexpMatches(self._warn(':shell.php echo(1+1); -debug 1'), 'Request[\S\s]*Response' )
        self.assertEqual(self._outp(':shell.php print($_COOKIE);'), 'Array')   
        self.assertRegexpMatches(self._warn(':shell.php print($_COOKIE); -mode Referer'), modules.shell.php.WARN_NO_RESPONSE),
        # Check if wrongly do __slacky_probe at every req    
        self.assertRegexpMatches(self._warn(':shell.php echo(1); -debug 1'), 'Request[\S\s]*Response'),   
        self.assertEqual(self._outp(':shell.php echo(2); -precmd print(1);'), '12')  
        self.assertEqual(self._outp(':shell.php -post "{ \'FIELD\':\'VALUE\' }" echo($_POST[\'FIELD\']);'), 'VALUE') 

    def test_sh(self):
        self.assertEqual(self._outp(':shell.sh echo $((1+1))'), '2')
        self.assertEqual(self._outp('echo $((1+1))'), '2')
        self.assertEqual(self._outp(':shell.sh echo "$((1+1))" -vector shell_exec'), '2')
        self.assertEqual(self._outp(':shell.sh echo "$((1+1))" -vector system'), '2')
        self.assertEqual(self._outp(':shell.sh echo "$((1+1))" -vector exec'), '2')
        self.assertEqual(self._outp(':shell.sh echo "$((1+1))" -vector popen'), '2')
        #self.assertEqual(self._outp(':shell.sh echo "$((1+1))" -vector python_eval'), '2')
        #self.assertEqual(self._outp(':shell.sh echo "$((1+1))" -vector perl_system'), '2')
        self.assertEqual(self._outp(':shell.sh echo "$((1+1))" -vector proc_open'), '2')
        self.assertEqual(self._outp(':shell.sh \'(echo "VISIBLE" >&2)\' -stderr'), 'VISIBLE')
        self.assertEqual(self._outp(':shell.sh \'(echo "INVISIBLE" >&2)\''), '')
        
        

if __name__ == '__main__':
    unittest.main(verbosity=2)

