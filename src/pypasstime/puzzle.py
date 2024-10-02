import pickle
import sys
from random import randint

import click
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
    return {"n": n, "a": a, "t": t, "ck": ck, "cm": cm}


def solve_time_lock_puzzle(puzzle):
    n = puzzle["n"]
    a = puzzle["a"]
    t = puzzle["t"]
    ck = puzzle["ck"]
    cm = puzzle["cm"]
    b = a % n
    for _ in range(t):
        b = b**2 % n
    key = int.to_bytes(ck - b, length=44, byteorder=sys.byteorder)
    decypher = Fernet(key)
    return decypher.decrypt(cm).decode("utf-8")


@click.command()
@click.argument("filename", type=click.File("rb"))
def solve_puzzle(filename):
    puzzle = pickle.load(filename)
    solution = solve_time_lock_puzzle(puzzle)
    with open("solved_puzzle.txt", "w") as f:
        f.write(solution)


@click.command()
@click.option("-t", "--text", type=str)
@click.option("-s", "seconds", type=int)
def create_puzzle(text, seconds):
    puzzle = generate_time_lock_puzzle(text, seconds)
    with open("puzzle.pkl", "wb") as pkl:
        pickle.dump(puzzle, pkl)
