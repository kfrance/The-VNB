import subprocess
import os

p = subprocess.Popen('git tag -l', shell=True, stdout=subprocess.PIPE)
version = ""
for line in p.stdout:
	version = line.decode().strip()
	break
tar_file = "the-vnb-" + version + ".tar.gz"
reply = input("Create " + tar_file + "? (Y/n)")
if reply in ['', "yes", "Y", "y", 'Yes', 'YES']:
	os.chdir('../')
	cmd = 'tar czf ' + tar_file + ' --exclude-vcs --exclude=make_tar_ball.py the-vnb'
	print(os.getcwd())
	print(cmd)
	os.system(cmd)

