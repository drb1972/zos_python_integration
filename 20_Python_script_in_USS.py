# Python script in USS ------------------------------------------------
# - Retrieve all member names from a PDS: PROD001.TENNIS             
# - Retrieve the content of the first member                          
#----------------------------------------------------------------------
import subprocess

def execute_command(command):
    try:
        result = subprocess.run(command, 
            shell=True, text=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print("Command execution failed.")
        print("Return Code:", e.returncode)
        print("Error:", e.stderr)
    return result.stdout, result.stderr, result.returncode  

pds = 'PROD001.TENNIS'

members, ste, rc = execute_command(f'tsocmd "listds \'{pds}\' members"')
members = [x.strip() for x in members.split('\n')]
members = members.split('--MEMBERS--')[0]
print(f'{pds}')
print('-'*25)
for member in members:
    print(member)

frstmem = members[0]
file_content, ste, rc = execute_command(f'cat "//\'{pds}({frstmem})\'"')
print(f'{pds}({frstmem})')
print('-'*25)
print(file_content)