#import subprocess
import paramiko        
ssh = paramiko.SSHClient()

user = "boris"

f = open("server.txt", "r")

password = f.read()

f.close()

server = '192.168.0.213'

#cmd_to_execute = "sudo systemctl restart boris.service"
cmd_to_execute = "sudo systemctl status boris.service"

ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

ssh.connect(server, username=user, password=password)

ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd_to_execute)


#print(ssh_stdin)
#print(ssh_stdout.readlines())
#print(ssh_stderr)


for line in ssh_stdout.readlines():
    print(line)
