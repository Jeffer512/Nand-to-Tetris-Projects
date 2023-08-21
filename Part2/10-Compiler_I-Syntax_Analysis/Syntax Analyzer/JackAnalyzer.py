import os
import sys
from compilationengine import CompilationEngine

# Check if a command line argument was provided
try:
    path = sys.argv[1]

# If not raise an error
except IndexError:
    print("Error: Please provide a path or file name.")
    sys.exit(1)

files_list = ""

# If the argument is a .jack file, set 'files_list' to the provided file
# set 'path' to the rest of the argument provided (could be empty).
if path.split('.')[-1] == 'jack':
    files_list = [path.split('/')[-1]]
    path = '/'.join(path.split('/')[:-1])

if path.split('.')[-1] == 'jack':
    files_list = [path.split('/')[-1]]
    path = '/'.join(path.split('/')[:-1])

if path:
    if path.endswith('/'):
        path = path[:-1]
    # If an invalid path was provided raise an error
    if not (path.startswith('..') or path.startswith('/') or path in os.listdir()):
        print("Error: Invalid path")
        sys.exit(1)
    # Go up as many directories as leading '..' in the command line argument provided
    if path.startswith('..'):
        path = path.split('/')
        go_up = 0
        while path[0] == '..':
            go_up += 1
            path.pop(0)
        path = '/' + '/'.join(sys.path[0].split('/')[1:-go_up]) + '/' + '/'.join(path)
    elif path.startswith('/'):
        pass
    else:
        path = sys.path[0] + '/' + path
    if files_list:
        pass
    else:
        files_list = [i for i in os.listdir(path) if i.endswith('.jack')]

    if not path.endswith('/'):
        path = path + '/'

for file in files_list:
    with open(path + file) as f:
        file_data = f.readlines()

    # Create a new instance of the CompilationEngine class with the contents of the file
    compiled = CompilationEngine(file_data)
    # Start the compilation by calling the compile_class method on the CompilationEngine object
    compiled.compile_class(cnt=1)

    # Write the generated XML code to an output file with the same name as the input file but with a .xml extension
    with open((path + file).split(".")[0] + '.xml', 'w') as f:
        for j in compiled.xml_data:
            f.write(j + '\n')

