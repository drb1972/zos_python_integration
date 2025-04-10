# Script to get the IPL map
# Run in USS
# Items generated:
#    ipl_map.json - Info of LOADxx and PARMLIBs
#    ipl_map.md - Markdown Format
#    symbols.json

from zoautil_py import opercmd
from zoautil_py import datasets
from zoautil_py import zsystem
from zoautil_py import jobs
import json
import os
import time

# Functions -----------------------------------------------------------

# Execute ZOAU oper command 
def oper_command(command, parameters, terse=True):
    out = opercmd.execute(command=f"{command}", parameters=f"{parameters}", terse=True)
    if out.rc == 0:
        out = out.stdout_response
    else:
        print(out.stdout_stderror_response)
        exit(1)
    return out

# Read dataset and copies it into ./data/
#    in the format './data/dsn(member.txt)'
def dataset_read(dsn, member):
    file = f'{dsn}({member})'
    content = datasets.read(f"{file}")
    # Save the member in ./data/
    with open(f'./data/{file}.txt','wt') as o:
        o.write(content)
    return content


# Get PARMLIB members for a type & Suffixes
# i.e. {iplmap}, 'IEASYM', ['00', 'PR', 'IP', 'UR'], 'called from'
def find_members(iplmap, type, type_list, from_mem=''):
    for suffix in type_list:
        member = f'{type}{suffix}'
        parmlib = zsystem.find_parmlib(f'"{member}"')
        if parmlib == '': continue
        print(f'Processing {parmlib} {member}') # dxr
        iplmap[parmlib][member]={}
        iplmap[parmlib][member]['path'] = f'./data/{parmlib}({member}).txt'
        iplmap[parmlib][member]['md'] = f'[{member}](./data/{parmlib}({member}).txt)'
        iplmap[parmlib][member]['from'] = f'{from_mem}'
        iplmap[parmlib][member]['content'] = dataset_read(parmlib, member)
    return iplmap

# Create local jcl
def create_jcl(jcl):
    my_rexx = '''/* rexx */
IsfRC = isfcalls( 'ON' )
address SDSF 'ISFEXEC SYSP'
do i = 1 to isfrows
    say PARM.i VALUE.i MEMBER.i REFNAME.i
end'''

    my_jcl=f'''//PROD001X JOB (124400000),'REXX',CLASS=A,
//      MSGCLASS=X,NOTIFY=&SYSUID                                   
//STEP1    EXEC PGM=IEBGENER
//SYSPRINT DD  SYSOUT=*
//SYSIN    DD  DUMMY
//SYSUT1   DD DATA,DLM='@@'
{my_rexx}
@@
//SYSUT2   DD  DSN=&&TEMPREXX(MYREXX),
//            DISP=(,PASS),UNIT=SYSDA,
//            SPACE=(TRK,(1,1,1)),
//            DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)
/*
//STEP2    EXEC PGM=IKJEFT01,PARM='%MYREXX'
//SYSTSPRT DD  SYSOUT=*
//SYSPRINT DD SYSOUT=* 
//SYSTSIN  DD DUMMY
//SYSEXEC  DD  DSN=&&TEMPREXX,DISP=(OLD,DELETE)
/*
'''

    with open(f'{jcl}','wt') as o:
        o.write(my_jcl)

# Submit local jcl end return stepname - dataset output
def submit_local_jcl(jcl, stepname, dataset):
    job = jobs.submit(f'{jcl}', hfs=True)
    print('jobid: ',job.id)
    job.wait()
    print('rc: ',job.rc)
    if job.rc != '0000':
        output = jobs.list_dds(f'{job.id}')
        print(output)
        for item in output:
            stepname = item['stepname']
            dataset = item['dataset']
            print(jobs.read_output(job.id, stepname, dataset))
        exit(1)
    else:
        output = jobs.read_output(f'{job.id}', f'{stepname}', f'{dataset}')
    return output

# Functions End -------------------------------------------------------

# Main workflow

path = f'./data'
if os.path.exists(path) == False:
    os.mkdir(path)


