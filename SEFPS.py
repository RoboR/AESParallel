import os.path
import hashlib
import datetime

from Crypto.Cipher import AES

class SEFPS:
    def __init__(self):
        # todo Set Constant
        self.name = "SEFPS"
        # self.file_name = None
        # self.file_binary = None
        # self.file_len = 0

    def __set_key__(self, key_string):
        key_bytes = bytearray(key_string, 'utf-8')
        hash_key = hashlib.sha3_256(key_bytes)

        return hash_key.digest()

    def __read_file__(self, filename):
        success = False
        file_binary = None
        file_len = 0

        if os.path.isfile(filename):
            with open(filename, "rb") as binary_file:
                data = binary_file.read()
                file_binary = data
                file_len = len(data)
                success = True

        return success, file_binary, file_len

    def __add_padding__(self, file_binary, file_len):
        require_pad_bytes = 32 - file_len % 16
        first_half_pad_size = 16
        second_half_pad_size = require_pad_bytes - 16
        first_half_val = 0      # First half of the padding are padded with zeroes
        second_half_val = second_half_pad_size

        print("Require padding : ", require_pad_bytes, "first half : ", first_half_pad_size,
              " second half: ", second_half_pad_size, " first val : ", first_half_val,
              " second val : ", second_half_val)
        padding_list = []

        for i in range(first_half_pad_size):
            padding_list.append(first_half_val)
        for i in range(second_half_pad_size):
            padding_list.append(second_half_val)

        file_padded = file_binary + bytes(padding_list)

        return file_padded

    def __compute_message_digest__(self, padded_file):
        hash = hashlib.sha3_256(padded_file)
        message_digest = padded_file + hash.digest()

        return message_digest

    def compute_ciphertext(self, filename):
        ciphertext = ""

        success, binary_file, file_len = self.__read_file__(filename)

        if success:
            padded_file = self.__add_padding__(binary_file, file_len)
            hash_file = self.__compute_message_digest__(padded_file)
        else:
            print("Warning ", filename, " does not exits")

        # Sequential AES
        PASSWORD = "password123"
        aes_key = self.__set_key__(PASSWORD)
        aes_ecb = AES.new(aes_key, AES.MODE_ECB)
        # print(hash_file)
        encrypt_file = aes_ecb.encrypt(hash_file)
        # print(encrypt_file)
        decrypt_file = aes_ecb.decrypt(encrypt_file)
        print(decrypt_file)

        # todo parallel AES

        return ciphertext


if __name__ == "__main__":
    start_time = datetime.datetime.now()
    sefps = SEFPS()
    sefps.compute_ciphertext("input/test.bin")
    # sefps.compute_ciphertext("input/SAMPLE.mp4")
    end_time = datetime.datetime.now()
    delta_time = end_time - start_time
    delta_microseconds = delta_time.total_seconds() * 1000
    print(int(delta_microseconds), "ms")
