#------------------- PYMA - Python & Mainframe library ----------------------
# Use 'import pyma' at the top of your code to access these functions
#----------------------------------------------------------------------------

#------------------- Required Libraries -------------------------------------
import requests
import subprocess
import json
#----------------------------------------------------------------------------

#------------------- Execute Command ----------------------------------------
# args: 
#    'command'(str) command to be executed
# -----
# returns: stdout, stderr, returncode  
# -----
def execute_command(command):
   try:
      result = subprocess.run(command, shell=True, text=True, capture_output=True)

   except subprocess.CalledProcessError as e:
      print("Command execution failed.")
      print("Return Code:", e.returncode)
      print("Error:", e.stderr)
      # exit(8) # Uncoment under expected app behavior 

   if result.returncode!=0:
      print('rc', result.returncode)
      print('sto ', result.stdout)
      print('ste ', result.stderr)
      # exit(8) # Uncoment under expected app behavior 

   return result.stdout, result.stderr, result.returncode 
#----------------------------------------------------------------------------

#------------------- API Request - z/OSMF -----------------------------------
import requests
# execute_command
# args: 
#    'credentials'(str) base64 format - dXNlcmlkOnBhc3N3b3Jk
#    'apiml_url'(str) z/OSMF url (usually lpar hostname/ip)
#    'port'(str) z/OSMF port (def. 443)
#    'base_path'(str) full base path i.e. f'zosmf/restfilesds/{pds}/member'
#    'parms'(str) 
# -----
# returns: text str or json object
# -----
def zosmf_request(credentials, 
                  zosmf_url, 
                  port,
                  base_path):
    apiml_uri   = f'https://{zosmf_url}'
    url         = f'{apiml_uri}:{port}/{base_path}'
    headers = {
        'Authorization': f'Basic {credentials}',
        'Content-Type': 'application/json',
        'X-CSRF-ZOSMF-HEADER': ''
    }
    return requests.get(url, headers=headers, verify=True)
#----------------------------------------------------------------------------

#------------------- Zowe Issue Console Command -----------------------------
# args: 
#    'command'(str) - without quotes
#    'prof'(str) - Optional f'--zosmf-p {your-zosmf-prof}' 
# -----
# returns:  stdout, stderr, returncode
# -----
def issue_console_command(command, prof=''):
   command=f'zowe zos-console issue command "{command}" {prof}'
   print(command)
   sto, ste, rc = execute_command(command)
   return(sto,ste,rc)
#----------------------------------------------------------------------------

#------------------- Zowe Create Terse Type File ----------------------------
# args: 
#    'file'(str) - File to create with Terse format
#    'prof'(str) - Optional f'--zosmf-p {your-zosmf-prof}' 
# -----
# returns: stdout, stderr, returncode
# returns:
def cre_trs_file(file, prof=''):
   command=f'zowe zos-files create ps "{file}" --rl 1024 --bs 1024 --rf FB --sz 100CYL {prof}'
   sto, ste, rc = execute_command(command)
   return(sto,ste,rc)
#----------------------------------------------------------------------------

#------------------- Zowe Submit Local JCL ----------------------------------
# args: 
#    'jcl'(str) local file name - full path if not in same dir
#        sample: jcl='./jcl/my_jcl.jcl' 
#    'prof'(str) - Optional f'--zosmf-p {your-zosmf-prof}' 
# -----
# returns: stdout, stderr, returncode
# -----
def submit_local_jcl(jcl,prof=''):
   command=f'zowe zos-jobs submit local-file "{jcl}" {prof} --wfo --rfj'
   sto, ste, rc = execute_command(command)
   response = json.loads(sto)
   ret_cod=response.get('data', {}).get('retcode')
   jobid=response.get('data', {}).get('jobid')
   return(ret_cod,jobid)    
#----------------------------------------------------------------------------

#------------------- Check Valid Data Set Name ------------------------------
# args: 
#    'file'(str) file name to check
# -----
# returns: True/False, message(str)
# -----
def check_zos_file_name(file):
   file=file.upper()
   tf=True
   message='Correct File Name'
   if len(file)>44:
      tf=False
      message='Error: A data set name cannot be longer than 44 characters'
   elif '.' not in file:
      tf=False
      message='Error: A data set name must be composed of at least two joined character segments (qualifiers), separated by a period (.)'
   elif '..' in file:
      tf=False
      message='Error: A data set name cannot contain two successive periods'
   elif file[-1]=='.':
      tf=False
      message='Error: A data set name cannot end with a period'
   else:
      hlqs=file.split('.')
      valid_first_char=''.join(chr(i) for i in range(ord('A'), ord('Z') + 1))+'#@$'
      valid_rest =''.join(chr(i) for i in range(ord('0'), ord('9') + 1))+valid_first_char+'-'
      for hlq in hlqs:
         if len(hlq)>8:
            tf=False
            message='Error: A segment cannot be longer than eight characters'
         elif hlq[0] not in valid_first_char:
            tf=False
            message='Error: The first segment character must be either a letter or one of the following three special characters: #, @, $'
         else: 
            for i in hlq[1:]:
               if i not in valid_rest:
                  tf=False
                  message='Error: The remaining seven characters in a segment can be letters, numbers, special characters (only #, @, or $), or a hyphen (-)'

   return(tf,message)
#----------------------------------------------------------------------------