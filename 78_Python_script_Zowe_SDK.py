# Python script & Zowe SDK --------------------------------------------
# - Retrieve all member names from a PDS: PROD001.TENNIS            
# - Retrieve the content of the first member    
#----------------------------------------------------------------------
import yaml
from zowe.zos_files_for_zowe_sdk import Files

with open('config.yaml', 'r') as f: 
   confile = yaml.safe_load(f) 

profile = {
    "host": f'{confile["host"]}',
    "port": f'{confile["api_port"]}',
    "user": f'{confile["username"]}',
    "password": f'{confile["password"]}'
}

dsn = 'PROD001.TENNIS'
files = Files(profile)

members = files.list_dsn_members(f'{dsn}')
members = [item['member'] for item in members['items']]
for member in members:
    print(member)

frstmem = members[0]
file_content = files.get_dsn_content(f'{dsn}({frstmem})')
print(file_content)