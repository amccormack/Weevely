
from base64 import b64encode

def join_abs_paths(paths,sep = '/'):
    return sep.join([p.strip(sep) for p in paths])


def b64_chunks(l, n):
    return [b64encode(l[i:i+n]) for i in range(0, len(l), n)]