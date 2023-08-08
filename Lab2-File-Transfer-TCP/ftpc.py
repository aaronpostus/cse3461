import socket
import sys
import os.path

#Author: Aaron Post

if len(sys.argv) != 4:
	print("Please provide exactly 3 arguments (ip address, port number, filename)")
	sys.exit(1)

host = sys.argv[1]
port = int(sys.argv[2])
filename = sys.argv[3]
path = "client_files/" + filename

# read from file in binary mode
try:
	input = open(path,"rb")
except OSError:
	print('File does not exist. Cannot read.')
	print('Ensure you are placing the file in client_files and are inputting the name of the file with the extension.')
	sys.exit(1)

print("Server IP: " + host)
print("Client IP: " + socket.gethostbyname(socket.gethostname()))
print("Port: ", port)
print("File: ", path)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
	sock.connect((host, port))
	filesize = os.path.getsize(path);
	# send file size
	sock.sendall(filesize.to_bytes(4, byteorder = 'big'))
	data = sock.recv(4)
	# send file name
	sock.sendall(bytes(filename,'utf-8'))
	data = sock.recv(20)
	endOfStream = False
	# reads up to 1000 bytes at a time and will return 0 if at EOS
	while not (endOfStream):
		data = input.read(1000)
		# empty string so we have reached EOS
		if not(data):
		    endOfStream = True
		else:
			# send up to 1000 bytes at a time
			sock.sendall(data)
			sock.recv(1000)
input.close()
