import os
import sys

operations = {'add': '@SP\nAM=M-1\nD=M\nA=A-1\nM=D+M\n',
              'sub': '@SP\nAM=M-1\nD=M\nA=A-1\nM=M-D\n',
              'eq': '@SP\nAM=M-1\nD=M\nA=A-1\nD=D-M\n@LOOP[x]\nD;JEQ\n@SP\nA=M-1\nM=0\n@END_LOOP[x]\nD;JNE\n(LOOP[x])'
                    '\n@SP\nA=M-1\nM=-1\n(END_LOOP[x])\n',
              'gt': '@SP\nAM=M-1\nD=M\nA=A-1\nD=M-D\n@LOOP[x]\nD;JGT\n@SP\nA=M-1\nM=0\n@END_LOOP[x]\nD;JLE\n(LOOP[x])'
                    '\n@SP\nA=M-1\nM=-1\n(END_LOOP[x])\n',
              'lt': '@SP\nAM=M-1\nD=M\nA=A-1\nD=M-D\n@LOOP[x]\nD;JLT\n@SP\nA=M-1\nM=0\n@END_LOOP[x]\nD;JGE\n(LOOP[x])'
                    '\n@SP\nA=M-1\nM=-1\n(END_LOOP[x])\n',
              'neg': '@SP\nA=M-1\nM=-M\n',
              'and': '@SP\nAM=M-1\nD=M\nA=A-1\nM=D&M\n',
              'or': '@SP\nAM=M-1\nD=M\nA=A-1\nM=D|M\n',
              'not': '@SP\nA=M-1\nM=!M\n'}

memory_segments = {'local': 'LCL',
                   'argument': 'ARG',
                   'this': 'THIS',
                   'that': 'THAT',
                   'temp': 5}

assembly = {}
sys_asm = {}
vm_instructions = {}
f_counter = 0
all_files = []
files_list = ''
path = ''

# Check if a command line argument was provided, if not raise an error
try:
    path = sys.argv[1]

except IndexError:
    print("Error: Please provide a directory.")
    sys.exit(1)

if path.endswith('/'):
    path = path[:-1]

# If an invalid path was provided raise an error
if not (path.startswith('..') or path.startswith('/') or path in os.listdir()):
    print("Error: Invalid path")
    sys.exit(1)

directory_name = path.split('/')[-1]

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

files_list = [i for i in os.listdir(path) if i.endswith('.vm')]

if not path.endswith('/'):
    path = path + '/'

for vm_file in files_list:
    with open(path + vm_file) as f:
        all_files += f.readlines()

data_dict2 = {i: all_files[i].strip().split(' ') for i in range(len(all_files)) if all_files[i][0] != '/' and all_files[i] != '\n'}
functions_dict = {f'{directory_name}.{value[1]}': 0 for key, value in data_dict2.items() if value[0] == 'call'}

