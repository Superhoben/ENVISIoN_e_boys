#  Created by Jesper Ericsson
# 
#  To the extent possible under law, the person who associated CC0
#  with the alterations to this file has waived all copyright and related
#  or neighboring rights to the alterations made to this file.
# 
#  You should have received a copy of the CC0 legalcode along with
#  this work.  If not, see
#  <http://creativecommons.org/publicdomain/zero/1.0/>.

import sys, os, inspect
import time
import select
import json
path_to_current_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(path_to_current_folder + "/../ENVISIoN")
from ENVISIoN import ENVISIoN


import threading
import queue

# TODO: select method for checking if input is empty will not work on windows.

def send_packet(tag, data):
# Package data into JSON-string-packet and send it via printing.
    packet = json.dumps({"type": tag, "data": data})
    print(packet)
    sys.stdout.flush()

def decode_packet(packet):
# Return python dictionary based on JSON-string-packet
    obj = json.loads(packet)
    return obj



def input_loop(input_queue):
    while True:
        input_queue.put(sys.stdin.readline())

def main():
    input_queue = queue.Queue()

    input_thread = threading.Thread(target=input_loop, args=(input_queue,))
    input_thread.daemon = True
    input_thread.start()

    time_start = time.time()
    while True:
        while not input_queue.empty():
            # send_packet("Debug", "Packet recieved")
            request = decode_packet(input_queue.get())
            # send_packet("echo", request)
            if request["type"] == "envision request":
                response = envision.handle_request(request["data"])
                send_packet("response", response)
        
        envision.update()

        # Try to loop at 60 fps
        time_elapsed = time.time() - time_start
        time.sleep(max([1.0/60 - time_elapsed, 0]))

# Initialize ENVISIoN
envision = ENVISIoN()

main()
# while True:
#     time_start = time.time()
#     # While stdin is not empty read lines
#     while select.select([sys.stdin,],[],[],0.0)[0]:
#         #JSON request packages are send from JavaScript via stdin
#         
#         request = decode_packet(sys.stdin.readline())
#         
#         if request["type"] == "envision request":
#             response = envision.handle_request(request["data"])
#             send_packet("response", response)
#     # else:
#     #     send_data("Debug", "No input recieved")
#     #     print("No input recieved")
    
#     envision.update()

#     # Try to loop at 60 fps
#     time_elapsed = time.time() - time_start
#     time.sleep(max([1.0/60 - time_elapsed, 0]))
    