# Get load_param_dsn, loadxx, ieasym_list, ieasys_list
out = oper_command('d','iplinfo')

# Retrieve values
data = {}
for line in out.split('\n'):
    # Get ieasym & ieasys lists
    if ' LIST = ' in line:
        key, value = line.split(' LIST = ', 1)
        data[key.strip()] = value.strip().strip("'")
    # Get loadxx & iplpar dsn from 'USED LOADPR IN SYS1.IPLPARM ON 04006'
    if 'USED LOAD' in line:
        words = line.split()
        loadxx = words[1]  
        load_param_dsn = words[3]

# Extract, clean, and process the 'IEASYM' list
ieasym_list = data.get('IEASYM', '').replace('(', '').replace(',L)', '').split(',')
ieasys_list = data.get('IEASYS', '').replace(' (OP)', "").replace('(', "").replace(')', "").split(',')
if '00' not in ieasys_list: 
    ieasys_list.append('00') # 'IEASYS00' always exists

# Downlad IPLPARM(loadxx) and create the iplmap dictionary
iplmap={}
iplmap['ds']=load_param_dsn
iplmap['loadxx']=loadxx
iplmap['path']=f'./data/{load_param_dsn}({loadxx}).txt'
iplmap['md']=f'[{load_param_dsn}({loadxx})](./data/{load_param_dsn}({loadxx}).txt)'
iplmap['content']=dataset_read(load_param_dsn, loadxx)


# Get PARMLIBs 
parmlibs = zsystem.list_parmlib()

# Create dict for each parmlib
for parmlib in parmlibs:
    iplmap[parmlib] = {}


# Retrieve info for IEASYS and IEASYM
iplmap = find_members(iplmap, 'IEASYS', ieasys_list)
iplmap = find_members(iplmap, 'IEASYM', ieasym_list)


# Create temporary local jcl
jcl = 'temp.jcl'
create_jcl(f'{jcl}')

# Submit local jcl and retrieve output
stepname = 'STEP2'
dataset  = 'SYSTSPRT'
output = submit_local_jcl(jcl, stepname, dataset)


# Retrieve info for PARMLIB members
parmlib_members = ['LNK','CMD','CON','LPA','OMVS','PROD','PROG','SCH']

lines = output.split('\n')
for line in lines:
    line = line[1:]
    words = line.replace('(', "").replace(')', "").split()
    if len(words) > 3 and words[0] in parmlib_members:
        list = words[1].split(',')
        iplmap = find_members(iplmap, words[3], list, words[2])


# Write the ipl_map dictionary to a JSON file
with open('ipl_map.json', 'w') as json_file:
    json.dump(iplmap, json_file, indent=4)


# Create a markdown file
markdown_content ='''---
markmap:
  colorFreezeLevel: 4
  initialExpandLevel: 4
  spacingVertical: 10
  spacingHorizontal: 80
  duration: 1000 
---
'''
markdown_content += "# PARMLIBs and Active Members\n\n"
markdown_content += f"# Load: {iplmap['md']}\n"
for parmlib, members in iplmap.items():
    if isinstance(members, dict):
        markdown_content += f"## {parmlib}\n"
        for member, details in members.items():
            markdown_content += f"### {details['md']}\n"
            if details['from'] != '':
                markdown_content += f" - from.. {details['from']}\n"
        markdown_content += "\n"


with open('ipl_map.md', 'wt') as o:
    o.write(markdown_content)


# Get system symbols
out = oper_command('d','symbols')

symbols = {}
lines = out.strip().split('\n')

# Skip the first line and process the remaining lines
for line in lines[1:]:
    if '=' in line:  # Check if the line contains a key-value pair
        key, value = line.split('=', 1)
        key = key.strip().rstrip('.')  # Remove trailing period and whitespace
        value = value.strip().strip('"')  # Remove surrounding quotes and whitespace
        symbols[key] = value

# Write the symbols dictionary to a JSON file
with open('symbols.json', 'w') as json_file:
    json.dump(symbols, json_file, indent=4)