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
from tempfile import NamedTemporaryFile
import pexpect

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


    def _run_test_quietly(self, command):
        stdout = sys.stdout
        #print '[>] %s' % command
        sys.stdout = open(os.devnull, 'w')  
        self.term.run_cmd_line(shlex.split(command))
        sys.stdout = stdout
        

    def _outp(self, command):
        
        self._run_test_quietly(command)
        return self.term._last_output

    def _warn(self, command):
        self._run_test_quietly(command)
        return self.term._last_warns
    

    def _run_cmd(self, cmd):
        #print '\n[env] %s' % cmd,
        child = pexpect.spawn(cmd)
        idx = child.expect([pexpect.TIMEOUT, pexpect.EOF])
        if idx == 0: child.interact()
        

    def _env_mkdir(self, relpath):
        abspath = os.path.join(conf['env_base_writable_web_dir'], relpath)
        cmd = Template(conf['env_mkdir_command']).safe_substitute(path=abspath)
        self._run_cmd(cmd)

        
    def _env_newfile(self, relpath, content = '1'):
    
        file = NamedTemporaryFile()
        file.close()
        frompath = file.name
        
        f = open(frompath, 'w')
        f.write('1')
        f.close()
        
        abspath = os.path.join(conf['env_base_writable_web_dir'], relpath)
        cmd = Template(conf['env_cp_command']).safe_substitute(frompath=frompath, topath=abspath)
        self._run_cmd(cmd)

    def _env_chmod(self, relpath, mode='644'):
        abspath = os.path.join(conf['env_base_writable_web_dir'], relpath)
        cmd = Template(conf['env_chmod_command']).safe_substitute(path=abspath, mode=mode)
        self._run_cmd(cmd)

    def _env_rm(self, relpath):
        abspath = os.path.join(conf['env_base_writable_web_dir'], relpath)
        
        if conf['env_base_writable_web_dir'].count('/') < 3:
            print 'Please check %s, not removing' % conf['env_base_writable_web_dir']
            return
        
        cmd = Template(conf['env_rm_command']).safe_substitute(path=abspath)
        self._run_cmd(cmd)

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
        
        self.basedir = conf['env_base_writable_web_dir']
        self.newdirs = ['w1', 'w2', 'w3', 'w4']
        self._env_rm(self.newdirs[0])   
        self._env_mkdir(os.path.join(*self.newdirs))

    def _unsetenv(self):
        self._env_rm(self.newdirs[0])        
        
    def test_ls(self):
        
        self.assertEqual(self._outp('ls %s' % self.basedir), self.newdirs[0])
        self.assertEqual(self._outp('ls %s' % os.path.join(self.basedir,self.newdirs[0])), self.newdirs[1])
        self.assertEqual(self._outp('ls %s' % os.path.join(self.basedir,*self.newdirs[:2])), self.newdirs[2])
        self.assertEqual(self._outp('ls %s' % os.path.join(self.basedir,*self.newdirs[:3])), self.newdirs[3])
        self.assertEqual(self._outp('ls %s' % os.path.join(self.basedir,*self.newdirs[:4])), '')
        self.assertEqual(self._outp('ls %s/.././/../..//////////////./../../%s/' % (self.basedir, self.basedir)), self.newdirs[0])


    def _path(self, command):
        self._run_test_quietly(command)
        return self.term.modhandler.load('shell.php').stored_args['path']

    def test_cwd(self):
        
        self.assertEqual(self._path('cd %s' % self.basedir), self.basedir)
        self.assertEqual(self._path('cd %s' % os.path.join(self.basedir,*self.newdirs[:4])), os.path.join(self.basedir,*self.newdirs[:4]))
        self.assertEqual(self._path('cd .'), os.path.join(self.basedir,*self.newdirs[:4]))
        self.assertEqual(self._path('cd ..'), os.path.join(self.basedir,*self.newdirs[:3]))
        self.assertEqual(self._path('cd ..'), os.path.join(self.basedir,*self.newdirs[:2]))
        self.assertEqual(self._path('cd ..'), os.path.join(self.basedir,*self.newdirs[:1]))
        self.assertEqual(self._path('cd ..'), self.basedir)
        self.assertEqual(self._path('cd %s' % os.path.join(self.basedir,*self.newdirs)), os.path.join(self.basedir,*self.newdirs))
        self.assertEqual(self._path('cd .././/../..//////////////./../%s/../' % self.newdirs[0]), self.basedir)


