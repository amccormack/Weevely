from baseclasses import SimpleTestCase
from tempfile import NamedTemporaryFile
import os


class FSEnum(SimpleTestCase):
    
    def test_help(self):
        help_output = self._warn(":help" )
        self.assertRegexpMatches(help_output, '|[\s]module[\s]+|[\s]description[\s]+|[\n]{%i}' % (len(self.term.modhandler.modules_classes)+2))       
        self.assertNotRegexpMatches(help_output, '\n'*4)       
        
        help_shell_output = self._warn(":help shell" )
        self.assertRegexpMatches(help_shell_output, '\[shell\.sh\] System shell[\s\S]+usage:[\s\S]+\[shell\.php\] PHP shell[\s\S]+usage:[\s\S]+')
        self.assertNotRegexpMatches(help_shell_output, '\n'*4)       
        
        help_nonexistant_output = self._warn(":help nonexistant" )
        self.assertRegexpMatches(help_nonexistant_output, '')
        
        help_shell_sh_output = self._warn(":help shell.sh" )
        self.assertRegexpMatches(help_shell_sh_output, 'usage:[\s\S]+System shell[\s\S]+positional arguments:[\s\S]+optional arguments:[\s\S]+stored arguments:[\s\S]+')
        self.assertNotRegexpMatches(help_shell_sh_output, '\n'*3)       
        