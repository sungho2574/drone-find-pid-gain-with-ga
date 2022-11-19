def change_face (line):
    line = line.split()

    new_line = 'f'
    for i in range(1, len(line)):
        part = line[i].split('/')
        new_line += ' ' + part[0] + '//' + part[2]
    
    return new_line


# print(change_face('f 1/1/1 2/2/2 3/3/3 4/4/4'))

with open('Final.obj', 'r') as f:
    data = f.read()
    data = data.split('\n')

    # check where is vt
    idx = []
    for i, line in enumerate(data):
        if line.startswith('vt'):
            idx.append(i)

    # change f
    for i, line in enumerate(data):
        if line.startswith('f'):
            data[i] = change_face(line)
    
    data = data[ : idx[0]] + data[idx[-1]+1 : ]
    data = '\n'.join(data)


with open('test.obj', 'w') as f:
    f.write(data)
    