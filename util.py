import os
import random
import string

class Utility:

    @staticmethod
    def get_random_string(size=6):
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choice(chars) for _ in range(size))

    @staticmethod
    def get_file_extension(file_name, basename=True):
        if basename:
            file_name = os.path.basename(file_name)
        return os.path.splitext(file_name)[1][1:]

    @staticmethod
    def get_file_with_extension(file_name, basename=True):
        if basename:
            file_name = os.path.basename(file_name)
        return file_name