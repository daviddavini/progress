import re
import sys

with open(sys.argv[1]) as f:
    lines = f.readlines()

for line in lines:
    m = re.search('".*"', line)
    print('    '*(m.start()-1), m.group()[1:-1], sep='')
