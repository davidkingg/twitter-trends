# from subprocess import call

# with open('run-docker.sh', 'rb') as file:
#     script = file.read()
# rc = call(script, shell=True)
# file.close()


import subprocess
exit_code = subprocess.call('./run-docker.sh')
print(exit_code)