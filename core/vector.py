from core.moduleexception import ModuleException
from string import Template
from types import ListType, StringTypes, DictType


class VectorList(list):
    def get_by_interpreters(self, shells):
        vect=[]
        for v in self:
            if v.interpreter in shells:
                vect.append(v)

        return vect

    def get(self, name):
        for v in self:
            if v.name == name:
                return v

    def get_names(self):

        return [v.name for v in self]

    def print_order(self, names):
        sorted = [v for v in self for n in names if n == v.name]
        print sorted

    def __repr__(self):
        repr = ''
        for v in self:
            repr += str(v)
        return repr


class Vector:
    
    
    def __init__(self, interpreter, name, payloads):
        self.interpreter = interpreter
        self.name = name
        
        # Payloads and Formats are list of lists
        self.payloads = []
        
        if isinstance(payloads, ListType):
            self.payloads = payloads
        elif isinstance (payloads, StringTypes):
            self.payloads.append(payloads)
        else:
            print "[!] Error declaring attack vector"


    def execute(self, modhandler, format_list = []):

        # Normalize type into list of dicts
        
        if isinstance(format_list, DictType):
            format_list = [ format_list ]
        elif isinstance (format_list, ListType):
            pass
        else:
            print "[!] Error with format vector type"
            return

        # Check lenght
        
        if format_list and len(format_list) != len(self.payloads):
            print "[!] Error with format length %i and vector length %i" % (len(format_list), len(self.payloads))
            return

        
        i = 0
        formatted_list = []
        for payload in self.payloads:
            
            if i >= len(format_list):
                formatted_list.append(payload)
            else:
                
                try:
                    formatted_list.append(Template(payload).safe_substitute(**format_list[i]))
                except KeyError, e:
                    raise   
            i+=1
        
        
        return modhandler.load(self.interpreter).run(formatted_list)

            

    def __repr__(self):
        return '[%s, %s, %s]' % (self.name,self.interpreter,  self.payloads)

