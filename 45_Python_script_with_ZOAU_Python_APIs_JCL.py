# Python script in USS using ZOAU Python APIs and JCL -----------------
# - Retrieve all member names from a PDS: PROD001.TENNIS             
# - Retrieve the content of the first member via JCL                          
#----------------------------------------------------------------------
from zoautil_py import datasets, jobs

pds = 'PROD001.TENNIS'

members = datasets.list_members(f'{pds}')
print(f'{pds}')
print('-'*25)
for member in members:
    print(member)

frstmem = members[0]

JCL = f'''//PROD001X JOB (124400000),'MYCOMP',CLASS=A,MSGCLASS=X,
//      NOTIFY=&SYSUID
//STEP01   EXEC PGM=IEBGENER
//SYSPRINT DD  SYSOUT=*
//SYSUT1   DD  DSN={pds}({members[0]}),DISP=SHR
//SYSUT2   DD  SYSOUT=*
//SYSIN    DD  DUMMY'''

datasets.write(f'{pds}(JCL)', content=JCL)

jobid = jobs.submit (f'{pds}(JCL)').id

datasets.delete_members(f'{pds}(JCL)')

file_content = jobs.read_output(f'{jobid}', 'STEP01', 'SYSUT2')

print(f'{pds}({frstmem})')
print('-'*25)
print(file_content)