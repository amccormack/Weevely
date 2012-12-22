from baseclasses import SimpleTestCase
import sys, os
sys.path.append(os.path.abspath('..'))


class Set(SimpleTestCase):


    def test_set(self):
        
        sh_params = [ x.dest for x in self.term.modhandler.load('shell.sh').argparser._actions ]
        
        # First, execute a shell.sh command to initialize shell
        self._res('echo')
        
        sh_params_print = self._warn(':set shell.sh')
        # Basic parameter output
        self.assertRegexpMatches(sh_params_print, '%s=\'.*\' ' % '=\'.*\' '.join(sh_params) )
        
        # Shell.sh should have an already set vector
        self.assertRegexpMatches(sh_params_print, 'vector=\'[\w]+\'')
        
        #Set parameter previously to execute command without 
        self.assertRegexpMatches(self._warn(':set shell.sh cmd="echo ASD"'), 'cmd=\'echo ASD\'' )
        self.assertRegexpMatches(self._warn(':set shell.sh'), 'cmd=\'echo ASD\'' )
        self.assertEqual(self._res(':shell.sh'), 'ASD' )
        
        #Set wrongly parameter with choices
        self.assertRegexpMatches(self._warn(':set shell.sh vector="nonexistant"'), 'vector=\'nonexistant\'' )
        self.assertRegexpMatches(self._warn(':shell.sh "echo ASD"'), 'invalid choice' )        
             
        # Reset parameters
        self.assertRegexpMatches(self._warn(':set shell.sh vector=""'), 'vector=\'\'' )
        self.assertRegexpMatches(self._warn(':set shell.sh cmd='), 'cmd=\'\'' )
        self.assertEqual(self._res('echo ASD'), 'ASD' )      

        #Set wrongly parameter with choices but run it correctly
        self.assertRegexpMatches(self._warn(':set shell.php debug="asd"'), 'debug=\'asd\'' )
        self.assertEqual(self._res(':shell.php print(\'ASD\'); -debug 4'), 'ASD' )   
        self.assertRegexpMatches(self._warn(':set shell.php debug='), 'debug=\'\'' )

        #Set wrongly parameter type
        self.assertRegexpMatches(self._warn(':set shell.php debug=\'asd\''), 'debug=\'asd\'' )
        self.assertRegexpMatches(self._warn('echo'), 'invalid int value' )    

