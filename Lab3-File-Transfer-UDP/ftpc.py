import socket
import sys
import os.path
import time

# Author: Aaron Post

localhost = socket.gethostbyname(socket.gethostname())
localport = 31295
remotehost = sys.argv[1]
remoteport = int(sys.argv[2])
trollport = int(sys.argv[3])
filename = sys.argv[4]
sleeptime = 0.0030
path = "client_files/" + filename

# creates a UDP packet with an appropriate header. assumes flag is not yet in binary mode but data is.
def create_udp_packet(flag, data):
	ip = socket.inet_aton(remotehost)
	port = remoteport.to_bytes(2, byteorder = 'big')
	fl = flag.to_bytes(1, byteorder = 'big')
	return bytes(ip + port + fl + data)

def check_ack(data):
	# check for invalid ack
	if(len(data) != 8):
		print(len(data))
		return False
	# return 1 if ACK flag is 1
	return int.from_bytes(data[7:8],byteorder='big') == 1

# we assume the name fits, but we may need to pad out with null bytes
def convert_to_bytes(string,length):
    # convert string to bytes
    bytes = string.encode()
    if len(bytes) < length:
        bytes = bytes.ljust(length,b'\0')
    return bytes

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


# send first segment (file size)
flag = 1
filesize = os.path.getsize(path)
data = create_udp_packet(flag, filesize.to_bytes(4, byteorder = 'big'))
sock.sendto(data,(localhost,trollport))
print('Sent first packet to server. Waiting for ACK.')

# wait for ACK
while(True):
	data = sock.recv(8)
	if(check_ack(data)):
		print('Received ACK from server.')
		break
	print('Received invalid ACK from server.')
	# add functionality for timeout / retransmission in lab 4

# wait in between packets
time.sleep(sleeptime)

# send second segment (name of file)
flag = 2
data = create_udp_packet(flag, convert_to_bytes(filename,20))
sock.sendto(data,(localhost,trollport))
print('Sent second packet to server. Waiting for ACK.')

# wait for ACK
while(True):
	data = sock.recv(8)
	if(check_ack(data)):
		print('Received ACK from server.')
		break
	print('Received invalid ACK from server.')
	# add functionality for timeout / retransmission in lab 4

flag = 3
endOfStream = False
# send segments that hold data bytes for file (up to 1000 bytes at a time) and wait for ACKs between segments
count = 0
while not (endOfStream):
	# wait in between packets
	time.sleep(sleeptime)

	data = input.read(1000)
	# empty string so we have reached EOS
	if not(data):
	    endOfStream = True
	else:
		count = count + 1
		# send up to 1000 bytes at a time
		data = create_udp_packet(flag, data)
		sock.sendto(data,(localhost,trollport))
		data = sock.recv(8)
		if(check_ack(data)):
			continue
		print('Received invalid ACK from server.')
		# add functionality for timeout / retransmission in lab 4
print(f"Sent {count} file data packets to server and receieved {count} ACKs.")
input.close()
	
