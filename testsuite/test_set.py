from baseclasses import SimpleTestCase
from core.utils import randstr
import sys, os
sys.path.append(os.path.abspath('..'))


class Set(SimpleTestCase):


    def test_set(self):
        
        module_params = [ x.dest for x in self.term.modhandler.load('file.upload').argparser._actions ]
        
        filename_rand = randstr(4)
        filepath_rand = os.path.join(self.basedir, filename_rand)

        self._res(':set shell.php debug=1')

        self.assertTrue(self._res(':file.upload /etc/hosts %s -content MYTEXT' % filepath_rand))
        
        params_print = self._warn(':set file.upload')
        # Basic parameter output
        self.assertRegexpMatches(params_print, '%s=\'.*\'[\s]+' % '=\'.*\'[\s]+'.join(module_params) )
        
        # Module should have an already set vector
        self.assertRegexpMatches(params_print, 'vector=\'[\w]+\'')
        
        #Set parameter previously to execute command without 
        self.assertRegexpMatches(self._warn(':set file.upload lpath="/etc/hosts"'), 'lpath=\'/etc/hosts\'' )
        self.assertRegexpMatches(self._warn(':set file.upload rpath="%s1"' % filepath_rand), 'rpath=\'%s1\'' % filepath_rand )
        self.assertRegexpMatches(self._warn(':set file.upload'),'lpath=\'/etc/hosts\'[\s]+rpath=\'%s1\'' % filepath_rand )
        self.assertTrue(self._res(':file.upload'))
        
        #Set wrongly parameter with choices
        self.assertRegexpMatches(self._warn(':set file.upload vector="nonexistant"'), 'vector=\'nonexistant\'' )
        self.assertRegexpMatches(self._warn(':file.upload /etc/hosts %s2' % filepath_rand), 'invalid choice' )      
           
        # Reset parameters
        self.assertRegexpMatches(self._warn(':set file.upload vector=""'), 'vector=\'\'' )
        self.assertRegexpMatches(self._warn(':set file.upload lpath='), 'lpath=\'\'' )
        self.assertRegexpMatches(self._warn(':set file.upload rpath='), 'rpath=\'\'' )
        self.assertTrue(self._res(':file.upload /etc/hosts %s3 -mycontent ASD' % filepath_rand))     
        
        #Set wrongly parameter with choices but run it correctly
        self.assertRegexpMatches(self._warn(':set shell.php debug="asd"'), 'debug=\'asd\'' )
        self.assertEqual(self._res(':shell.php print(\'ASD\'); -debug 4'), 'ASD' )   
        self.assertRegexpMatches(self._warn(':set shell.php debug='), 'debug=\'\'' )

        #Set wrongly parameter type
        self.assertRegexpMatches(self._warn(':set shell.php debug=\'asd\''), 'debug=\'asd\'' )
        self.assertRegexpMatches(self._warn('echo'), 'invalid int value' )    

