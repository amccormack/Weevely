from baseclasses import SimpleTestCase, FolderFSTestCase, conf
from tempfile import NamedTemporaryFile
import os


class FSUserFiles(SimpleTestCase):
    
    @classmethod
    def _setenv(cls):    
        FolderFSTestCase._setenv.im_func(cls)
        cls._env_chmod(conf['currentuser_home_path'], '755', currentuser=True)
        cls._env_chmod(conf['currentuser_path_1'], '644', currentuser=True)
        cls._env_chmod(conf['currentuser_path_2'], '644', currentuser=True)
        
    @classmethod
    def _unsetenv(cls):
        FolderFSTestCase._unsetenv.im_func(cls)
        cls._env_chmod(conf['currentuser_home_path'], conf['currentuser_home_mode'], currentuser=True)
        cls._env_chmod(conf['currentuser_path_1'], conf['currentuser_default_mode_1'], currentuser=True)
        cls._env_chmod(conf['currentuser_path_2'], conf['currentuser_default_mode_2'], currentuser=True)
        
    
    
    def test_userfiles(self):
        
        expected_enum_map = {
            os.path.join(conf['currentuser_home_path'],conf['currentuser_path_1']): ['exists', 'readable', '', ''],
            os.path.join(conf['currentuser_home_path'],conf['currentuser_path_2']): ['exists', 'readable', '', '']
            }
        
        path_list = [conf['currentuser_path_1'], conf['currentuser_path_2'] ]
        
        temp_path = NamedTemporaryFile(); 
        temp_path.write('\n'.join(path_list)+'\n')
        temp_path.flush() 
        
        self.assertDictContainsSubset(expected_enum_map, self._res(":audit.userfiles"))
        self.assertEqual(self._res(":audit.userfiles -pathlist \"%s\"" % str(path_list)), expected_enum_map)
        self.assertDictContainsSubset(expected_enum_map, self._res(":audit.userfiles -auto-user"))
        self.assertDictContainsSubset(expected_enum_map, self._res(":audit.userfiles -pathfile %s" % temp_path.name))

        temp_path.close()
      