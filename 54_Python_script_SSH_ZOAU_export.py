# Python script in USS using ZOAU & SSH Explicit environment data ----- 
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
        "export PATH=/usr/lpp/IBM/zoautil/env/bin:/usr/lpp/IBM/zoautil/bin:/usr/lpp/IBM/cyp/v3r9/pyz/bin:/bin:/usr/lpp/java/current/bin:/usr/lpp/java/current"
        "export LIBPATH=/usr/lpp/IBM/zoautil/lib;"
         )

    remote_command = (exports + command) 

    # Execute the remote command
    stdin, stdout, stderr = client.exec_command(remote_command)

    out = stdout.read().decode() 
    client.close()
    return out

pds = 'PROD001.TENNIS'

command = f'mls "{pds}"'
members = execute_command(command)
members = [x.strip() for x in members.split('\n')]
print(f'{pds}')
print('-'*25)
for member in members:
    print(member)

frstmem = members[0]
print('firstmem: ',frstmem)
file_content = execute_command(f'dcat "{pds}({frstmem})"')
print(f'{pds}({frstmem})')
print('-'*25)
print(file_content)