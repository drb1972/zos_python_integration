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

    # login = (
    #     f"sh -L -c 'python -c \"from zowe_native_bindings import zds_py as datasets; "
    #      )

    login = (
        "sh -L -c ' "
            )

    remote_command = (login + command) 

    # Execute the remote command
    stdin, stdout, stderr = client.exec_command(remote_command)

    out = stdout.read().decode() 
    client.close()
    return out

pds = 'PROD001.TENNIS'

command = f"zowex ds lm {pds} '"

members = execute_command(command)
print(f'{pds}')
print('-'*25)
# Convert the output to a list and get rid of echo from Login shell
members = [line.strip() for line in members.splitlines() if line.strip() and '=' not in line]
for member in members:
    print(member)

frstmem = members[0]
command = f"zowex ds view \"{pds}({frstmem})\" '"

# command = f"print(datasets.read(\\\"{pds}({frstmem})\\\"))\"'"
file_content = execute_command(command)


# To get rid of the headers I know in my text there is no '=' signs
clean_output = "\n".join(
    line for line in file_content.splitlines()
    if "=" not in line
    # and not line.strip().startswith("export")
)
print(f'{pds}({frstmem})')
print('-'*25)
print(clean_output)