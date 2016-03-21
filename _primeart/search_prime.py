import primesieve
import math
from .noise_generator import generate_noise

def first_prime_factor(n):
    it = primesieve.Iterator()
    max = math.ceil(math.sqrt(n))
    i = it.next_prime()
    while i <= max:
        if n % i:
            i = it.next_prime()
        else:
            n //= i
            return i
    if n > 1: return n

def add_noise(target, font, limit=5):
    yield target
    w = len(target)
    for noise in generate_noise(w, limit):
        result = []
        for i in range(0, w):
            v = font.near_char(target[i], noise[i])
            if v is None:
                result = None
                break
            result.append(v)
        if result is not None: yield result
