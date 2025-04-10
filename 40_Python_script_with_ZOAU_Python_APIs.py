# Python script in USS using ZOAU Python APIs--------------------------
# - Retrieve all member names from a PDS: PROD001.TENNIS             
# - Retrieve the content of the first member                          
#----------------------------------------------------------------------
from zoautil_py import datasets

pds = 'PROD001.TENNIS'

members = datasets.list_members(f'{pds}')
print(f'{pds}')
print('-'*25)
for member in members:
    print(member)

frstmem = members[0]
file_content = datasets.read(f'{pds}({frstmem})')
print(f'{pds}({frstmem})')
print('-'*25)
print(file_content)