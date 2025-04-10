# Python script & Zowe API ML------------------------------------------
# - Retrieve all member names from a PDS: PROD001.TENNIS            
# - Retrieve the content of the first member    
#----------------------------------------------------------------------
import yaml
import requests

with open('config.yaml', 'r') as f: 
   confile = yaml.safe_load(f) 

base_uri = confile['base_uri']
api_port = confile['api_port']
credentials = confile['credentials']

def get_data(type=''):
    url = f'{base_uri}:{api_port}/{base_path}/{parms}'
    headers = {
        'Authorization': f'Basic {credentials}',
        'Content-Type': 'application/json',
        'X-CSRF-ZOSMF-HEADER': ''
    }
    response = requests.get(url, headers=headers, verify=True)
    if type == 'text': return response.text
    else: return response.json()

pds = 'PROD001.TENNIS'
base_path = 'ibmzosmf/api/v1/zosmf/restfiles'

# list members
parms = f'ds/{pds}/member'
members = get_data()
print(f'{pds}')
print('-'*25)
members = [item['member'] for item in members['items']]
for member in members:
    print(member)

# Retrieve the content for the first member [0]
member = members[0]
parms = f'ds/{pds}({member})'
file_content = get_data('text')
print(f'{pds}({member})')
print('-'*25)
print(file_content)