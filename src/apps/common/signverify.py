from ubinascii import hexlify

from trezor.crypto.hashlib import blake256, sha256
from trezor.utils import HashWriter

from apps.wallet.sign_tx.signing import write_varint


def message_digest(coin, message):
    if coin.decred:
        h = HashWriter(blake256)
    else:
        h = HashWriter(sha256)
    write_varint(h, len(coin.signed_message_header))
    h.extend(coin.signed_message_header)
    write_varint(h, len(message))
    h.extend(message)
    ret = h.get_digest()
    if coin.sign_hash_double:
        ret = sha256(ret).digest()
    return ret


def split_message(message):
    try:
        m = bytes(message).decode()
        words = m.split(" ")
    except UnicodeError:
        m = "hex(%s)" % hexlify(message).decode()
        words = [m]
    return words
