from apps.common.gf256 import Gf256
from trezor.crypto import random

def lagrange_polynomial(x, xi, y):
    """
    Interpolate the ith lagrange polynomial for points x at y

    Lagrange polynomials are a nifty tool for doing polynomial
    interpolation. Given a set of x's, the ith Lagrange polynomial
    should have the value of 1 at y = x_i, and should be zero at all 
    of y = x_j (j != i).
    """    
    result = Gf256(1)
    for xj in x:
        if xj != xi:
            # result = result * (y - xj) / (xi - xj)
            # but * overloading is not working
            result = result.multiply((y.sub(xj)).divide(xi.sub(xj)))
    return result

class Dealer(object):
    # Note that in an ideal situation, the member variables should be stored in
    # persistant memory so that the "deal" can take place over several
    # 'sessions'.
    #    
    def __init__(self, entropy, threshold):
        self.__threshold = threshold
        self.__size = len(entropy)

        # We need threshold-1 more chunks of random bytes at least the same size as
        # entropy
        self.__coefs = [entropy] + [random.bytes(self.__size) for _ in range(1, threshold)]
        self.__next_share = 1

        # This does not have to be cryptographically random - just a way to keep
        [self.__family] = random.bytes(1)

    def sharesDealt(self):
        return self.__next_share -1

    def dealingDone(self):
        return self.__next_share > self.__threshold

    def dealShare(self):
        prefix = bytearray(4)
        prefix[0] = (self.__family) & 255
        prefix[1] = (self.__threshold) & 255
        prefix[2] = (self.__next_share) & 255
        prefix[3] = 0

        payload = bytearray(self.__size)
        x = Gf256(self.__next_share)

        # Compute powers of x
        # powers[j] = x ^ j
        powers = [Gf256(1)]*self.__threshold
        for j in range(1, self.__threshold):
            powers[j] = powers[j-1].multiply(x)

        for i in range(0, len(payload)):
            value = Gf256(0)
            for j in range(0, self.__threshold):
                value = value.add(powers[j].multiply(Gf256(self.__coefs[j][i])))
            payload[i] = value.byte()

        share_bytes = prefix + payload

        self.__next_share += 1
        return share_bytes

class Collector(object):
    # Like the dealer, the state of this object should get persisted to longer
    # term memory, so users can collect shares over several sessions. This
    # allows the unit to get powered down and back up again between inputting
    # shares.

    def __init__(self):
        self.__family_initialized = False
        self.__family = None
        self.__threshold = None
        self.__size = None
        self.__collected = {}

    def _setFamily(self, family, threshold, size):
        if self.__family_initialized:
            # Check to see that the family and threshold match
            if self.__family != family or self.__threshold != threshold or self.__size != size:
                raise Exception("family does not match")
        else:
            # The first share sets the family
            self.__family = family
            self.__threshold = threshold
            self.__size = size
            self.__collected = [None] * threshold
            self.__position = 0
            self.__family_initialized = True

    def collectShare(self, share_bytes):
        prefix = share_bytes[0:4]
        payload = share_bytes[4:]
        index = Gf256(prefix[2])

        self._setFamily(prefix[0], prefix[1], len(payload))

        for pair in self.__collected:
            if pair is not None and pair[0] == index:
                raise Exception("Duplicate share index")

        self.__collected[self.__position] = (index,payload)
        self.__position += 1

    def sharesRemaining(self):
        if self.__family_initialized:
            return self.__threshold - self.__position
        else:
            return 1

    def recoverSecret(self):
        if self.sharesRemaining() > 0:
            raise Exception("Not enough shares collected")

        x = [ pair[0] for pair in self.__collected]
        
        zero = Gf256(0)
        lagrange = [lagrange_polynomial(x, xj, zero) for xj in x]

        results = bytearray(self.__size)
        for i in range(0, self.__size):
            value = Gf256(0)
            for j in range(0, self.__threshold):
                xj = x[j]
                value = value.add(
                  lagrange[j].multiply(Gf256(self.__collected[j][1][i]))
                )
            results[i] = value.byte()

        return results
       