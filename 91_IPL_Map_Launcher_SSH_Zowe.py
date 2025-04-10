# Script to launch the IPL map process in USS

import subprocess
import paramiko
import yaml
import argparse
import sys

try:
   parser = argparse.ArgumentParser(description='IPL Map ./data folder')
   parser.add_argument('-p','--profile', help='Provide zosmf profile', required=True)
   args = parser.parse_args()
except Exception as exc:
   print(sys.exc_info())
   print(exc)

profile = args.profile.lower()

zosmf_profile = f'--zosmf-p {profile}.zosmf'
ssh_profile = f'--ssh-p {profile}.ssh' 

with open('config_multi.yaml', 'r') as f:
    confile = yaml.safe_load(f)

host     = confile[f'{profile}']['host']
username = confile[f'{profile}']['username']
password = confile[f'{profile}']['password']

# Initialize the SSH client
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())


# Functions -----------------------------------------------------------

def execute_command(command):
    try:
        result = subprocess.run(command,
            shell=True, text=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print("Command execution failed.")
        print("Return Code:", e.returncode)
        print("Error:", e.stderr)
    return result.stdout, result.stderr, result.returncode 

def execute_ssh_command(command):
    client.connect(host, port=22, username=username, password=password)
    exports= (
        "export PATH=/usr/lpp/IBM/zoautil/env/bin:/usr/lpp/IBM/zoautil/bin:/usr/lpp/IBM/cyp/v3r9/pyz/bin:/bin:/usr/lpp/java/current/bin:/usr/lpp/java/current"
        "export LIBPATH=/usr/lpp/IBM/zoautil/lib;"
         )
    remote_command = (exports + command)
    # Execute the remote command
    stdin, stdout, stderr = client.exec_command(remote_command)
    exit_status = stdout.channel.recv_exit_status()  # Blocks until the command finishes
    out = stdout.read().decode()
    err = stderr.read().decode()
    client.close()
    return out, err, exit_status

def disp_msgs(sto, ste, rc):
    print('sto: ', sto)
    print('ste: ', ste)
    print('rc : ', rc)
    exit(1)

def execute_zowe_command(zowe_command):
    print(f'{zowe_command}')
    sto, ste, rc = execute_command(zowe_command)
    if rc != 0: disp_msgs(sto, ste, rc)
    return sto

# Functions End -------------------------------------------------------

# Main workflow
if __name__ == "__main__":
    # Retrieve home directory

    # Get 'home' directory
    ssh_command = 'pwd'
    zowe_command = f'zowe uss issue cmd "{ssh_command}" {ssh_profile}'
    sto = execute_zowe_command(zowe_command)
    home = sto.split('$')[1].replace(' ', '').strip()
    print('home: ', home)
    if home=='/': home = '/tmp' 
    # home = "/u/users/group/product/prod001/temp_ipl"
    temp_dir = f'{home}/temp_ipl'

    # Delete temp directory
    zowe_command = f'zowe files del uss "{temp_dir}" -rf {zosmf_profile}'
    # This script doesn't call the execute_zowe_command
    #    because it fails if the directory doesn't exist
    print(f'{zowe_command}')
    sto, ste, rc = execute_command(zowe_command)

    # Create temp directory
    zowe_command = f'zowe files create dir "{temp_dir}" -m rwxrwxrwx {zosmf_profile}'
    sto = execute_zowe_command(zowe_command)
    
    # Upload the ipl_map.py script to temp_ipl
    file = 'ipl_map.py'
    path = f'{temp_dir}/{file}'
    zowe_command = f'zowe files upload ftu "{file}" "{path}" {zosmf_profile}'
    sto = execute_zowe_command(zowe_command)

    # Execute script
    ssh_command = f'cd {temp_dir}; python {path}'
    print(f'{ssh_command}')
    sto, ste, rc = execute_ssh_command(ssh_command)

    # Cleanup temp artifacts
    files = ['temp.jcl','ipl_map.py']
    for file in files:
        path = f'{temp_dir}/{file}'
        zowe_command = f'zowe files delete uss "{path}" -fi {zosmf_profile}'
        sto = execute_zowe_command(zowe_command)

    # Download Data,ipl_map.json, ipl_map.md and sysmols.json in zosmf_prof folder
    folder = f'{profile}'
    zowe_command = f'zowe files download uss-dir "{temp_dir}" -d {folder} {zosmf_profile}'
    sto = execute_zowe_command(zowe_command)

    # Delete temp directory
    zowe_command = f'zowe files del uss "{temp_dir}" -rf {zosmf_profile}'
    sto = execute_zowe_command(zowe_command)