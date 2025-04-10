# Python script SSH Basic USS -----------------------------------------
# - Retrieve all member names from a PDS: PROD001.TENNIS             
# - Retrieve the content of the first member                          
#----------------------------------------------------------------------
import yaml
import paramiko

with open('config.yaml', 'r') as f: 
   confile = yaml.safe_load(f) 

host     = confile['host']
username = confile['username']
password = confile['password']

# Initialize the SSH client
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

def execute_command(command):
    client.connect(host, port=22, username=username, password=password)
    # Execute the remote command
    stdin, stdout, stderr = client.exec_command(command)
    out = stdout.read().decode() 
    client.close()
    return out

pds = 'PROD001.TENNIS'

members, ste, rc = execute_command(f'tsocmd "listds \'{pds}\' members"')
members = [x.strip() for x in members.split('\n')]
members = members.split('--MEMBERS--')[0]
print(f'{pds}')
print('-'*25)
for member in members:
    print(member)

frstmem = members[0]
file_content = execute_command(f'cat "//\'{pds}({frstmem})\'"')
print(f'{pds}({frstmem})')
print('-'*25)
print(file_content)