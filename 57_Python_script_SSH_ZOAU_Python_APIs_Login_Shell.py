# Python script in USS using ZOAU Python APIs & SSH Login Shell--------
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

    login = (
        f"sh -L -c 'python -c \"from zoautil_py import datasets; "
         )

    remote_command = (login + command) 

    # Execute the remote command
    stdin, stdout, stderr = client.exec_command(remote_command)

    out = stdout.read().decode() 
    client.close()
    return out

pds = 'PROD001.TENNIS'

command = f"print(datasets.list_members(\\\"{pds}\\\"))\"'"

members = execute_command(command)
# Convert the output to a list since it is newline-separated
members = members.splitlines()
print(f'{pds}')
print('-'*25)
# Convert the string to a list
members = members[-1].strip("[]").replace("'", "").split(", ")
for item in members:
    print(item)

frstmem = members[0]
command = f"print(datasets.read(\\\"{pds}({frstmem})\\\"))\"'"
file_content = execute_command(command)

# To get rid of the headers I know in my text there is no '=' signs
clean_output = "\n".join(
    line for line in file_content.splitlines()
    if "=" not in line
    and not line.strip().startswith("export")
)
print(f'{pds}({frstmem})')
print('-'*25)
print(clean_output)