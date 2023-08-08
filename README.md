# CSE 3461 - Computer Networking
This repository houses four labs I made for Dr. Adam Champion's computer networking course.   
    
Lab 1: File Transfer    
This lab was focused on setting up the functionality for reading a file in small segments and then writing to a destination file one segment at a time.
It was good practice for later labs since we already had a program that could read data in packet-sized chunks even though this program did not transmit data over the internet.

Lab 2: File Transfer via TCP    
This lab expanded on the file transfer program. I created a client and server program where a file was sent in small segments via a TCP socket.
Because TCP is a connection-oriented service, this was the simplest file transfer lab since TCP provides many guarantees that UDP does not.

Lab 3: File Transfer via UDP    
This lab was essentially a more challenging version of Lab 2. I used UDP sockets instead of TCP sockets, and wrapped each segment with a header.
ACKs were implemented at this stage, but they weren't very useful yet because we didn't have to deal with packets being dropped.

Lab 4: File Transfer via UDP (with dropped packets in both directions)    
This lab expanded upon Lab 3, and we had to implement timeouts and retransmissions in both directions (server->client and client->server).
It was a pretty challenging lab, but I successfully implemented the alternating-bit protocol and made a pair of programs that worked as expected.
