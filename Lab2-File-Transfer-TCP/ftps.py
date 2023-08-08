import socket
import sys
import os.path
import math

#Author: Aaron Post

if len(sys.argv) != 2:
	print("Please provide exactly 1 argument (port number)")
	sys.exit(1)

host = socket.gethostbyname(socket.gethostname())
port = int(sys.argv[1])
print("Server IP: " + host)
print("Port: ", port)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
	sock.bind((host, port))
	sock.listen()
	# address not utilized yet
	connection, address = sock.accept()
	with connection:
		# number of bytes in file -- will later be used to 
		numofbytes = connection.recv(4)
		connection.sendall(numofbytes)
		# file name
		filename = connection.recv(20).decode('utf-8');
		connection.sendall(bytes(filename,'utf-8'));
		path = "server_files/" + filename
		output = open(path, "ab")
		print("Received file with name :", filename)
		filesize = int.from_bytes(numofbytes,'big')
		print("File Size is :", filesize, "bytes")
		print("Writing file to :",path)
		# use file size to determine appropriate number of receive calls
		for x in range(math.ceil(filesize/1000)):
			data = connection.recv(1000)
			if not data:
				break
			output.write(data)
			connection.sendall(data)
		output.close()
print("Completed writing file.")
