# Python script in USS using ZOWEX Python APIs ------------------------
# - Retrieve all member names from a PDS: PROD001.TENNIS             
# - Retrieve the content of the first member                          
#----------------------------------------------------------------------
from zowe_native_bindings import zds_py as datasets

pds = 'PROD001.TENNIS'

members = datasets.list_members(f'{pds}')
print(f'{pds}')
print('-'*25)
for member in members:
    print(member.name)

frstmem = members[0].name
file_content = datasets.read_data_set(f'{pds}({frstmem})')
print(f'{pds}({frstmem})')
print('-'*25)
print(file_content)