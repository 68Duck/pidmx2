import paramiko
import socket
from getpass import getpass

class Raspberry_pi_manager(object):
    def __init__(self,ip,password):
        self.ip = ip
        self.password = password
        self.run_file_client = paramiko.SSHClient()
        self.run_file_client.load_system_host_keys()
        self.run_file_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.universe_data = [0]*512

    def connect_client(self):
        self.client.connect((self.ip,12345))
        print("CLIENT: connected")
        msg = "test"
        self.client.send(msg.encode())
        from_server = self.client.recv(4096).decode()
        # print("Recieved: "+ from_server)

    def send_command(self,command):
        self.client.send(command.encode())
        from_server = self.client.recv(4096).decode()
        # print("Recieved: "+ from_server)
        return from_server

    def run_file(self):
        try:
            self.run_file_client.connect(self.ip,"22","pi",self.password)
            dir = "/var/www/dmx"
            command = "sudo python raspberry_pi_connection_test2.py"
            stdin, stdout, stderr = self.run_file_client.exec_command('sudo  fuser -k 12345/tcp')
            stdin, stdout, stderr = self.run_file_client.exec_command(f'cd {dir}; {command}',get_pty=True)
            stdout.channel.set_combine_stderr(True)
            self.test = stdout
        except paramiko.ssh_exception.AuthenticationException:
            raise Exception("Incorrect password. Please try again")
        except TimeoutError:
            raise Exception("Could not connect. Please try again later")
        except paramiko.ssh_exception.NoValidConnectionsError: #this happend when the address is of something else so you cannot ssh into it
            raise Exception("The ipv4 is incorrect. Please try again.")

    def send_stop(self):
        self.client.send("stop".encode())
        from_server = self.client.recv(4096).decode()
        # print("Recieved: "+ from_server)

    def set_data(self,channel_number,data):
        if isinstance(channel_number,float): #checks if the id is a float
            raise Exception("The id needs to be an integer.")
            return
        try:
            channel_number = int(channel_number) #converts the id to an integer as this is required to send the dmx
        except:
            raise Exception("The id is not an integer. Please try again")
            return
        if channel_number>512 or channel_number<1: #checks if the id is in range
            raise Exception("The id value needs to be between 1 and 512 inclusive.")
            return
        if isinstance(data,float): #checks if the data value is a float
            raise Exception("The data value needs to be an integer")
            return
        try:
            data = int(data)
        except:
            raise Exception("The data value is not an integer. Please try again")
            return
        if data > 255 or data < 0:
            raise Exception("The data value needs to be between 0 and 255 inclusive")
            return
        self.universe_data[channel_number-1] = data


    def send_data(self):
        data_to_send = ""
        for data in self.universe_data:
            data_to_send = str(data_to_send) + "," + str(data)
        data_to_send = data_to_send[1:len(data_to_send)]
        self.client.send(data_to_send.encode())
        from_server = self.client.recv(4096).decode()
        # print("Recieved: "+ from_server)

    def __del__(self):
        try:
            self.client.send("stop".encode())
        except Exception as e:
            print(e)
        try:
            self.run_file_client.exec_command(chr(3))
        except Exception as e:
            print(e)
        try:
            self.run_file_client.close()
            self.client.shutdown(1)
            self.client.close()
        except Exception as e:
            print(e)
