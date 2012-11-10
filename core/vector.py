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
        
        # Payloads and Formats are lists
        self.payloads = []
        
        if payloads and isinstance(payloads, ListType):
            self.payloads = payloads
        elif payloads and isinstance (payloads, StringTypes):
            self.payloads.append(payloads)
        
    def execute(self, modhandler, format_list = {}, stringify = False):

        # Check type dict
        if not isinstance(format_list, DictType):
            print "[!] Error, format vector type is not dict"
            return


        formatted_list = []
        format_template_list = format_list.keys()
        for payload in self.payloads:
            
            # Search format keys present in current payload part 
            list_of_key_formats_in_payload = [s for s in format_template_list if '$%s' % s in payload]
            
            # Extract from format dict just the ones for current payload part
            dict_of_formats_in_payload = {k:v for k,v in format_list.iteritems() if k in list_of_key_formats_in_payload}
            
            if dict_of_formats_in_payload:
                formatted_list.append(Template(payload).safe_substitute(**dict_of_formats_in_payload))
            else:
                formatted_list.append(payload)

        return modhandler.load(self.interpreter).run(formatted_list, stringify)

            

    def __repr__(self):
        return '[%s, %s, %s]' % (self.name,self.interpreter,  self.payloads)

