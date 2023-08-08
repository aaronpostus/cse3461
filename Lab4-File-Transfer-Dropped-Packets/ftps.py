import socket
import sys
import os.path
import math

# Author: Aaron Post

# functions

# grabs the header from a packet and adds an ACK bit at the end
# ip : port : flag : ACK (seq number)
def ack(data):
	head = data[0:6]
	ackflag = 4
	seqnum = data[7:8]
	print(len(head + ackflag.to_bytes(1, 'big') + seqnum))
	return head + ackflag.to_bytes(1, 'big') + seqnum

def complement(data):
	if(data == 1):
		return 0
	elif(data ==0):
		return 1
	else:
		# this is a grave error and should not happen
		return -1289739821738921783271

def nack(data):
	head = data[0:6]
	ackflag = 4
	seqnum = int.from_bytes(data[7:8],byteorder='big')
	seqnum = complement(seqnum)
	n = head + ackflag.to_bytes(1, 'big') + seqnum.to_bytes(1, 'big')
	print(int.from_bytes(data[7:8],byteorder='big'),"before")
	print(int.from_bytes(n[7:8],byteorder='big'),"after")
	return n

# main program

if len(sys.argv) != 3:
	print("Please provide exactly 2 arguments (local port of this system, troll port of this system)")
	sys.exit(1)

localhost = socket.gethostbyname(socket.gethostname())
localport = int(sys.argv[1])
trollport = int(sys.argv[2])

print("Server IP: " + localhost)
print("Port: ", localport)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((localhost, localport))

print("Socket bound; UDP Server listening for client packets.")

lastsegment = None
sequencenum = 0
segmentcount = 0
output = None

while(True):
	# receive up to 1010 bytes
	segment = sock.recv(1010)
	if(int.from_bytes(segment[7:8],byteorder='big') == sequencenum):
		if(int.from_bytes(segment[6:7],byteorder='big') == 1):
			print("Received first segment with file size. Sending ACK to client.")
			# extract file size segment
			filesize = int.from_bytes(segment[8:len(segment)],byteorder='big')
			print(f"Incoming file has a size of {filesize} bytes.")
		elif(int.from_bytes(segment[6:7],byteorder='big') == 2):
			print("Received second segment with file name. Sending ACK to client.")
			filename = segment[8:len(segment)].decode('utf-8').rstrip('\x00')
			print(f"Incoming file is named {filename}.")

			# now we open a file output stream and we know how many packets to expect based on the filesize.
			path = "server_files/" + filename

			# open file in append mode
			output = open(path, "ab")
		elif(int.from_bytes(segment[6:7],byteorder='big') == 3):
			print("Received file data segment. Sending ACK to client.")
			output.write(segment[8:len(segment)])
			segmentcount = segmentcount + 1
		else:
			# wrong flag
			print("Wrong flag.")
		# send ACK to client
		sock.sendto(ack(segment),('',trollport))
		# flip seq num for alt bit
		sequencenum = complement(sequencenum)

		# if we have the whole file, stop waiting for new data
		if(segmentcount >= math.ceil(filesize/1000)):
			break;
	else:
		print("Received duplicate segment or incorrect seq num. Sending NACK.")
		sock.sendto(ack(segment),('',trollport))

output.close()
sock.close()
print("Completed writing file.")
sys.exit(1)