for i in files_list:
    file_name = i.split('.')[0]
    with open(path + i) as f:
        file = f.readlines()

    data_dict = {i: file[i].strip().split(' ') for i in range(len(file)) if file[i][0] != '/' and file[i] != '\n'}

    x = 0
    for key, value in data_dict.items():
        comment = '// ' + ' '.join(value)
        if value[0] in 'eq gt lt':
            instruction = operations[value[0]].replace('[x]', str(x))
            x += 1
        elif value[0] == 'return':
            instruction = '@LCL\nD=M\n@5\nA=D-A\nD=M\n@retAddr\nM=D\n' \
                          '@SP\nA=M-1\nD=M\n@ARG\nA=M\nM=D\n' \
                          'D=A+1\n@SP\nM=D\n' \
                          '@LCL\nA=M-1\nD=M\n@THAT\nM=D\n' \
                          '@LCL\nD=M-1\nA=D-1\nD=M\n@THIS\nM=D\n' \
                          '@LCL\nD=M\n@3\nA=D-A\nD=M\n@ARG\nM=D\n' \
                          '@LCL\nD=M\n@4\nA=D-A\nD=M\n@LCL\nM=D\n' \
                          '@retAddr\nA=M\n0;JMP\n'
        elif value[0] in operations:
            instruction = operations[value[0]]
        elif value[1] == 'static':
            instruction = f'@{file_name}.{value[2]}\n'
            if value[0] == 'push':
                instruction = instruction + 'D=M\n@SP\nM=M+1\nA=M-1\nM=D\n'
            else:
                instruction = '@SP\nAM=M-1\nD=M\n' + instruction + 'M=D\n'

        elif value[0] == 'label':
            instruction = '(' + value[1] + ')\n'
        elif 'goto' in value[0]:
            if 'if' in value[0]:
                instruction = f'@SP\nAM=M-1\nD=M\n@{value[1]}\nD;JNE\n'
            else:
                instruction = f'@{value[1]}\n0;JMP\n'
        elif value[0] == 'call':
            i = functions_dict[f'{directory_name}.{value[1]}']
            instruction = f'@{directory_name}.{value[1]}$ret.{i}\nD=A\n@SP\nM=M+1\nA=M-1\nM=D\n' \
                          f'@LCL\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n' \
                          f'@ARG\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n' \
                          f'@THIS\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n' \
                          f'@THAT\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n' \
                          f'@SP\nD=M\n@{5+int(value[2])}\nD=D-A\n@ARG\nM=D\n' \
                          f'@SP\nD=M\n@LCL\nM=D\n' \
                          f'@{directory_name}.{value[1]}\n0;JMP\n' \
                          f'({directory_name}.{value[1]}$ret.{i})\n'
            functions_dict[f'{directory_name}.{value[1]}'] += 1
        elif value[0] == 'function':
            instruction = f'({directory_name}.{value[1]})\n' + '@0\nD=A\n@SP\nM=M+1\nA=M-1\nM=D\n' * int(value[2])
        else:
            if value[1] == 'pointer':
                if value[2] == '0':
                    value[1] = 'this'
                else:
                    value[1] = 'that'
                if value[0] == 'push':
                    instruction = f'@{memory_segments[value[1]]}\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n'
                elif value[0] == 'pop':
                    instruction = f'@SP\nAM=M-1\nD=M\n@{memory_segments[value[1]]}\nM=D\n'
            elif value[0] == 'push':
                if value[1] == 'constant':
                    instruction = f'@{value[2]}\nD=A\n@SP\nM=M+1\nA=M-1\nM=D\n'
                elif value[1] == 'temp':
                    instruction = f'@{memory_segments[value[1]] + int(value[2])}\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n'
                elif value[2] == '0':
                    instruction = f'@{memory_segments[value[1]]}\nA=M\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n'
                else:
                    instruction = f'@{memory_segments[value[1]]}\nD=M\n@{value[2]}\nA=A+D\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n'
            elif value[0] == 'pop':
                if value[1] == 'temp':
                    instruction = f'@SP\nAM=M-1\nD=M\n@{memory_segments[value[1]] + int(value[2])}\nM=D\n'
                elif value[2] == '0':
                    instruction = f'@SP\nAM=M-1\nD=M\n@{memory_segments[value[1]]}\nA=M\nM=D\n'
                else:
                    instruction = f'@{memory_segments[value[1]]}\nD=M\n@{value[2]}\nD=D+A\n@SP\nM=M-1\nA=M+1\nM=D\nA=A-1' \
                                  f'\nD=M\nA=A+1\nA=M\nM=D\n'
            else:
                instruction = ''
        if file_name == 'Sys':
            sys_asm[f'{file_name}.{key}'] = comment + '\n' + instruction
        else:
            assembly[f'{file_name}.{key}'] = comment + '\n' + instruction
if len(files_list) > 1:
    sys_init = {'sys.init': f'// Sys.init\n@256\nD=A\n@SP\nM=D\n'
                            f'@{directory_name}.Sys.init\nD=A\n@SP\nM=M+1\nA=M-1\nM=D\n'
                            f'@LCL\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n'
                            f'@ARG\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n'
                            f'@THIS\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n'
                            f'@THAT\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n'
                            f'@SP\nD=M\n@{5}\nD=D-A\n@ARG\nM=D\n'
                            f'@SP\nD=M\n@LCL\nM=D\n'}
else:
    sys_init = {}

sys_asm = {**sys_init, **sys_asm}
all_asm = {**sys_asm, **assembly}

with open(path + directory_name + '.asm', 'w') as file:
    for value in all_asm.values():
        file.write(value)
