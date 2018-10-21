
__initialized = False
__pow = [0]*256
__log = [0]*256

def __initialize():
    global __initialized
    global __pow
    global __log

    if not __initialized:
        i = 0
        m = 1
        while i<256:
            __pow[i] = m
            __log[m] = i
            i += 1
            m ^= (m<<1) ^ (0 if (m & 0x80 == 0) else 0x11b)
        __initialized = True


class Gf256(object):
    def __init__(self, byte):
        if not __initialized:
            __initialize()
        self.__byte = byte

    def __add__(self, a):
        return Gf256(self.__byte ^ a.__byte)
    add = __add__
    __sub__ = __add__
    sub = __add__

    # For some unfathomalble reason, overloading * does not appear to be working.
    def __mul__(self, a):
        if self.__byte == 0 or a.__byte == 0:
            return Gf256(0)
        l = (__log[self.__byte] + __log[a.__byte]) % 255
        return Gf256(__pow[l])
    multiply = __mul__


    def __truediv__(self, a):
        if self.__byte == 0:
            return Gf256(0)
        if a.__byte == 0:
            return 1/a.__byte
        l = (255 + __log[self.__byte] - __log[a.__byte]) % 255
        return Gf256(__pow[l])
    divide = __truediv__

    def __eq__(self,a):
        return self.__byte == a.__byte

    def inverse(self):
        if self.__byte == 0:
            return 1/self.__byte
        l = (255 - __log[self.__byte]) % 255
        return Gf256(__pow[l])

    def byte(self):
        return self.__byte
