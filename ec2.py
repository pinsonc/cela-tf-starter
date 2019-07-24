import paramiko
import boto
import boto3

# credit: https://stackoverflow.com/questions/42645196/how-to-ssh-and-run-commands-in-ec2-using-boto3

IP = input('Enter your instance\'s public IP address: ')
UN = input('Enter your instance\'s login username: ')
print('Connecting...')

key = paramiko.RSAKey.from_private_key_file('/home/connerpinson/Downloads/conner_key.pem')
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
     # Here 'ubuntu' is user name and 'instance_ip' is public IP of EC2
    client.connect(hostname=IP, username=UN, pkey=key)
    print('Connected.')

    # Execute a command(cmd) after connecting/ssh to an instance
    cmd = input('Enter a command (q to exit): ')
    while cmd != 'q':
        stdin, stdout, stderr = client.exec_command(cmd)
        print(stdout.read())
        cmd = input('Enter a command (q to exit): ')

    # close the client connection once the job is done
    client.close()

except Exception as e:
    print(e)
