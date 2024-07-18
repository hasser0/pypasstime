import sys
from random import randint

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import rsa


def generate_time_lock_puzzle(message, n_seconds):
    priv_key = rsa.generate_private_key(public_exponent=65537, key_size=512)
    p = priv_key.private_numbers().p
    q = priv_key.private_numbers().q
    n = p * q
    phi_n = (p - 1) * (q - 1)
    key = Fernet.generate_key()
    k = int.from_bytes(key, sys.byteorder)
    cypher = Fernet(key)
    cm = cypher.encrypt(bytes(message, "utf-8"))
    # TODO automatically calculate for any machine
    cycles_per_second_on_machine = 750_000
    t = n_seconds * cycles_per_second_on_machine
    a = randint(2, n - 1)
    e = pow(2, t, phi_n)
    ck = k + pow(a, e, n)
    return n, a, t, ck, cm


def solve_time_lock_puzzle(n, a, t, ck, cm):
    b = a % n
    for _ in range(t):
        b = b**2 % n
    key = int.to_bytes(ck - b, length=44, byteorder=sys.byteorder)
    decypher = Fernet(key)
    return decypher.decrypt(cm).decode("utf-8")


# TODO create and read from zip file and using click
