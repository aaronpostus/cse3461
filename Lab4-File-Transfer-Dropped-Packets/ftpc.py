import socket
import sys
import os.path
import time
import select

# Author: Aaron Post

localhost = socket.gethostbyname(socket.gethostname())
localport = 31295
remotehost = sys.argv[1]
remoteport = int(sys.argv[2])
trollport = int(sys.argv[3])
filename = sys.argv[4]
sleeptime = 0.0030
timeouttime = 0.050
path = "client_files/" + filename

# functions

# creates a UDP packet with an appropriate header. assumes flag is not yet in binary mode but data is.
# 4 byte ip, 2 byte port, 1 byte flag, 1 byte sqn for header
def create_udp_packet(flag, seqnum, data):
	ip = socket.inet_aton(remotehost)
	port = remoteport.to_bytes(2, byteorder = 'big')
	fl = flag.to_bytes(1, byteorder = 'big')
	sqn = seqnum.to_bytes(1, byteorder = 'big')
	return ip + port + fl + sqn + data

# check for invalid ack segment (where data is a segment in byte order)
def check_ack(data):
	return len(data) >= 8

def complement(data):
	if(data == 1):
		return 0
	elif(data ==0):
		return 1
	else:
		# this is a grave error and should not happen
		return -1289739821738921783271

# truncate byte order data segment to a one byte integer
# precond: data arg must be at least 8 bytes long
def value_ack(data):
	return int.from_bytes(data[7:8],byteorder='big')

# we assume the name fits, but we may need to pad out with null bytes
def convert_to_bytes(string,length):
    # convert string to bytes
    bytes = string.encode()
    if len(bytes) < length:
        bytes = bytes.ljust(length,b'\0')
    return bytes

# main program

# check args
if len(sys.argv) != 5:
	print("Please provide exactly 4 arguments (ip address of this system, remote port on system 2, troll port of this system, filename)")
	sys.exit(1)

# read from file in binary mode
try:
	input = open(path,"rb")
except OSError:
	print('File does not exist. Cannot read.')
	print('Ensure you are placing the file in client_files and are inputting the name of the file with the extension.')
	sys.exit(1)

# create socket and bind to local host and troll port
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((localhost, localport))

# first segment - file size (flag of 1)
flag = 1
filesize = os.path.getsize(path)

sequencenum = 0
data = create_udp_packet(flag, sequencenum, filesize.to_bytes(4, byteorder = 'big'))

# continue sending segment to the server until we are ACKed.

print('Sending segment 1 to server.')

while(True):
	sock.sendto(data,('',trollport))
	read, write, error = select.select([sock], [], [], timeouttime)
	if(len(read) > 0):
		print("length > 0")
		validack = False
		acksegment = read[0].recv(8)
		if(check_ack(acksegment)):
			print(3)
			if(sequencenum == value_ack(acksegment)):
				print('Received ACK from server for segment 1.')
				validack = True
				break
		if(not validack):
			time.sleep(sleeptime)
			print('Received invalid ACK from server for segment 1. Resending segment.')
			continue
	elif(read == [] and write == [] and error == []):
		time.sleep(sleeptime)
		print("Timed out for segment 1 ACK (file size). Resending segment.")
		continue

# wait in between packets
time.sleep(sleeptime)

# create segment 2
flag = 2
sequencenum = complement(sequencenum)
segment = create_udp_packet(flag, sequencenum, convert_to_bytes(filename,20))

# continue sending segment to the server until we are ACKed.
print('Sending segment 2 to server.')
while(True):
	sock.sendto(segment,('',trollport))
	read, write, error = select.select([sock], [], [], timeouttime)
	if(len(read) > 0):
		validack = False
		acksegment = read[0].recv(8)
		if(check_ack(acksegment)):
			if(sequencenum == value_ack(acksegment)):
				print('Received ACK from server for segment 2.')
				validack = True
				break
		if(not validack):
			time.sleep(sleeptime)
			print('Received invalid ACK from server for segment 2. Resending segment.')
			continue
	elif(read == [] and write == [] and error == []):
		time.sleep(sleeptime)
		print("Timed out for segment 2 ACK (file name). Resending segment.")
		continue

# send file data segments up to 1000 bytes at a time, plus header) and wait for ACKs between. flag of 3.
flag = 3
count = 0
failedsegments = 0

while (True):
	sequencenum = complement(sequencenum)
	segment = input.read(1000)
	# empty string so we have reached EOS
	if not(segment):
	    break;
	count = count + 1
	segment = create_udp_packet(flag, sequencenum, segment)

	while(True):
		# wait in between packets
		time.sleep(sleeptime)
		sock.sendto(segment,('',trollport))
		print('Sending file data segment to server.')
		read, write, error = select.select([sock], [], [], timeouttime)
		if(len(read) > 0):
			validack = False
			acksegment = read[0].recv(8)
			if(check_ack(acksegment)):
				if(sequencenum == value_ack(acksegment)):
					print('Received ACK from server for a file data segment.')
					validack = True
					break
			if(not validack):
				print('Received invalid ACK from server for a file data segment. Resending segment.')
				failedsegments = failedsegments + 1
		elif(read == [] and write == [] and error == []):
			print("Timed out for a file data segment. Resending segment.")
			failedsegments = failedsegments + 1

print(f"Sent {count + failedsegments} file data segments to server. {failedsegments} retransmissions occurred.")
input.close()
sys.exit(1)

	