class FSInteract(SimpleTestCase):

    def _setenv(self):
        
        self.basedir = conf['env_base_writable_web_dir']
        self.newdirs = ['w1', 'w2', 'w3', 'w4']
        self.filenames = []
        self._env_mkdir(os.path.join(*self.newdirs))
        
        i=1
        for i in range(len(self.newdirs)):
            pathlist = self.newdirs[:i] + [ 'file-%s.txt' % self.newdirs[i] ]
            filename = os.path.join(*pathlist)
            self._env_newfile(filename)
            self.filenames.append(filename)
            i+=1

        
    def _unsetenv(self):
        self._env_rm(self.newdirs[0])   
        for path in self.filenames:
            self._env_rm(path)   
            
        
    
    def test_check(self):
        
        self.assertEqual(self._outp(':file.check unexistant exists'), 'False')
        self.assertEqual(self._outp(':file.check %s read' % self.basedir), 'True')
        self.assertEqual(self._outp(':file.check %s exec' % self.basedir), 'True')
        self.assertEqual(self._outp(':file.check %s isfile' % self.basedir), 'False')
        self.assertEqual(self._outp(':file.check %s exists' % self.basedir), 'True')
        self.assertEqual(self._outp(':file.check %s isfile' % os.path.join(self.basedir,self.filenames[0])), 'True')
        self.assertEqual(self._outp(':file.check %s md5' % os.path.join(self.basedir,self.filenames[0])), 'c4ca4238a0b923820dcc509a6f75849b')


    def test_rm(self):
        pass
        
        
#                        'rm' : TG(conf,
#                [
#                TC([ ':file.rm unexistant' ], ERR_NO_SUCH_FILE),
#                # Delete a single file
#                TC([ ':file.rm %s/newfile' % (conf['existant_base_dir']) ], PROMPT_PHP_SH),
#                TC([ ':file.check %s/newfile exists' % (conf['existant_base_dir']) ], 'False'),
#                
#                # Delete a single file recursively
#                TC([ ':file.rm %s/newfile1 -recursive' % (conf['existant_base_dir']) ], PROMPT_PHP_SH),
#                TC([ ':file.check %s/newfile1 exists' % (conf['existant_base_dir']) ], 'False'),               
#                
#                # Try to delete dir tree without recursion
#                TC([ ':file.rm %s/%s ' % (conf['existant_base_dir'], conf['existant_base_4_lvl_subdirs'].split('/')[0]) ], PROMPT_PHP_SH),
#                TC([ ':file.check %s/%s exists' % (conf['existant_base_dir'], conf['existant_base_4_lvl_subdirs'].split('/')[0]) ], 'True'), 
#                
#                # Delete dir tree with recursion
#                TC([ ':file.rm %s/%s -recursive' % (conf['existant_base_dir'], conf['existant_base_4_lvl_subdirs'].split('/')[0]) ], PROMPT_PHP_SH),
#                TC([ ':file.check %s/%s exists' % (conf['existant_base_dir'], conf['existant_base_4_lvl_subdirs'].split('/')[0]) ], 'False'), 
#                    
#                # VECTORS
#                TC([ ':set shell.php debug=1' ], PROMPT_PHP_SH),  
#                
#                # Delete with php_rmdir vector
#                TC([ ':file.rm %s/newfile2 -vector php_rmdir' % (conf['existant_base_dir']) ], "function rrmdir"),
#                TC([ ':file.check %s/newfile2 exists' % (conf['existant_base_dir']) ], 'False'),
#                
#                # Delete with rm vector
#                TC([ ':file.rm %s/newfile3 -vector rm -recursive' % (conf['existant_base_dir']) ], 'rm -rf %s' % (conf['existant_base_dir'])),
#                TC([ ':file.check %s/newfile3 exists' % (conf['existant_base_dir']) ], 'False'),
#                               
#                ]),


if __name__ == '__main__':
    unittest.main(verbosity=2)
#    suite = unittest.TestLoader().loadTestsFromTestCase(FSInteract)
#    unittest.TextTestRunner(verbosity=2).run(suite)



#            'cwd_safemode' : TG(conf,
#                [
#                TC([ 'cd unexistant' ], ERR_NO_SUCH_FILE),       
#                TC([ 'cd ..' ], ERR_NO_SUCH_FILE),       
#                ]),
#  
#            'ls_safemode' : TG(conf,
#                [
#                TC([ 'ls unexistant' ], ERR_NO_SUCH_FILE),       
#                TC([ 'ls /' ], ERR_NO_SUCH_FILE),    
#                TC([ 'ls /tmp/' ], ERR_NO_SUCH_FILE),    
#
#                ]),
