#import subprocess
import paramiko        
ssh = paramiko.SSHClient()

user = "root"

f = open("server.txt", "r")

password = f.read()

f.close()

server = '192.168.0.100'

#cmd_to_execute = "sudo systemctl restart boris.service"
#cmd_to_execute = "sudo systemctl status boris.service"
cmd_to_execute = "sudo /sbin/shutdown -h now"


ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

ssh.connect(server, username=user, password=password)

ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd_to_execute)


print(ssh_stdin.readlines())
#print(ssh_stdout.readlines())
print(ssh_stderr.readlines())


for line in ssh_stdout.readlines():
    print(line)
