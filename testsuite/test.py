#!/usr/bin/env python

from os import system as run_bg, remove
from sys import argv
from testgroups import TestGroups, testsuites
from testclasses import TestException

class TestSuite:

    def __parse_testlist_parameters(self):

        tslist = []
        if len(argv) >= 3:
            
                    
            try:
                self.testgroups = TestGroups(argv[1])
            except Exception, e:
                print 'Error opening ini config file %s: %s' % (argv[1], str(e))
                raise
            
            
            for par in argv[2:]:
                tslist.append(par)
        else:
            print '[TEST] test.py <conf.ini> <%s | all>' % (' |'.join(testsuites.keys()))
        
        return tslist
           
           
    def __run_tests(self,tslist):
        try:
            for userts in tslist:
                  for ts, tgs in testsuites.items():
                      if userts == ts or userts == 'all':
                          print '[%s]' % ts
                          for tg in tgs:
                              print '  [%s]' % tg
                              self.testgroups.TGs[tg].test()

        except TestException, e:
            print '[!] %s' % str(e)

    def __init__(self):
        
        tslist = self.__parse_testlist_parameters()
        if tslist:
            self.__run_tests(tslist)

    
if __name__ == "__main__":
    TestSuite()
