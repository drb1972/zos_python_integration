# Python script in USS using ZOWEX Python APIs and JCL ----------------
# - Retrieve all member names from a PDS: PROD001.TENNIS             
# - Retrieve the content of the first member via JCL                          
#----------------------------------------------------------------------
from zowe_native_bindings import zds_py as datasets
from zowe_native_bindings import zjb_py as jobs
import time

pds = 'PROD001.TENNIS'

members = datasets.list_members(f'{pds}')
print(f'{pds}')
print('-'*25)
for member in members:
    print(member.name)

frstmem = members[0].name

JCL = f'''//PROD001X JOB (124400000),'MYCOMP',CLASS=A,MSGCLASS=X,
//      NOTIFY=&SYSUID
//STEP01   EXEC PGM=IEBGENER
//SYSPRINT DD  SYSOUT=*
//SYSUT1   DD  DSN={pds}({frstmem}),DISP=SHR
//SYSUT2   DD  SYSOUT=*
//SYSIN    DD  DUMMY'''

jobid = jobs.submit_job(JCL)
# print(jobid)

while jobs.get_job_status(jobid).status != 'OUTPUT':
    time.sleep(1)

spool_files = jobs.list_spool_files(jobid)

for dd in spool_files:
    # print(f"  DD: {dd.ddn} DSN: {dd.dsn} Step: {dd.stepname} ProcStep: {dd.procstep} Key: {dd.key}")
    if 'SYSUT2' in dd.ddn:
        key = int(dd.key)
        break

file_content = jobs.read_spool_file(jobid, key)
print(f'{pds}({frstmem})')
print('-'*25)
print(file_content)