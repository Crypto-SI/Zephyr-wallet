# -*- coding: utf-8 -*-
#
# Electrum - lightweight Bitcoin client
# Copyright (C) 2018 The Electrum developers
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import json

from .util import inv_dict


def read_json(filename, default):
    path = os.path.join(os.path.dirname(__file__), filename)
    try:
        with open(path, 'r') as f:
            r = json.loads(f.read())
    except:
        r = default
    return r


class AbstractNet:

    @classmethod
    def max_checkpoint(cls) -> int:
        return max(0, len(cls.CHECKPOINTS) * 2016 - 1)


class BitcoinMainnet(AbstractNet):

    TESTNET = False
    REGTEST = False
    WIF_PREFIX = 212
    ADDRTYPE_P2PKH = 30
    ADDRTYPE_P2SH = 13
    GENESIS = "0000041e482b9b9691d98eefb48473405c0b8ec31b76df3797c74a78680ef818"
    DEFAULT_PORTS = {'t': '50001', 's': '50002'}
    DEFAULT_SERVERS = read_json('servers.json', {})
    CHECKPOINTS = read_json('checkpoints.json', [])

    XPRV_HEADERS = {
        'standard':    0x022D2533,  # xprv
    }
    XPRV_HEADERS_INV = inv_dict(XPRV_HEADERS)
    XPUB_HEADERS = {
        'standard':    0x0221312B,  # xpub
    }
    XPUB_HEADERS_INV = inv_dict(XPUB_HEADERS)
    BIP44_COIN_TYPE = 119

    POS_BLOCK = 259201
    ZC_VERSION = 4


class BitcoinTestnet(AbstractNet):

    TESTNET = True
    REGTEST = False
    WIF_PREFIX = 239
    ADDRTYPE_P2PKH = 139
    ADDRTYPE_P2SH = 19
    GENESIS = "0000041e482b9b9691d98eefb48473405c0b8ec31b76df3797c74a78680ef818"
    DEFAULT_PORTS = {'t': '51001', 's': '51002'}
    DEFAULT_SERVERS = read_json('servers_testnet.json', {})
    CHECKPOINTS = read_json('checkpoints_testnet.json', [])

    XPRV_HEADERS = {
        'standard':    0x3a8061a0,  # tprv
    }
    XPRV_HEADERS_INV = inv_dict(XPRV_HEADERS)
    XPUB_HEADERS = {
        'standard':    0x3a805837,  # tpub
    }
    XPUB_HEADERS_INV = inv_dict(XPUB_HEADERS)
    BIP44_COIN_TYPE = 1

    POS_BLOCK = 201
    ZC_VERSION = 4


class BitcoinRegtest(BitcoinTestnet):

    REGTEST = True

    GENESIS = "0000041e482b9b9691d98eefb48473405c0b8ec31b76df3797c74a78680ef818"
    DEFAULT_SERVERS = read_json('servers_regtest.json', {})
    CHECKPOINTS = []

    POS_BLOCK = 251
    ZC_VERSION = 4


# don't import net directly, import the module instead (so that net is singleton)
net = BitcoinMainnet


def set_mainnet():
    global net
    net = BitcoinMainnet


def set_testnet():
    global net
    net = BitcoinTestnet


def set_regtest():
    global net
    net = BitcoinRegtest
