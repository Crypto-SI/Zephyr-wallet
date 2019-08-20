import shutil
import tempfile
import sys
import os
import json
from decimal import Decimal
import time

from io import StringIO
from zephyr_code.storage import WalletStorage
from zephyr_code.json_db import FINAL_SEED_VERSION
from zephyr_code.wallet import (Abstract_Wallet, Standard_Wallet,
                                  create_new_wallet,
                                  restore_wallet_from_text, Imported_Wallet)
from zephyr_code.exchange_rate import ExchangeBase, FxThread
from zephyr_code.util import TxMinedInfo
from zephyr_code.bitcoin import COIN
from zephyr_code.json_db import JsonDB

from zephyr_code.tests.cases import SequentialTestCase


class FakeSynchronizer(object):

    def __init__(self):
        self.store = []

    def add(self, address):
        self.store.append(address)


class WalletTestCase(SequentialTestCase):

    def setUp(self):
        super(WalletTestCase, self).setUp()
        self.user_dir = tempfile.mkdtemp()

        self.wallet_path = os.path.join(self.user_dir, "somewallet")

        self._saved_stdout = sys.stdout
        self._stdout_buffer = StringIO()
        sys.stdout = self._stdout_buffer

    def tearDown(self):
        super(WalletTestCase, self).tearDown()
        shutil.rmtree(self.user_dir)
        # Restore the "real" stdout
        sys.stdout = self._saved_stdout


class TestWalletStorage(WalletTestCase):

    def test_read_dictionary_from_file(self):

        some_dict = {"a":"b", "c":"d"}
        contents = json.dumps(some_dict)
        with open(self.wallet_path, "w") as f:
            contents = f.write(contents)

        storage = WalletStorage(self.wallet_path, manual_upgrades=True)
        self.assertEqual("b", storage.get("a"))
        self.assertEqual("d", storage.get("c"))

    def test_write_dictionary_to_file(self):

        storage = WalletStorage(self.wallet_path)

        some_dict = {
            u"a": u"b",
            u"c": u"d",
            u"seed_version": FINAL_SEED_VERSION}

        for key, value in some_dict.items():
            storage.put(key, value)
        storage.write()

        with open(self.wallet_path, "r") as f:
            contents = f.read()
        d = json.loads(contents)
        for key, value in some_dict.items():
            self.assertEqual(d[key], value)

class FakeExchange(ExchangeBase):
    def __init__(self, rate):
        super().__init__(lambda self: None, lambda self: None)
        self.quotes = {'TEST': rate}

class FakeFxThread:
    def __init__(self, exchange):
        self.exchange = exchange
        self.ccy = 'TEST'

    remove_thousands_separator = staticmethod(FxThread.remove_thousands_separator)
    timestamp_rate = FxThread.timestamp_rate
    ccy_amount_str = FxThread.ccy_amount_str
    history_rate = FxThread.history_rate

class FakeWallet:
    def __init__(self, fiat_value):
        super().__init__()
        self.fiat_value = fiat_value
        self.db = JsonDB("{}", manual_upgrades=True)
        self.db.transactions = self.db.verified_tx = {'abc':'Tx'}

    def get_tx_height(self, txid):
        # because we use a current timestamp, and history is empty,
        # FxThread.history_rate will use spot prices
        return TxMinedInfo(height=10, conf=10, timestamp=int(time.time()), header_hash='def')

    default_fiat_value = Abstract_Wallet.default_fiat_value
    price_at_timestamp = Abstract_Wallet.price_at_timestamp
    class storage:
        put = lambda self, x: None

txid = 'abc'
ccy = 'TEST'

class TestFiat(SequentialTestCase):
    def setUp(self):
        super().setUp()
        self.value_sat = COIN
        self.fiat_value = {}
        self.wallet = FakeWallet(fiat_value=self.fiat_value)
        self.fx = FakeFxThread(FakeExchange(Decimal('1000.001')))
        default_fiat = Abstract_Wallet.default_fiat_value(self.wallet, txid, self.fx, self.value_sat)
        self.assertEqual(Decimal('1000.001'), default_fiat)
        self.assertEqual('1,000.00', self.fx.ccy_amount_str(default_fiat, commas=True))

    def test_save_fiat_and_reset(self):
        self.assertEqual(False, Abstract_Wallet.set_fiat_value(self.wallet, txid, ccy, '1000.01', self.fx, self.value_sat))
        saved = self.fiat_value[ccy][txid]
        self.assertEqual('1,000.01', self.fx.ccy_amount_str(Decimal(saved), commas=True))
        self.assertEqual(True,       Abstract_Wallet.set_fiat_value(self.wallet, txid, ccy, '', self.fx, self.value_sat))
        self.assertNotIn(txid, self.fiat_value[ccy])
        # even though we are not setting it to the exact fiat value according to the exchange rate, precision is truncated away
        self.assertEqual(True, Abstract_Wallet.set_fiat_value(self.wallet, txid, ccy, '1,000.002', self.fx, self.value_sat))

    def test_too_high_precision_value_resets_with_no_saved_value(self):
        self.assertEqual(True, Abstract_Wallet.set_fiat_value(self.wallet, txid, ccy, '1,000.001', self.fx, self.value_sat))

    def test_empty_resets(self):
        self.assertEqual(True, Abstract_Wallet.set_fiat_value(self.wallet, txid, ccy, '', self.fx, self.value_sat))
        self.assertNotIn(ccy, self.fiat_value)

    def test_save_garbage(self):
        self.assertEqual(False, Abstract_Wallet.set_fiat_value(self.wallet, txid, ccy, 'garbage', self.fx, self.value_sat))
        self.assertNotIn(ccy, self.fiat_value)


