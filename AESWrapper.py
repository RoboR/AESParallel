from aes_en_decrypt_functions import 	key_expansion, \
                                        aes_encrypt, \
                                        aes_decrypt

import numpy

class AESWrapper:

    def __init__(self, key_bytes):
        self.BLOCK_IN_BYTES = 16
        self.key_size = len(key_bytes)

        assert isinstance(key_bytes, numpy.ndarray)
        assert self.key_size == 16 or self.key_size == 24 or self.key_size == 32

        self.hash_key = key_expansion(key_bytes)

    def encrypt(self, plaintext_bytes):
        total_size = len(plaintext_bytes)
        ciphertext = numpy.zeros((total_size,), dtype=int)

        for start_idx in range(0, total_size, self.BLOCK_IN_BYTES):
            end_idx = start_idx + self.BLOCK_IN_BYTES
            current_block = plaintext_bytes[start_idx:end_idx]
            np_bytearray = numpy.array(current_block)

            ciphertext[start_idx:end_idx] = aes_encrypt(np_bytearray, self.hash_key)

        return ciphertext

    def decrypt(self, ciphertext_bytes):
        total_size = len(ciphertext_bytes)
        plaintext = numpy.zeros((total_size,), dtype=int)

        for start_idx in range(0, total_size, self.BLOCK_IN_BYTES):
            end_idx = start_idx + self.BLOCK_IN_BYTES
            current_block = ciphertext_bytes[start_idx:end_idx]

            plaintext[start_idx:end_idx] = aes_decrypt(current_block, self.hash_key)

        return plaintext


if __name__ == '__main__':
    key = numpy.random.choice(256, 32).astype(numpy.uint8)

    wrapper = AESWrapper(key)

    text = "ABCDEFGHIJKLMNOPQRSTUVWXYZ012345"
    cipher = wrapper.encrypt(bytearray.fromhex(text.encode().hex()))
    plain = wrapper.decrypt(cipher)
    print(plain)
