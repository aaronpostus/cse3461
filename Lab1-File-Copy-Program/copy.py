import sys
import os.path

#AUTHOR: Aaron Post

if len(sys.argv) != 2:
    print("please provide exactly one argument with the file name")
    sys.exit(1)

# correct number of arguments, run program
print('file name is', sys.argv[1])

# read from file in binary mode
try:
    input = open(sys.argv[1],"rb")
except OSError:
    print('File does not exist. Cannot read.')
    sys.exit(1)

path = "recv/"

# if folder 'recv' doesnt exist, create it
if not(os.path.exists(path)):
	os.mkdir(path)

# open output file (and create it if it doesn't exist)
output = open(path + sys.argv[1], "ab")
endOfStream = False

# reads up to 1000 bytes at a time and will return 0 if at EOS
while not (endOfStream):
    data = input.read(1000)
    # empty string so we have reached EOS
    if not(data):
        endOfStream = True
    else:
		#append up to 1000 bytes at a time
        output.write(data)

# close IO streams
input.close()
output.close()
