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
from commands import getstatusoutput


confpath = 'conf.ini'

configparser = ConfigParser()
configparser.read(confpath)
conf = configparser._sections['global']

class SimpleTestCase(unittest.TestCase):
    
    def setUp(self):
        self._setenv()        
        self.term = core.terminal.Terminal (ModHandler(conf['url'], conf['pwd']))


    def tearDown(self):
        self._unsetenv()

    def _setenv(self):
        pass
    
    def _unsetenv(self):
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
    

    def _env_mkdir(self, relpath):
        
        abspath = os.path.join(conf['env_base_writable_web_dir'], relpath)
        cmd = Template(conf['env_mkdir_command']).safe_substitute(path=abspath)
        status, output = getstatusoutput(cmd)
        print '[env_mkdir] %s' % cmd
        if status != 0:
            print output
        
    def _env_newfile(self, relpath, content = '1'):
        abspath = os.path.join(conf['env_base_writable_web_dir'], relpath)
        
        cmd = Template(conf['env_mk_new_file_with_content']).safe_substitute(path=abspath, content=content)
        status, output = getstatusoutput(cmd)
        print '[env_newfile] %s' % cmd
        if status != 0:
            print output

    def _env_chmod(self, relpath, mode='644'):
        abspath = os.path.join(conf['env_base_writable_web_dir'], relpath)
        
        cmd = Template(conf['env_chmod_command']).safe_substitute(path=abspath, mode=mode)
        print '[env_chmod] %s' % cmd
        if status != 0:
            print output

    def _env_rm(self, relpath):
        abspath = os.path.join(conf['env_base_writable_web_dir'], relpath)
        
        if conf['env_base_writable_web_dir'].count('/') != 3:
            print 'Please check %s, not removing' % conf['env_base_writable_web_dir']
            return
        
        cmd = Template(conf['env_rm_command']).safe_substitute(path=abspath)
        status, output = getstatusoutput(cmd)
        print '\n[env_rm] %s' % cmd
        if status != 0:
            print output

class Shells(SimpleTestCase):


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
        

class ShellsFSBrowse(SimpleTestCase):

    def _setenv(self):
        
        self.basedir = 'env_base_writable_web_dir'
        self.newdirs = ['w1', 'w2', 'w3', 'w4']
        self._env_mkdir(os.path.join(*self.newdirs))

    def _unsetenv(self):
        self._env_rm(self.newdirs[0])        
        
    def test_ls(self):
        
        self.assertEqual(self._outp(':shell.sh echo $((1+1))'), '2')


if __name__ == '__main__':
    unittest.main(verbosity=2)

