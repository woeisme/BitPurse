#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2012 Benoit HERVIER <khertan@khertan.net>
# Licenced under GPLv3

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published
## by the Free Software Foundation; version 3 only.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License

import hashlib
import ecdsa
import re
import urllib2
import json
import urllib

class EC_KEY(object):
    def __init__( self, secret ):
        self.pubkey = ecdsa.ecdsa.Public_key( generator_secp256k1, generator_secp256k1 * secret )
        self.privkey = ecdsa.ecdsa.Private_key( self.pubkey, secret )
        self.secret = secret

        
def unpadding(data):
    return data[0:-ord(data[-1])]


def padding(data):
    return data + (16 - len(data) % 16) * chr(16 - len(data) % 16)


def hash_160(public_key):
    try:
        md = hashlib.new('ripemd160')
        md.update(hashlib.sha256(public_key).digest())
        return md.digest()
    except:
        import ripemd
        md = ripemd.new(hashlib.sha256(public_key).digest())
        return md.digest()


addrtype = 0

Hash = lambda x: hashlib.sha256(hashlib.sha256(x).digest()).digest()
hash_encode = lambda x: x[::-1].encode('hex')
hash_decode = lambda x: x.decode('hex')[::-1]


def public_key_to_bc_address(public_key):
    h160 = hash_160(public_key)
    return hash_160_to_bc_address(h160)


def hash_160_to_bc_address(h160):
    vh160 = chr(addrtype) + h160
    h = Hash(vh160)
    addr = vh160 + h[0:4]
    return b58encode(addr)


def bc_address_to_hash_160(addr):
    bytes = b58decode(addr, 25)
    return bytes[1:21]


def prettyPBitcoin(value, useColor=False):
    s = '%010d' % abs(value)
    sign = '' if value >= 0 else '-'
    if useColor:
        return sign + s[-10:-8] + '.' + s[-8:-6] + s[-6:]
    else:
        return '<b>' + sign + s[-10:-8] + '.' + s[-8:-6] + '</b>' + s[-6:]

def regenerate_key(pk):
    pko=ecdsa.SigningKey.from_secret_exponent(pk,SECP256k1)
    pubkey=binascii.hexlify(pko.get_verifying_key().to_string())
    pubkey2=hashlib.sha256(binascii.unhexlify('04'+pubkey)).hexdigest()
    pubkey3=hashlib.new('ripemd160',binascii.unhexlify(pubkey2)).hexdigest()
    pubkey4=hashlib.sha256(binascii.unhexlify('00'+pubkey3)).hexdigest()
    pubkey5=hashlib.sha256(binascii.unhexlify(pubkey4)).hexdigest()
    pubkey6=pubkey3+pubkey5[:8]
    pubnum=int(pubkey6,16)
    pubnumlist=[]
    while pubnum!=0: pubnumlist.append(pubnum%58); pubnum/=58
    address=''
    for l in ['123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'[x] for x in pubnumlist]:
        address=l+address
    return '1'+addres

__b58chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
__b58base = len(__b58chars)


def b58encode(v):
    """ encode v, which is a string of bytes, to base58."""

    long_value = 0L
    for (i, c) in enumerate(v[::-1]):
        long_value += (256 ** i) * ord(c)

    result = ''
    while long_value >= __b58base:
        div, mod = divmod(long_value, __b58base)
        result = __b58chars[mod] + result
        long_value = div
    result = __b58chars[long_value] + result

    # Bitcoin does a little leading-zero-compression:
    # leading 0-bytes in the input become leading-1s
    nPad = 0
    for c in v:
        if c == '\0':
            nPad += 1
        else:
            break

    return (__b58chars[0] * nPad) + result


def b58decode(v, length):
    """ decode v into a string of len bytes."""
    long_value = 0L
    for (i, c) in enumerate(v[::-1]):
        long_value += __b58chars.find(c) * (__b58base ** i)

    result = ''
    while long_value >= 256:
        div, mod = divmod(long_value, 256)
        result = chr(mod) + result
        long_value = div
    print long_value
    result = chr(long_value) + result

    nPad = 0
    for c in v:
        if c == __b58chars[0]:
            nPad += 1
        else:
            break

    result = chr(0) * nPad + result
    if length is not None and len(result) != length:
        return None

    return result


def EncodeBase58Check(vchIn):
    hash = Hash(vchIn)
    return b58encode(vchIn + hash[0:4])


def DecodeBase58Check(psz):
    vchRet = b58decode(psz, None)
    key = vchRet[0:-4]
    csum = vchRet[-4:]
    hash = Hash(key)
    cs32 = hash[0:4]
    if cs32 != csum:
        return None
    else:
        return key


def PrivKeyToSecret(privkey):
    return privkey[9:9 + 32]


def SecretToASecret(secret):
    vchIn = chr(addrtype + 128) + secret
    return EncodeBase58Check(vchIn)


def ASecretToSecret(key):
    vch = DecodeBase58Check(key)
    if vch and vch[0] == chr(addrtype + 128):
        return vch[1:]
    else:
        return False


# secp256k1, http://www.oid-info.com/get/1.3.132.0.10
_p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2FL
_r = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141L
_b = 0x0000000000000000000000000000000000000000000000000000000000000007L
_a = 0x0000000000000000000000000000000000000000000000000000000000000000L
_Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798L
_Gy = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8L
curve_secp256k1 = ecdsa.ellipticcurve.CurveFp(_p, _a, _b)
generator_secp256k1 = ecdsa.ellipticcurve.Point(curve_secp256k1, _Gx, _Gy, _r)
oid_secp256k1 = (1, 3, 132, 0, 10)
SECP256k1 = ecdsa.curves.Curve("SECP256k1",
                               curve_secp256k1,
                               generator_secp256k1,
                               oid_secp256k1)


def filter(s):
    out = re.sub('( [^\n]*|)\n', '', s)
    out = out.replace(' ', '')
    out = out.replace('\n', '')
    return out


def rev_hex(s):
    return s.decode('hex')[::-1].encode('hex')


def int_to_hex(i, length=1):
    s = hex(i)[2:].rstrip('L')
    s = "0" * (2 * length - len(s)) + s
    return rev_hex(s)


def var_int(i):
    if i < 0xfd:
        return int_to_hex(i)
    elif i <= 0xffff:
        return "fd" + int_to_hex(i, 2)
    elif i <= 0xffffffff:
        return "fe" + int_to_hex(i, 4)
    else:
        return "ff" + int_to_hex(i, 8)


def is_valid(addr):
    ADDRESS_RE = re.compile('[1-9A-HJ-NP-Za-km-z]{26,}\\Z')
    if not ADDRESS_RE.match(addr):
        return False
    try:
        h = bc_address_to_hash_160(addr)
    except:
        return False
    return addr == hash_160_to_bc_address(h)


def getDataFromChainblock(request, params=None):
    if params:
        body = urllib.urlencode(params)
    else:
        body = None
    req = urllib2.Request(request,
                          body,
                          {'user-agent': 'BitPurse',
                           'Content-Type':
                           'application/x-www-form-urlencoded',
                           'Accept': 'application/json'})
    opener = urllib2.build_opener()
    fh = opener.open(req)
    result = fh.read()
    return json.loads(result)    