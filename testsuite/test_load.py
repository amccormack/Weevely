from baseclasses import RcTestCase
from tempfile import NamedTemporaryFile
from os import path, remove
from commands import getstatusoutput
from baseclasses import conf

rc_file = """
:shell.php print(\'W\');
:set shell.php debug=1
echo EE
# echo X
# shell.php print(\'X\');
:set shell.php debug=
echo VELY
"""

class Load(RcTestCase):

    def test_load(self):
        
        temp_file = NamedTemporaryFile(); 
        temp_file.write(rc_file)
        temp_file.flush()

        self.assertEqual(self._outp(':load %s' % temp_file.name), 'WEEVELY')
        self.assertRegexpMatches(self._warn(':load %sa' % temp_file.name), 'Error opening')
        
        temp_file.close()
        
    def test_rc(self):
        
        rcfile = open(self.__class__.rcpath,'w')
        rcfile.write(rc_file) 
        rcfile.close()
        
        call = "'echo'"
        command = '%s %s %s %s' % (conf['cmd'], conf['url'], conf['pwd'], call)
        status, output = getstatusoutput(command)
        
        self.assertRegexpMatches(output, '\nW[\s\S]+\nEE[\s\S]+\nVELY')  
        