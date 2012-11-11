
import types
from commands import getstatusoutput as run
from re import search, DOTALL
import pexpect
import testgroups

class TestException(Exception):
    pass


class TGproc(list):
    
    def __init__(self, conf, TCs):
        
        self.conf = conf
        list.__init__(self)
        self.extend(TCs)

        
    def test(self):
        
        for tc in self:
            tc.test()


    def outp_format(self, out):
        
        return ' \n===============================\n%s\n===============================\n' % out


class TCproc:
    def __init__(self, params, expected_output, expected_status = None, negate=False, printout=False, background=False):
        
        if isinstance(expected_output, types.ListType):
            self.expected_output = expected_output
        elif isinstance (expected_output, types.StringTypes):
            self.expected_output = [ expected_output ]
        else:
            print "[!] Error declaring TC expected output"

        self.params = params
        
        self.status = expected_status
        self.negate = negate
        self.printout = printout
        self.background = background

    def outp_format(self, out):
        
        return ' \n===============================\n%s\n===============================\n' % out



    def test(self):
            
        result = 'KO'
            
        if self.background:
            cmd_string = './weevely.py %s &' % (' '.join(self.params))
            if not self.printout:
                cmd_string = '(%s) > /dev/null' % cmd_string
            run_bg(cmd_string)
            result = 'BG'
        else:
            cmd_string = './weevely.py %s' % (' '.join(self.params))
            status, output = run(cmd_string)
            for expected in self.expected_output:
                if self.negate != bool(search('.*%s.*' % expected, output, flags=DOTALL)):
                    # Only one test passed in enough
                    
                    if self.negate:
                        result = "OK NOT [ '%s' ]" % "', '".join(self.expected_output)
                    else:
                        result = "OK [ '%s' ]" % (expected)
                    
                    break

        print '    [+] %s .. %s' % (cmd_string, result) 

        if result == 'KO':
            raise TestException('Test failed. Expected output: \'%s\'\n %s' % ("', '".join(self.expected_output), self.outp_format(output)))
        
        if self.printout:
            print self.outp_format(output)
            
            

class TG(TGproc):
    
    def __init__(self, conf, TCs):
        
        self.proc = pexpect.spawn('%s %s' % (conf['cmd'], conf['urlpwd']), timeout=int(conf['timeout']))
        
        TGproc.__init__(self, conf, TCs)

    def test(self):
        
        # Wait for prompt
        result_index = self.proc.expect([ '.*\$ ', '.*> ', pexpect.TIMEOUT ])
        output = str(self.proc.before) + str(self.proc.after)
        if result_index > 2:
            raise TestException('Test failed. Expected prompt\n %s' % (self.outp_format(output)))
        
        
        for tc in self:
            tc.test(self.proc)


class TC(TCproc):
    def __init__(self, params, expected_output, expected_status = None, negate=False, printout=False, background=False):
        TCproc.__init__(self, params, expected_output, expected_status, negate, printout, background)
    
    def test(self, proc):
            
        result = 'KO'
        
        command = ' '.join(self.params) + '\r\n'
        proc.send(command)
        
        if self.expected_output[0] == testgroups.JUST_PROMPT:
            self.expected_output = [ command[-10:] + out for out in self.expected_output ]
        
        expected_list = self.expected_output + [ pexpect.TIMEOUT ]
        
        result_index = proc.expect(expected_list)
        output = str(proc.before) + str(proc.after)
        
        #print  expected_list, result_index, '|' + output + '|'
        
        if self.negate != (result_index < len(expected_list) - 1):
            result = "OK [ '%s' ]" % (expected_list[result_index] if expected_list[result_index] == pexpect.TIMEOUT else ''.join(expected_list[result_index].splitlines()))
        
        print '[+] %s .. %s' % (' '.join(self.params), result) 
            
        if result == 'KO':
            raise TestException('Test failed. Expected output: \'%s\'\n %s' % ("', '".join(self.expected_output), self.outp_format(output)))
        
        
        
        if self.printout:
            print self.outp_format(output)
            

