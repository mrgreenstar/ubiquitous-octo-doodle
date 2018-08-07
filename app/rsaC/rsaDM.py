'''
    Модуль для шифровки сообщений методом RSA.
'''
import math
import random
import gmpy2

def prime_number(lowerBound, upperBound):
    '''
        Модуль для генерации "большого" простого числа в пределах.
    '''

    random_number = random.randint(lowerBound, upperBound)
    random_prime_number = gmpy2.next_prime(random_number)
    return random_prime_number


def generate_keys():
    '''
        Модуль для генерации ключей.
        Возвращает 2 словаря.
    '''

    lowerBound = 2**1024
    upperBound = 2**2048
    Flag = 1
    d = 1

    # Выбираем p.
    p = prime_number(lowerBound, upperBound)
    while not gmpy2.is_prime(p):
        p = prime_number(lowerBound, upperBound)

    # Выбираем q.
    q = prime_number(lowerBound, upperBound)
    while not gmpy2.is_prime(q):
        q = prime_number(lowerBound, upperBound)

    while p == q:
        q = prime_number(lowerBound, upperBound)

    n = p * q

    # Создаем открытую e экспоненту
    eiler = (p - 1) * (q - 1)
    e = prime_number(2**512, 2**1000)
    while e > eiler:
        e = prime_number()

    while Flag:
        e = e + 1
        if gmpy2.gcd(eiler, e) == 1:
            Flag = 0

    # Считаем d
    Flag = 1
    while Flag:
        d = gmpy2.invert(e, eiler)
        if d:
            Flag = 0
    public_key = {'publ_exp': int(e), 'modulus' : n}
    private_key = {'priv_exp': int(d), 'modulus' : n, 'p': p, 'q': q}
    return private_key, public_key

def encrypt_message(message, public_key):
    '''
        Функция для шифрования сообщения.

        Возвращает зашифрованное сообщение.
    '''

    E = public_key['publ_exp']
    # Составляем список из номеров букв и шифруем
    encrypted_lst = []
    for i in range(0, len(message)):
        char = ord(message[i])
        encrypted_lst.append(gmpy2.powmod(char, E, int(public_key['modulus'])))

    encrypted_message = ''
    for i in range(0, len(encrypted_lst)):
        encrypted_message += str(encrypted_lst[i]) + '?'

    return encrypted_message

def decrypt_message(encrypted_message, private_key):
    '''
        Функция для расшифровки сообщений.

        Возвращается расшифрованное сообщение.
    '''

    decrypted_message = ''
    encrypted_message = encrypted_message.split('?')
    print('Зашифрованное:',encrypted_message)
    for i in range(0, len(encrypted_message)):
        if encrypted_message[i] != '':
            char = int(encrypted_message[i])
            m = gmpy2.powmod(char, int(private_key['priv_exp']), int(private_key['modulus']))
            m=chr(m)
            decrypted_message = decrypted_message + str(m)

    decrypted_message.encode('utf-8')
    return decrypted_message

def generate_public(privKey):

    eiler = (int(privKey['p']) - 1) * (int(privKey['q']) - 1)
    Flag = 1
    d = int(privKey['priv_exp'])
    while Flag:
        e = gmpy2.invert(d, eiler)
        if e:
            Flag = 0

    public_key = dict(publ_exp = int(e), modulus = privKey['modulus'])
    return public_key

def base_decode(base_key):
    '''
        Функция для преобразования ключа, полученного из базы.
    '''

    key_parts = base_key.key.split('|')
    private_key = dict(priv_exp=key_parts[0], modulus=key_parts[1],
        p=key_parts[2], q=key_parts[3])

    return private_key

def create_signature(message, private_key):
    '''
            Функция для создания электронной подписи.

            Принимает зашифрованное сообщение и приватный ключ.
            Возвращает подпись.
    '''
    message = message.split('?')[:-1]
    print(message)
    signature = []
    for i in message:
        signature.append(gmpy2.powmod(int(i),
            int(private_key['priv_exp']), int(private_key['modulus'])))

    return signature

def check_signature(message, signature, public_key):
    '''
        Функция для проверки электронной подписи.

        Принимает исходное зашифрованное сообщение,
        электронную подпись и публичный ключ.
    '''
    checked_message = []
    message = message.split('?')[:-1]
    for i in signature:
        checked_message.append(str(gmpy2.powmod(int(i),
             int(public_key['publ_exp']), int(public_key['modulus']))))
    print('Сообщение:{}\nПосле проверки:{}\n'.format(message, checked_message))
    return checked_message == message

def salt(message):
    '''
        Функция для добавления лишних бит к символу.

        Возвращает сообщение с измененными битами и "затемнитель".
    '''
    bin_message = []
    dimmer = random.randint(100,2000)                            # "Затемнитель"
    for i in message:
        bin_message.append(ord(i))

    message = []
    for i in bin_message:
        bit = list(bin(i)[2:])                                  # Получаем двоичное представление одного символа
        bits_32 = [0 for x in range(0, 32 - len(bit))]
        bits_32.extend(bit)                                     # Вспомогательный массив, представляющий число в 2СС 32 бита
        bit_str = "".join(str(x) for x in bits_32)              # Представляем в виде строки 2СС 32 бита
        darker_char = int(bit_str, 2) & dimmer
        darker_char = bin(darker_char)[2:]
        message.append(darker_char)

    return darker_char, dimmer
