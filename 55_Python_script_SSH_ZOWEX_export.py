# Python script in USS using ZOWEX & SSH Explicit environment data ---- 
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

    exports= (
        "export PATH=/u/users/group/zowex/zx.0.1.9;")

    remote_command = (exports + command) 

    # Execute the remote command
    stdin, stdout, stderr = client.exec_command(remote_command)

    out = stdout.read().decode() 

    client.close()
    return out

pds = 'PROD001.TENNIS'

command = f'zowex ds lm "{pds}"'
members = execute_command(command)

members = [x.strip() for x in members.split('\n')]
print(f'{pds}')
print('-'*25)
for member in members:
    print(member)

frstmem = members[0]
# print('firstmem: ',frstmem)
file_content = execute_command(f'zowex ds view "{pds}({frstmem})"')
print(f'{pds}({frstmem})')
print('-'*25)
print(file_content)