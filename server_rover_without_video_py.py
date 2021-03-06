import socket
import argparse
import sys
import struct
import base64
import cv2
import datetime
import time
import numpy as np
import pickle
from tkinter import *
import threading
import concurrent.futures
from multiprocessing import Process, Lock
# from video import Webcam

parser = argparse.ArgumentParser(description = "This is the server for the multithreaded socket demo!")
parser.add_argument('--host', metavar = 'host', type = str, nargs = '?', default = 'localhost')
parser.add_argument('--port', metavar = 'port', type = int, nargs = '?', default = 9999)
args = parser.parse_args()

print(f"Running the server on: {args.host} and port: {args.port}")

sck_msg = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sck_vid = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sck_vid2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s_cmd1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cap = cv2.VideoCapture(0)#Altered for higher frame rate
cap1 = cv2.VideoCapture(1)

try:
    sck_msg.bind((args.host, args.port))
    sck_msg.listen(5)
    sck_vid.bind((args.host, 1234))
    sck_vid.listen(5)
    sck_vid2.bind((args.host, 8080))
    sck_vid2.listen(5)
    s_cmd1.bind((args.host, 1235))
    s_cmd1.listen(5)
except Exception as e:
    raise SystemExit(f"We could not bind the server on host: {args.host} to port: {args.port}, because: {e}")


def on_new_client(client, connection):#recieve message
    ip = connection[0]
    port = connection[1]
    print(f"THe new connection was made from IP: {ip}, and port: {port}!")
    while True:
        msg = client.recv(1024)
        if msg.decode() == 'exit':
            break
        print(f"The client said: {msg.decode()}")
        reply = f"You told me: {msg.decode()}"
        client.sendall(reply.encode('utf-8'))
    print(f"The client from ip: {ip}, and port: {port}, has gracefully diconnected!")
    client.close()
    
def video_stream(client, connection):#send from front camera
    ip = connection[0]
    port = connection[1]
    print(f"THe new connection was made from IP: {ip}, and port: {port}!")
    # rett = cap.begin()
    while True:
        ret, frame = cap.read()
        if (ret):
            encoded, buffer = cv2.imencode('.jpg', frame)
            b_frame = base64.b64encode(buffer)
            b_size = len(b_frame)
            #sending data
            client.sendall(struct.pack("<L", b_size) + b_frame)
    print(f"The client from ip: {ip}, and port: {port}, has gracefully diconnected!")
    client.close()

def video_stream2(client, connection):#send from second camera
    ip = connection[0]
    port = connection[1]
    print(f"THe new connection was made from IP: {ip}, and port: {port}!")
    # rett = cap1.begin()
    while True:
        ret, frame = cap1.read()
        if (ret):
            encoded, buffer = cv2.imencode('.jpg', frame)
            b_frame = base64.b64encode(buffer)
            b_size = len(b_frame)
            #sending data
            client.sendall(struct.pack("<L", b_size) + b_frame)
    print(f"The client from ip: {ip}, and port: {port}, has gracefully diconnected!")
    client.close()

def recv_cmd(client, connection):#recieve controller inputs

    while 1:
        msg = client.recv(1024)
        if msg.decode() == "":
            break
        else:
            print("recieved command " + str(msg.decode("utf-8")))

try:
    client, ip = sck_msg.accept()
    client2, ip2 = sck_vid.accept()
    client3, ip3 = sck_vid2.accept()
    conn_cmd1, addr_cmd1 = s_cmd1.accept()
    t1 = threading.Thread(target = on_new_client,args=(client, ip), daemon = True)
    t2 = threading.Thread(target = video_stream,args=(client2, ip2), daemon = True)
    t3 = threading.Thread(target = video_stream2,args=(client3, ip3), daemon = True)
    t4 = threading.Thread(target = recv_cmd,args=(conn_cmd1, addr_cmd1), daemon = True)
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    while True:
        time.sleep(100)
        
except KeyboardInterrupt:
    print(f"shutting down the server!")
except Exception as e:
    print(f"error: {e}")
# cap.stopped()
# cap1.stopped()
sck_msg.close()
sck_vid.close()
sck_vid2.close()
s_cmd1.close()
