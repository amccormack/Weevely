import argparse
ns = argparse.StoredNamespace()
a = argparse.ArgumentParser()
a.add_argument('-asd')
a.add_argument('gna')
print 'A'
print a.parse_args([ '-asd', 'ASD' ], ns)
print 'B'
print a.parse_args('-asd')
print 'C'