class TestCreateRestoreWallet(WalletTestCase):

    def test_create_new_wallet(self):
        passphrase = 'mypassphrase'
        password = 'mypassword'
        encrypt_file = True
        d = create_new_wallet(path=self.wallet_path,
                              passphrase=passphrase,
                              password=password,
                              encrypt_file=encrypt_file)
        wallet = d['wallet']  # type: Standard_Wallet
        wallet.check_password(password)
        self.assertEqual(passphrase, wallet.keystore.get_passphrase(password))
        self.assertEqual(d['seed'], wallet.keystore.get_seed(password))
        self.assertEqual(encrypt_file, wallet.storage.is_encrypted())

    def test_restore_wallet_from_text_mnemonic(self):
        text = 'twenty oil method educate cloud reunion worry stay turtle nut volume fit'
        passphrase = ''
        password = 'mypassword'
        encrypt_file = True
        d = restore_wallet_from_text(text,
                                     path=self.wallet_path,
                                     network=None,
                                     passphrase=passphrase,
                                     password=password,
                                     encrypt_file=encrypt_file)
        wallet = d['wallet']  # type: Standard_Wallet
        self.assertEqual(passphrase, wallet.keystore.get_passphrase(password))
        self.assertEqual(text, wallet.keystore.get_seed(password))
        self.assertEqual(encrypt_file, wallet.storage.is_encrypted())
        self.assertEqual('DRWitZjTupNRGhGrztniNi9GDH3JmVT3kh', wallet.get_receiving_addresses()[0])

    def test_restore_wallet_from_text_xpub(self):
        text = 'TDt9EWvD5T5T44hAZuJZXMfHWGsmD66d1YWTp7CVhrX1zjHNuB3VYXnbaKZ2HUkx5KoCtby3iwJaVT7Tn3Cr4vQ9vy5LfFiiqS6cUJfY8HTHzr4'
        d = restore_wallet_from_text(text, path=self.wallet_path, network=None)
        wallet = d['wallet']  # type: Standard_Wallet
        self.assertEqual(text, wallet.keystore.get_master_public_key())
        self.assertEqual('DRWitZjTupNRGhGrztniNi9GDH3JmVT3kh', wallet.get_receiving_addresses()[0])

    def test_restore_wallet_from_text_xprv(self):
        text = 'ToEA6epvY6iUs9r4QP4tkWhqMS6w41PBs6vgjSGtjZGsea1M1W49FRcCWWEeLX5imWRTPcEa5navHfj3u1doNVnfwt3JG78rafcdQj6FqbcDXHn'
        d = restore_wallet_from_text(text, path=self.wallet_path, network=None)
        wallet = d['wallet']  # type: Standard_Wallet
        self.assertEqual(text, wallet.keystore.get_master_private_key(password=None))
        self.assertEqual('DRWitZjTupNRGhGrztniNi9GDH3JmVT3kh', wallet.get_receiving_addresses()[0])

    def test_restore_wallet_from_text_addresses(self):
        text = 'DRWitZjTupNRGhGrztniNi9GDH3JmVT3kh DTZ5ScjVGhSZ9wCFeYuNrnAFtbg2A7T4Rf'
        d = restore_wallet_from_text(text, path=self.wallet_path, network=None)
        wallet = d['wallet']  # type: Imported_Wallet
        self.assertEqual('DRWitZjTupNRGhGrztniNi9GDH3JmVT3kh', wallet.get_receiving_addresses()[0])
        self.assertEqual(2, len(wallet.get_receiving_addresses()))
        # also test addr deletion
        wallet.delete_address('DTZ5ScjVGhSZ9wCFeYuNrnAFtbg2A7T4Rf')
        self.assertEqual(1, len(wallet.get_receiving_addresses()))

    def test_restore_wallet_from_text_privkeys(self):
        text = 'p2pkh:YNimAB1DHy2UrRN2ce8yNVaBHRpU7gjnqY2ogcGjFMMrdWJja5Rb p2pkh:YQ7zo2kTHEKfKCm18MJnK1ALVBtLPVdq8z4oLMgotWBHMX1bR7V8'
        d = restore_wallet_from_text(text, path=self.wallet_path, network=None)
        wallet = d['wallet']  # type: Imported_Wallet
        addr0 = wallet.get_receiving_addresses()[0]
        self.assertEqual('D5C7eBMk4yPy7LnikE1EpVdjhfkEhAyNvH', addr0)
        self.assertEqual('p2pkh:YQ7zo2kTHEKfKCm18MJnK1ALVBtLPVdq8z4oLMgotWBHMX1bR7V8',
                         wallet.export_private_key(addr0, password=None)[0])
        self.assertEqual(2, len(wallet.get_receiving_addresses()))
        # also test addr deletion
        wallet.delete_address('DRWitZjTupNRGhGrztniNi9GDH3JmVT3kh')
        self.assertEqual(1, len(wallet.get_receiving_addresses()))
