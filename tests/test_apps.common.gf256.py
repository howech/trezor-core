from common import *

from apps.common.gf256 import Gf256


class TestGf256(unittest.TestCase):

    def test_gf256_zero_and_one(self):
        zero = Gf256(0)
        one = Gf256(1)

        self.assertEqual(zero, zero)
        self.assertEqual(one, one)
        self.assertEqual(zero, one.add(one))
        self.assertEqual(one, one.inverse())

        self.assertEqual(zero, zero.add(zero))
        self.assertEqual(one, zero.add(one))
        self.assertEqual(one, one.add(zero))

        self.assertEqual(zero, zero.multiply(zero))
        self.assertEqual(zero, zero.multiply(one))
        self.assertEqual(zero, one.multiply(zero))
        self.assertEqual(one, one.multiply(one))


    def test_gf256_add_inverse(self):
        zero = Gf256(0)
        one = Gf256(1)

        for i in range (1, 256):
            g = Gf256(i)
            self.assertEqual(zero, g.add(g))

    def test_gf256_mult_inverse(self):
        zero = Gf256(0)
        one = Gf256(1)

        for i in range (1, 256):
            g = Gf256(i)
            h = g.inverse()
            self.assertEqual(one, g.multiply(h))
            self.assertEqual(one, h.multiply(g))
            self.assertEqual(one.divide(g), h)
            self.assertEqual(one.divide(h), g)
            self.assertEqual(g, h.inverse())

if __name__ == '__main__':
    unittest.main()
