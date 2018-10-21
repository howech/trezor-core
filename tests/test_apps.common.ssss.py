from common import *
from apps.common.gf256 import Gf256
from apps.common.ssss import Dealer, Collector, lagrange_polynomial

class TestSSSS(unittest.TestCase):

    def test_lagrange_polynomial(self):
        zero = Gf256(0)
        one = Gf256(1)
        x = [ Gf256(21), Gf256(37), Gf256(95)]

        for i in range(0,3):
            for j in range(0,3):
                l = lagrange_polynomial(x, x[i], x[j])
                if i==j:
                    self.assertEqual(one, l)
                else:
                    self.assertEqual(zero,l)

    def test_happy_path(self):
        entropy = bytearray(10)
        dealer = Dealer(entropy, 3)
        share1 = dealer.dealShare()
        share2 = dealer.dealShare()
        share3 = dealer.dealShare()
        share4 = dealer.dealShare()
        share5 = dealer.dealShare()
        share6 = dealer.dealShare()
        
        self.assertTrue(dealer.dealingDone())

        collector = Collector()
        collector.collectShare(share1)
        collector.collectShare(share4)
        collector.collectShare(share6)

        recovered = collector.recoverSecret()
        self.assertEqual(entropy, recovered)

        collector = Collector()
        collector.collectShare(share2)
        collector.collectShare(share5)
        collector.collectShare(share3)

        recovered = collector.recoverSecret()
        self.assertEqual(entropy, recovered)


if __name__ == '__main__':
    unittest.main()
