# Python script & Zowe CLI --------------------------------------------
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

command = f'zowe zos-files list all-members "{pds}"'
members, ste, rc = execute_command(command)
print(f'{pds}')
print('-'*25)
print(members)

members = members.splitlines()
frstmem = members[0]
command = f'zowe zos-files view data-set "{pds}({frstmem})"'
file_content, ste, rc = execute_command(command)
print(file_content)