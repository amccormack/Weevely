import os,sys
from module import ModuleException
from vector import VectorList, Vector
from helper import Helper


class ModHandler(Helper):

    interpreters_priorities = [ 'shell.sh', 'shell.php' ]


    def __init__(self, url = None, password = None):

        self.url = url
        self.password = password

        self.__set_path_modules()

        self.loaded_shells = []
        self.modules_classes = {}
        self.modules = {}

        Helper.__init__(self)

        self._first_load(self.path_modules)

        self.verbosity=[ 3 ]

        self.interpreter = None

    def __set_path_modules(self):

	try:
		current_path = os.path.realpath( __file__ )
		root_path = '/'.join(current_path.split('/')[:-2]) + '/'
		self.path_modules = root_path + 'modules'
	except Exception, e :
		raise Exception('Error finding module path: %s' % str(e))

        if not os.path.exists(self.path_modules):
		raise Exception( "No module directory %s found." % self.path_modules )



    def _first_load(self, startpath, recursive = True):

        for file_name in os.listdir(startpath):

            file_path = startpath + os.sep + file_name

            if os.path.isdir(file_path) and recursive:
                self._first_load(file_path, False)
            if os.path.isfile(file_path) and file_path.endswith('.py') and file_name != '__init__.py':
		module_name = '.'.join(file_path[:-3].split('/')[-2:])
                mod = __import__('modules.' + module_name, fromlist = ["*"])
                modclass = getattr(mod, mod.classname)
                self.modules_classes[module_name] = modclass

                module_g, module_n = module_name.split('.')
                if module_g not in self.modules_names_by_group:
                    self.modules_names_by_group[module_g] = []
                self.modules_names_by_group[module_g].append(module_name)

        self.ordered_groups = self.modules_names_by_group.keys()
        self.ordered_groups.sort()

    def load(self, module_name, disable_interpreter_probe=False):

        if not module_name in self.modules:
            if module_name not in self.modules_classes.keys():
                raise ModuleException(module_name, "Not found in path '%s'." % (self.path_modules) )

            self.modules[module_name]=self.modules_classes[module_name](self, self.url, self.password)

            if module_name.startswith('shell.'):
                self.loaded_shells.append(module_name)

        return self.modules[module_name]


    def set_verbosity(self, v = None):

        if not v:
            if self.verbosity:
                self.verbosity.pop()
            else:
                self.verbosity = [ 3 ]
        else:
            self.verbosity.append(v)


    def load_interpreters(self):

        for interpr in self.interpreters_priorities:

            try:
                self.load(interpr)
            except ModuleException, e:
                print '[!] [%s] %s' % (e.module, e.error)
            else:
                self.interpreter = interpr
                return self.interpreter


        raise ModuleException('[!]', 'No remote backdoor found. Check URL and password.')
#

