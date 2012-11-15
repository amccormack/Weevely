from core.moduleprobeall import ModuleProbeAll
from core.moduleexception import ProbeException, ProbeSucceed, ExecutionException
from core.vector import VectorList, Vector as V
from core.savedargparse import SavedArgumentParser as ArgumentParser

class User:

    def __init__(self,line):

        linesplit = line.split(':')

        self.line = line
        self.name = linesplit[0]
        self.home = '/home/' + self.name


        if len(linesplit) > 6:
             self.uid = int(linesplit[2])
             self.home = linesplit[5]
             self.shell = linesplit[6]

class Etcpasswd(ModuleProbeAll):
    """Enumerate users and /etc/passwd content"""


    vectors = VectorList([
        V('shell.php', 'posix_getpwuid', "for($n=0; $n<2000;$n++) { $uid = @posix_getpwuid($n); if ($uid) echo join(':',$uid).\'\n\';  }"),
        V('shell.sh', 'cat', "cat /etc/passwd"),
        V('file.read', 'read', "/etc/passwd")
        ])

    argparser = ArgumentParser(usage=__doc__)
    argparser.add_argument('-real', help='Show only real users', action='store_true')
    argparser.add_argument('-vector', choices = vectors.get_names())


    def __verify_execution(self):


        pwdfile = ''

        if self._result:
            response_splitted = self._result.split('\n')
            if response_splitted and response_splitted[0].count(':') >= 6:
                raise ProbeSucceed(self.name, 'Password file enumerated')
        else:
            raise ExecutionException(self.name, 'Enumeration execution failed')
            

    def _output_result(self):
        
        filter_real_users = self.args['real']
        response_splitted = self._result.split('\n')
        response_dict = {}
        output_str = ''
        
        for line in response_splitted:
            if line:

                user = User(line)

                if filter_real_users:
                    if (user.uid == 0) or (user.uid > 999) or (('false' not in user.shell) and ('/home/' in user.home)):
                        output_str += line + '\n'
                        response_dict[user.name]=user
                else:
                        output_str += line + '\n'
                        response_dict[user.name]=user

        self._output = output_str[:-1] # Stringified /etc/passwd without last \n
        self._result = response_dict # Objectified /etc/passwd



