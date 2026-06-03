import sys

tag     = sys.argv[1]
service = sys.argv[2]

with open('helm/hotel/values.yaml', 'r') as f:
    lines = f.readlines()

in_service = False
updated    = False

for i, line in enumerate(lines):
    if service in line:
        in_service = True
    if in_service and line.strip().startswith('tag:'):
        lines[i]   = '    tag: "' + tag + '"\n'
        in_service = False
        updated    = True
        break

with open('helm/hotel/values.yaml', 'w') as f:
    f.writelines(lines)

if updated:
    print('Tag mis a jour pour ' + service + ' : ' + tag)
else:
    print('ERREUR: service ' + service + ' non trouve dans values.yaml')
    sys.exit(1)