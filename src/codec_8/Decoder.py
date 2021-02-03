import sys
import logging
import requests

logger = logging.getLogger("decoder.py")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s :	%(asctime)s : %(name)s: %(message)s')
file_handler = logging.FileHandler('../logs/fmb_connections.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

class FMB_Decoder:
    def __init__(self, client, addr):
        self.CLIENT = client
        self.ADDR = addr
        self.received_data = ''
        self.IMEI_lenght = None
        self.IMEI = None
        self.authenticated = False
        self.sendingAVL = False

    def process_received_(self, data):
        self.received_data = data

    def is_authenticating(self):
        # when module connects to server, module sends its IMEI. 
        # First comes short identifying number of bytes written and then goes IMEI as text (bytes). 
        # First two bytes denote IMEI length!!!

        length_of_received_data = len(bytearray(self.received_data))
        first_two_bytes = self.received_data[:2]
        first_two_bytes_int = int.from_bytes(first_two_bytes, byteorder=sys.byteorder)

        # first_two_bytes = int(first_two_bytes, 16)
        # print(f"LENGTH OF BYTES: {length_of_received_data}")
        # print(first_two_bytes_int)

        # print(f"HEXA LENGTH: {len(self.received_data)}")
        # print(f"PRINTING RECEIVED DATA IN is_auth METHOD: {self.received_data}")
        if length_of_received_data < 20 and first_two_bytes_int > 0:
            # print(f"[decoder] Client connected from {self.ADDR}. Authenticating")
            self.IMEI_lenght = first_two_bytes_int
            self.IMEI = self.received_data

            return True
        else:
            return False

    def is_authenticated(self):
        return self.authenticated

    def get_IMEI_length(self):
        return self.IMEI_lenght

    def get_IMEI_RAW(self):
        return bytearray(self.IMEI)

    def get_IMEI_str(self):
        return self.IMEI.decode('utf-8')
    
    # def IMEI(self):
    #     return len(self.IMEI)

    def is_sending_AVL(self):
        msg = self.received_data
        length_of_received_data = len(bytearray(msg))
        first_four_bytes = msg[:4]
        first_four_bytes_int = int.from_bytes(first_four_bytes, byteorder=sys.byteorder)
        
        if length_of_received_data > 5 and first_four_bytes_int < 1:
            # print(first_four_bytes_int)
            self.sendingAVL = True
            return True
        else:
            return False
    
    def get_AVL_Data_Array_Length(self):
        if self.is_sending_AVL():
            avl = self.received_data
            length = avl[4:8]
            return int.from_bytes(length, byteorder=sys.byteorder)

    def get_codec_id(self):
        if self.is_sending_AVL():
            avl = self.received_data
            codec_id = avl[8:9]
            return int.from_bytes(codec_id, byteorder=sys.byteorder)

    def get_number_of_records_one(self):
        if self.is_sending_AVL():
            avl = self.received_data
            number_of_records = avl[9:10]
            return int.from_bytes(number_of_records, byteorder=sys.byteorder)

    def get_number_of_records_two(self, raw):
        if self.sendingAVL:
            avl = self.received_data
            number_of_records = avl[-5:-4]
            if raw:
                # number of records in AVL preceded by three ZERO bytes
                # After server receives packet and parses it, server must report to module number of data received as integer (four bytes).
                ba = bytearray(b'\x00\x00\x00' + number_of_records)
                return ba
            else:
                return int.from_bytes(number_of_records, byteorder=sys.byteorder)

    def accept_connection(self, client):
        # this part is mooved from is_authenticating method
        self.authenticated = True


        response = bytearray()
        response.append(0x01)
        # print(f"[decoder] Accepting connection from {self.ADDR}")
        client.send(response)

    def refuse_connection(self, client):
        response = bytearray()
        response.append(0x00)
        client.send(response)
        self.CLIENT.close()

    def is_device_registered(self, imei):
        req = requests.post('', data={"imei" : imei})
        
        status = req.status_code

        # if status == 200:
        #     resp = req.json()
        #     # print(resp)
        #     if resp > 0:
        #         return True
        #     else:
        #         return False
        # else:
        #     print("[ DECODER is_device_registered error ]: API response != 200")
        #     return False

        if status == 200:
            return True
        else:
            return False

    
    



        
        