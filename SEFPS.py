class SEFPS:
    def __init__(self):
        # todo Set Constant
        self.name = "SEFPS"

    def set_key(self, key_string):
        self.key_string = key_string
        # todo get AES key

    def read_file(self, filename):
        success = False
        # todo read file in bytes
        return success

    def add_padding(self):
        # todo add padding
        return False

    def compute_message_digest(self):
        message_digest = ""
        # todo compute message digest from plain text + padding
        return message_digest

    def compute_ciphertext(self):
        ciphertext = ""

        # todo sequential AES

        # todo parallel AES

        return ciphertext


if __name__ == "__main__":
    sefps = SEFPS()
    print('abc', sefps.name)
