import os
import json
from dotenv import load_dotenv
from cryptography.fernet import Fernet

load_dotenv()

crypt_key = os.getenv('CRYPT_KEY')


def encrypt_json_file(file_name: str) -> None:

    fernet = Fernet(crypt_key)

    with open(file_name, "rb") as file:
        json_data = file.read()

    encrypted_data = fernet.encrypt(json_data)

    with open(file_name, "wb") as file:
        file.write(encrypted_data)



def decrypt_json_file(file_name: str) -> None:

    fernet = Fernet(crypt_key)

    with open(file_name, "rb") as file:
        encrypted_data = file.read()

    decrypted_data = fernet.decrypt(encrypted_data)

    with open(file_name, "wb") as file:
        file.write(decrypted_data)