import socket
import threading
import signal
import sys
import logging
import time
import os
from codec_8.Decoder import FMB_Decoder
from SENDER.Sender import Sender
from MONGO_LOGGER.mongo_logger import Mongo_logger


LOCAL = socket.gethostbyname(socket.gethostname())
PUBLIC = "0.0.0.0"
PORT = 5050

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((PUBLIC, PORT))

logger = logging.getLogger("[SERVER]")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s :	%(asctime)s : %(name)s: %(message)s')
file_handler = logging.FileHandler('../logs/server.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


# CHANGE TO TRUE TO USE RABBITMQ ON HARPIA
SENDER = Sender(production = True)
SENDER.check_connection()


# MONGO CLASS
MONGO = Mongo_logger(cluster = True)
MONGO.connect()

# if connection with remote queue is established, is_connected_to_queue is set to True, else False


# if connected to queue
if SENDER.is_connected_to_queue and MONGO.is_connected_to_mongo:

    # client handler function. Passed to thread as target 
    def handle_client(client, addr):
        connected = True
        # each client is an instance of decoder class
        FMB_140 = FMB_Decoder(client, addr)
        # init loop
        while connected:
            # store received data
            data = client.recv(4096)
            data_size = sys.getsizeof(data)

            FMB_140.process_received_(data)
            # checking if device is sending IMEI
            if FMB_140.is_authenticating():
            
                IMEI = FMB_140.get_IMEI_str()
                # print(f"Device sending IMEI: {IMEI[2:]}")
                # logger.info(f"Connection from {addr}")
                MONGO.log(data_size=data_size, imei=IMEI[2:], operation="auth")

                # check for device IMEI id DB
                if FMB_140.is_device_registered(IMEI[2:]):
                    FMB_140.accept_connection(client = client)
                else:
                    FMB_140.refuse_connection(client = client)
                    connected = False
                
                continue


            # else if sending AVL data
            elif FMB_140.is_sending_AVL():
                # print('sending avl')
                # authenticated set to True if passed is_authenticating method
                if FMB_140.is_authenticated():
                
                    IMEI = bytearray(FMB_140.get_IMEI_RAW())
                    IMEI_STR = FMB_140.get_IMEI_str()

                    DATA_2_B_SENT = bytearray(IMEI + data)

                    # print(f"AVL size: {len(data)}")

                    SENDER.forward_to_queue(DATA_2_B_SENT, FMB_140.get_IMEI_str())

                    MONGO.log(data_size=data_size, imei=IMEI_STR[2:], operation="avl")


                    # return number of records to client
                    # print(f"[server] Sending data length")
                    client.send(FMB_140.get_number_of_records_two(True))
                
                else:
                    # print("*REJECTED. NO AUTH PASSED*")
                    FMB_140.refuse_connection(client = client)

                    connected = False
                    # logger.warning(f"Rejected connection from {addr}. No auth passed")

                    # client.close()
                continue
            # else disconnect
            else:
                # logger.info(f" Client {addr} disconnected")
                connected = False
                client.shutdown(1)
                client.close()
                continue


    def start(server):
        server.listen(5)

        while True:
            # block and  wait for new connection
            client, addr = server.accept()
            # print(f"[server accept] Client connected from {addr}")
            # on connection start new thread passing socket and addr as arguments to callable function
            thread = threading.Thread(target=handle_client, args=(client, addr))
            # logger.info(f" Client {addr} connected")
            # print(f"Client from {addr} connecting...")
            thread.daemon = True
            # start the thread
            thread.start()
            # thread terminates when the target function returns!!!
            
            

    if __name__ == "__main__":
        if SENDER.production():
            print(f"[LISTENER v2] [PRODUCTION MODE] Waiting for incomming connections on port: {LOCAL}:{PORT}")
        else:
            print(f"[LISTENER v2] [DEVELOPMENT MODE] Waiting for incomming connections on port: {LOCAL}:{PORT}")

        # logger.info(f"Server listening at port {PORT}")

        # !!!! create and start listening in new thread !!!!
        server_thread = threading.Thread(target=start, args=(server,))
        # logger.info(f'[STARTING MAIN THREAD ID] {threading.get_ident()} \n')
        server_thread.daemon =True
        server_thread.start()

    while True:
        # wait for ctrl+c to shutdown
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print('[LISTENER v2] Shutting down')
            # logger.info(f"Server shutting down \n")
            time.sleep(.5)
            break

else:
    print('[ERROR] No connection to exchange established')
