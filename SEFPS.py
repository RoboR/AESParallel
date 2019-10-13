import os.path
import hashlib

import numpy
from multiprocessing import Process, Queue

from AESWrapper import AESWrapper

class SEFPS:

    def __init__(self, thread_count, key_bytes):
        self.name = "SEFPS"
        self.BLOCK_SIZE = 16

        self.thread_count = thread_count
        self.key_bytes = key_bytes
        self.key_len = len(key_bytes)

    def __add_padding__(self, file_bytes_array):
        assert isinstance(file_bytes_array, numpy.ndarray)

        file_len = len(file_bytes_array)
        require_pad_bytes = 32 - file_len % self.BLOCK_SIZE
        first_half_pad_size = self.BLOCK_SIZE
        second_half_pad_size = require_pad_bytes - self.BLOCK_SIZE
        first_half_val = 0      # First half of the padding are padded with zeroes
        second_half_val = second_half_pad_size

        # print("File Len : ", file_len,
        #       "Require padding : ", require_pad_bytes, "first half : ", first_half_pad_size,
        #       " second half: ", second_half_pad_size, " first val : ", first_half_val,
        #       " second val : ", second_half_val)
        padding_list = numpy.zeros((first_half_pad_size + second_half_pad_size,), dtype=int)
        padding_list[first_half_pad_size:] = (second_half_val,)

        # file_padded = file_binary + bytes(padding_list)
        padded_array = numpy.append(file_bytes_array, padding_list)

        return padded_array

    def __get_message_digest__(self, byte):
        assert isinstance(byte, numpy.ndarray)

        hash = hashlib.sha3_256(byte)
        np_hash = numpy.frombuffer(hash.digest(), numpy.uint8)

        return np_hash

    def __add_message_digest__(self, padded_file):
        assert isinstance(padded_file, numpy.ndarray)

        hash_bytes = self.__get_message_digest__(padded_file)
        message_digest = numpy.append(padded_file, hash_bytes)

        return message_digest

    def count_array_sum(self, array):
        sum = 0
        for a in array:
            sum = sum + a

    def __get_encrypt_cipher__(self, plain, res):
        aes = AESWrapper(self.key_bytes)
        cipher = aes.encrypt(plain)
        res.put(cipher)

    def __get_decrypt_cipher__(self, cipher, res):
        aes = AESWrapper(self.key_bytes)
        plain = aes.decrypt(cipher)
        res.put(plain)

    def __compute_ciphertext__(self, plain_text_bytes):
        assert isinstance(plain_text_bytes, numpy.ndarray)

        parallel_block = self.__assign_block_for_parallel__(plain_text_bytes, self.thread_count)
        procs = []
        result = Queue()

        for block in parallel_block:
            proc = Process(target=self.__get_encrypt_cipher__, args=(block, result,))
            procs.append(proc)
            proc.start()

            for proc in procs:
                proc.join()

        res = [result.get() for p in procs]
        append_res = numpy.zeros(0, dtype=int)

        for r in res:
            append_res = numpy.append(append_res, r)

        return append_res

    def __compute_plain_text__(self, cipher_text_bytes):
        assert isinstance(cipher_text_bytes, numpy.ndarray)

        # Assign parallel block
        parallel_block = self.__assign_block_for_parallel__(cipher_text_bytes, self.thread_count)

        # Parallel computation
        procs = []
        result = Queue()

        for block in parallel_block:
            proc = Process(target=self.__get_decrypt_cipher__, args=(block, result,))
            procs.append(proc)
            proc.start()

            for proc in procs:
                proc.join()

        res = [result.get() for p in procs]
        append_res = numpy.zeros(0, dtype=int)

        for r in res:
            append_res = numpy.append(append_res, r)

        return append_res

    def __assign_block_for_parallel__(self, text_block, thread_num):
        assert isinstance(text_block, numpy.ndarray)

        plain_len = len(text_block)
        rmd = int((plain_len / self.BLOCK_SIZE) % thread_num)    # reminder block
        mean_pt_len = int(plain_len / self.BLOCK_SIZE / thread_num) * self.BLOCK_SIZE
        start_idx = 0
        end_idx = mean_pt_len
        parallel_block = [[] for i in range(thread_num)]

        for t in range(0, thread_num):
            if t < rmd:
                end_idx = end_idx + self.BLOCK_SIZE
            parallel_block[t] = text_block[start_idx:end_idx]
            start_idx = end_idx
            end_idx = start_idx + mean_pt_len

        return numpy.array(parallel_block)

    def encrypt(self, plain_text_array):
        assert isinstance(plain_text_array, numpy.ndarray)

        # Add padding
        text_padded = self.__add_padding__(plain_text_array)

        # Add Message digest
        text_pad_digest = self.__add_message_digest__(text_padded)

        # Do encryption
        cipher_text = self.__compute_ciphertext__(text_pad_digest)

        return cipher_text

    def decrypt(self, cipher_text_array):
        assert isinstance(cipher_text_array, numpy.ndarray)

        # Do decryption
        decrypt_text = self.__compute_plain_text__(cipher_text_array)

        # Check message digest
        message_digest = decrypt_text[-32:]
        plain_text_and_pad = decrypt_text[:-32]

        msg_digest_calc = self.__get_message_digest__(plain_text_and_pad)
        integrity_check = False
        plain_text = None

        if numpy.array_equal(msg_digest_calc, message_digest):
            integrity_check = True

            # Remove message digest and padding
            extra_pad = plain_text_and_pad[-1]
            padding_len = extra_pad + self.BLOCK_SIZE
            plain_text = plain_text_and_pad[:-padding_len]

        return integrity_check, plain_text


if __name__ == "__main__":
    THREADS_USED = 4
    KEY_BYTES_SIZE = 24

    key_bytes = numpy.random.choice(256, KEY_BYTES_SIZE).astype(numpy.uint8)

    sefps = SEFPS(THREADS_USED, key_bytes)
    file_bytes = numpy.random.choice(256, 22).astype(numpy.uint8)
    cipher = sefps.encrypt(file_bytes)
    check, plain = sefps.decrypt(cipher)
