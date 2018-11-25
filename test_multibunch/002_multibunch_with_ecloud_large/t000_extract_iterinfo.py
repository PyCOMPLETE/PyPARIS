

with open('pyparislog.txt', 'r') as fid:
    lines = fid.readlines()

iterlin = sorted([ll for ll in lines if ll.startswith('Iter')])

with open('iterlines.txt', 'w') as fid:
    fid.writelines(iterlin)

