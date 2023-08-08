import socket
import sys
import os.path
import math

# Author: Aaron Post

# grabs the header from a packet and adds an ACK bit at the end
# ip : port : flag : ACK
def ack(data):
	nd = data[:7]
	x = int(True)
	return nd + x.to_bytes(1,byteorder='big')

if len(sys.argv) != 2:
	print("Please provide exactly 1 argument (local port of this system)")
	sys.exit(1)

localhost = socket.gethostbyname(socket.gethostname())
localport = int(sys.argv[1])

print("Server IP: " + localhost)
print("Port: ", localport)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((localhost, localport))

print("Socket bound; UDP Server listening for client packets.")

# receive first packet (size 11 bytes)
data, address = sock.recvfrom(11)
# check for incorrect packet size
if(len(data) != 11):
	print("Error. First packet had an unexpected size.")
# check for wrong flag number
flag = int.from_bytes(data[6:7],byteorder='big')
if(flag != 1):
	print("Error. First packet had an unexpected flag number.")
print("Received first packet. Sending ACK to client.")
# send ACK to client
sock.sendto(ack(data),address)
# extract file size segment
filesize = int.from_bytes(data[7:len(data)],byteorder='big')
print(f"Incoming file has a size of {filesize} bytes.")

# receive second packet (size 27 bytes)
data, address = sock.recvfrom(27)
# check for incorrect packet size
if(len(data) != 27):
	print("Error. Second packet had an unexpected size.")
# check for wrong flag number
flag = int.from_bytes(data[6:7],byteorder='big')
if(flag != 2):
	print("Error. Second packet had an unexpected flag number.")
print("Received second packet. Sending ACK to client.")
# send ACK to client
sock.sendto(ack(data),address)
# extract file name segment
filename = data[7:len(data)].decode('utf-8').rstrip('\x00')
print(f"Incoming file is named {filename}.")

# now we open a file output stream and we know how many packets to expect based on the filesize.
path = "server_files/" + filename

# open file in append mode
output = open(path, "ab")
# use file size to determine appropriate number of receive calls
count = 0
for x in range(math.ceil(filesize/1000)):
	data = sock.recv(1007)
	if not data:
		break
	count = count + 1
	if(len(data) < 8):
		print("Error. File data packet had an unexpected size.")
		continue
	# check for wrong flag number
	flag = int.from_bytes(data[6:7],byteorder='big')
	if(flag != 3):
		print("Error. File data packet had an unexpected flag number.")
		continue
	output.write(data[7:len(data)])
	sock.sendto(ack(data),address)
output.close()
print(f"Received {count} file data packets and responded with {count} ACKs.")
print("Completed writing file.")
