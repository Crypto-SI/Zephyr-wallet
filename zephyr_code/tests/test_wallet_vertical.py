from unittest import mock
import shutil
import tempfile
from typing import Sequence

from zephyr_code import storage, bitcoin, keystore
from zephyr_code.transaction import Transaction
from zephyr_code.simple_config import SimpleConfig
from zephyr_code.address_synchronizer import TX_HEIGHT_UNCONFIRMED, TX_HEIGHT_UNCONF_PARENT
from zephyr_code.wallet import sweep, Multisig_Wallet, Standard_Wallet, Imported_Wallet
from zephyr_code.util import bfh, bh2u
from zephyr_code.transaction import TxOutput
from zephyr_code.mnemonic import seed_type

from zephyr_code.tests.cases import TestCaseForTestnet
from zephyr_code.tests.cases import SequentialTestCase
from .test_bitcoin import needs_test_with_all_ecc_implementations


UNICODE_HORROR_HEX = 'e282bf20f09f988020f09f98882020202020e3818620e38191e3819fe381be20e3828fe3828b2077cda2cda2cd9d68cda16fcda2cda120ccb8cda26bccb5cd9f6eccb4cd98c7ab77ccb8cc9b73cd9820cc80cc8177cd98cda2e1b8a9ccb561d289cca1cda27420cca7cc9568cc816fccb572cd8fccb5726f7273cca120ccb6cda1cda06cc4afccb665cd9fcd9f20ccb6cd9d696ecda220cd8f74cc9568ccb7cca1cd9f6520cd9fcd9f64cc9b61cd9c72cc95cda16bcca2cca820cda168ccb465cd8f61ccb7cca2cca17274cc81cd8f20ccb4ccb7cda0c3b2ccb5ccb666ccb82075cca7cd986ec3adcc9bcd9c63cda2cd8f6fccb7cd8f64ccb8cda265cca1cd9d3fcd9e'
UNICODE_HORROR = bfh(UNICODE_HORROR_HEX).decode('utf-8')
assert UNICODE_HORROR == '₿ 😀 😈     う けたま わる w͢͢͝h͡o͢͡ ̸͢k̵͟n̴͘ǫw̸̛s͘ ̀́w͘͢ḩ̵a҉̡͢t ̧̕h́o̵r͏̵rors̡ ̶͡͠lį̶e͟͟ ̶͝in͢ ͏t̕h̷̡͟e ͟͟d̛a͜r̕͡k̢̨ ͡h̴e͏a̷̢̡rt́͏ ̴̷͠ò̵̶f̸ u̧͘ní̛͜c͢͏o̷͏d̸͢e̡͝?͞'


class WalletIntegrityHelper:

    gap_limit = 1  # make tests run faster

    @classmethod
    def check_seeded_keystore_sanity(cls, test_obj, ks):
        test_obj.assertTrue(ks.is_deterministic())
        test_obj.assertFalse(ks.is_watching_only())
        test_obj.assertFalse(ks.can_import())
        test_obj.assertTrue(ks.has_seed())

    @classmethod
    def check_xpub_keystore_sanity(cls, test_obj, ks):
        test_obj.assertTrue(ks.is_deterministic())
        test_obj.assertTrue(ks.is_watching_only())
        test_obj.assertFalse(ks.can_import())
        test_obj.assertFalse(ks.has_seed())

    @classmethod
    def create_standard_wallet(cls, ks, gap_limit=None):
        store = storage.WalletStorage('if_this_exists_mocking_failed_648151893')
        store.put('keystore', ks.dump())
        store.put('gap_limit', gap_limit or cls.gap_limit)
        w = Standard_Wallet(store)
        w.synchronize()
        return w

    @classmethod
    def create_imported_wallet(cls, privkeys=False):
        store = storage.WalletStorage('if_this_exists_mocking_failed_648151893')
        if privkeys:
            k = keystore.Imported_KeyStore({})
            store.put('keystore', k.dump())
        w = Imported_Wallet(store)
        return w

    @classmethod
    def create_multisig_wallet(cls, keystores: Sequence, multisig_type: str, gap_limit=None):
        """Creates a multisig wallet."""
        store = storage.WalletStorage('if_this_exists_mocking_failed_648151893')
        for i, ks in enumerate(keystores):
            cosigner_index = i + 1
            store.put('x%d/' % cosigner_index, ks.dump())
        store.put('wallet_type', multisig_type)
        store.put('gap_limit', gap_limit or cls.gap_limit)
        w = Multisig_Wallet(store)
        w.synchronize()
        return w


class TestWalletKeystoreAddressIntegrityForMainnet(SequentialTestCase):

    @needs_test_with_all_ecc_implementations
    @mock.patch.object(storage.WalletStorage, '_write')
    def test_electrum_seed_standard(self, mock_write):
        seed_words = 'twenty oil method educate cloud reunion worry stay turtle nut volume fit'
        self.assertEqual(seed_type(seed_words), 'standard')

        ks = keystore.from_seed(seed_words, '', False)

        WalletIntegrityHelper.check_seeded_keystore_sanity(self, ks)
        self.assertTrue(isinstance(ks, keystore.BIP32_KeyStore))

        self.assertEqual(ks.xprv, 'ToEA6epvY6iUs9r4QP4tkWhqMS6w41PBs6vgjSGtjZGsea1M1W49FRcCWWEeLX5imWRTPcEa5navHfj3u1doNVnfwt3JG78rafcdQj6FqbcDXHn')
        self.assertEqual(ks.xpub, 'TDt9EWvD5T5T44hAZuJZXMfHWGsmD66d1YWTp7CVhrX1zjHNuB3VYXnbaKZ2HUkx5KoCtby3iwJaVT7Tn3Cr4vQ9vy5LfFiiqS6cUJfY8HTHzr4')

        w = WalletIntegrityHelper.create_standard_wallet(ks)
        self.assertEqual(w.txin_type, 'p2pkh')

        self.assertEqual(w.get_receiving_addresses()[0], 'DRWitZjTupNRGhGrztniNi9GDH3JmVT3kh')
        self.assertEqual(w.get_change_addresses()[0], 'DMpYyHtEtMyH8eKB88rQCdmMyGZPKYXCdH')

    @needs_test_with_all_ecc_implementations
    @mock.patch.object(storage.WalletStorage, '_write')
    def test_bip39_seed_bip44_standard(self, mock_write):
        seed_words = 'tray machine cook badge night page project uncover ritual toward person enact'
        self.assertEqual(keystore.bip39_is_checksum_valid(seed_words), (True, True))

        ks = keystore.from_bip39_seed(seed_words, '', "m/44'/119'/0'")

        self.assertTrue(isinstance(ks, keystore.BIP32_KeyStore))

        self.assertEqual(ks.xprv, 'ToEA6m3VBmwn5r9SsZAz2Zysn17amzbedZC8cxHpxQHgtSZgi4w6xukSVGLCJd9CVxd4yfDt4gynFAj59cx8HYx7AbmwTiECho64a4xnE5ABoGf')
        self.assertEqual(ks.xpub, 'TDt9Ed8mj8JkGkzZ35QeoQwKvqtQw5K5mzmuhdDRvhXqEbqibjvTG1vqZ5eaFd3PTh3SHTnBs4rQc1mtUAziVFjY3ZtSUf6oGap4k3HEjqYuDHo')

        w = WalletIntegrityHelper.create_standard_wallet(ks)
        self.assertEqual(w.txin_type, 'p2pkh')

        self.assertEqual(w.get_receiving_addresses()[0], 'DSDT7LpsJTRsWP1zRtyNz2PrSi8sgashza')
        self.assertEqual(w.get_change_addresses()[0], 'D5q1yTM9aHEHgiCs7rWCJuKTnvEkPzhPTV')

    @needs_test_with_all_ecc_implementations
    @mock.patch.object(storage.WalletStorage, '_write')
    def test_electrum_multisig_seed_standard(self, mock_write):
        seed_words = 'blast uniform dragon fiscal ensure vast young utility dinosaur abandon rookie sure'
        self.assertEqual(seed_type(seed_words), 'standard')

        ks1 = keystore.from_seed(seed_words, '', True)
        WalletIntegrityHelper.check_seeded_keystore_sanity(self, ks1)
        self.assertTrue(isinstance(ks1, keystore.BIP32_KeyStore))
        self.assertEqual(ks1.xprv, 'ToEA6epvY6iUs9r4RZUe2Ng5EvEVMEztmfxnJHNDie3uhb373XD7gD7c5HGcf8u7nfhZ9VchoNFnSchop9id1i7CqRYW6QgYKcjaQHZ7zUYaZ2s')
        self.assertEqual(ks1.xpub, 'TDt9EWvD5T5T44hAb5iJoDdXPm1KWKiKv7YZNxHpgwJ43kK8wCCTyKJ196azcAEgV5wSYUjYKiLmYC1Sp7hSnTpTfZRoUXuoEen1tLNKEogUZK3')

        # electrum seed: ghost into match ivory badge robot record tackle radar elbow traffic loud
        ks2 = keystore.from_xpub('TDt9EWvD5T5T44hAb5iJoDdXPm1KWKiKv7YZNxHpgwJ43kK8wCCTyKJ196azcAEgV5wSYUjYKiLmYC1Sp7hSnTpTfZRoUXuoEen1tLNKEogUZK3')
        WalletIntegrityHelper.check_xpub_keystore_sanity(self, ks2)
        self.assertTrue(isinstance(ks2, keystore.BIP32_KeyStore))

        w = WalletIntegrityHelper.create_multisig_wallet([ks1, ks2], '2of2')
        self.assertEqual(w.txin_type, 'p2sh')

        self.assertEqual(w.get_receiving_addresses()[0], '6XnTFwisLJuM4Zbjn1APhnfNWnVe4RRaY8')
        self.assertEqual(w.get_change_addresses()[0], '6Q55sPL24e6JXvexMzWT9RWNAN5fua46E9')

    @needs_test_with_all_ecc_implementations
    @mock.patch.object(storage.WalletStorage, '_write')
    def test_bip39_multisig_seed_bip45_standard(self, mock_write):
        seed_words = 'treat dwarf wealth gasp brass outside high rent blood crowd make initial'
        self.assertEqual(keystore.bip39_is_checksum_valid(seed_words), (True, True))

        ks1 = keystore.from_bip39_seed(seed_words, '', "m/45'/0")
        self.assertTrue(isinstance(ks1, keystore.BIP32_KeyStore))
        self.assertEqual(ks1.xprv, 'ToEA6in9EDqryvMFHjxvhQLV6QsvD2HLJAb1Jo9BMLDV8GBu6gbhp73hGKvdModwk9zbA8jnPrzLAiHV6zLPnugNZ48rqRdCThWfWZWUrp2C63d')
        self.assertEqual(ks1.xpub, 'TDt9EasRmaCqAqCMTGCbUFHwFFekN6zmScAnPU4nKdTdURTvzMb47DE6L9F1JnYtinYoJWdojQmusvAKDr7wXxWFQyYhJy9tPXKJVmWQfGSz1HK')

        # bip39 seed: tray machine cook badge night page project uncover ritual toward person enact
        # der: m/45'/0
        ks2 = keystore.from_xpub('TDt9EbvwtXeurEcUS1XkJxCUarsEwSmLwrspaY1XL7jFMrPWypteJLwDrbGMezTCDVLwkHGck9EiqizSuV1dAkN3MXQ2stTaWvCLwQFqusp7vcV')
        WalletIntegrityHelper.check_xpub_keystore_sanity(self, ks2)
        self.assertTrue(isinstance(ks2, keystore.BIP32_KeyStore))

        w = WalletIntegrityHelper.create_multisig_wallet([ks1, ks2], '2of2')
        self.assertEqual(w.txin_type, 'p2sh')

        self.assertEqual(w.get_receiving_addresses()[0], '6X6HGuB2ZwfXim8ftiJmpHH863B2TmQ6YY')
        self.assertEqual(w.get_change_addresses()[0], '6Tyo6nLz9fV3MugLHJprA29myUhFgBa3Y3')

    @needs_test_with_all_ecc_implementations
    @mock.patch.object(storage.WalletStorage, '_write')
    def test_bip32_extended_version_bytes(self, mock_write):
        seed_words = 'crouch dumb relax small truck age shine pink invite spatial object tenant'
        self.assertEqual(keystore.bip39_is_checksum_valid(seed_words), (True, True))
        bip32_seed = keystore.bip39_to_seed(seed_words, '')
        self.assertEqual('0df68c16e522eea9c1d8e090cfb2139c3b3a2abed78cbcb3e20be2c29185d3b8df4e8ce4e52a1206a688aeb88bfee249585b41a7444673d1f16c0d45755fa8b9',
                         bh2u(bip32_seed))

        def create_keystore_from_bip32seed(xtype):
            ks = keystore.BIP32_KeyStore({})
            ks.add_xprv_from_seed(bip32_seed, xtype=xtype, derivation='m/')
            return ks

        ks = create_keystore_from_bip32seed(xtype='standard')
        self.assertEqual('033a05ec7ae9a9833b0696eb285a762f17379fa208b3dc28df1c501cf84fe415d0', ks.derive_pubkey(0, 0))
        self.assertEqual('02bf27f41683d84183e4e930e66d64fc8af5508b4b5bf3c473c505e4dbddaeed80', ks.derive_pubkey(1, 0))

        ks = create_keystore_from_bip32seed(xtype='standard')  # p2pkh
        w = WalletIntegrityHelper.create_standard_wallet(ks)
        self.assertEqual(ks.xprv, 'ToEA6epvY6iUs9r4RUJDav8XBUypExAC3FDBySoXNGfVArdhUSCMbXv1u9ZAwnEWvJSxmBwQj2f35fWd5iHQbPGBXvEFrM6chgqrWniyMEJHdSa')
        self.assertEqual(ks.xpub, 'TDt9EWvD5T5T44hAazXtMm5yLKkeQ2sdBgny47j8LZudX1ujN7Bhte6QxxsYtnLu6VNwZGhCmvXrS44tonCqriGe6Nws2f5xuyRkoB1hUGQqxnY')
        self.assertEqual(w.get_receiving_addresses()[0], 'DDobmkXB96CXnnHuGxqfMg8achhMEpH5XG')
        self.assertEqual(w.get_change_addresses()[0], 'DJNcetWgKFgv5ypvNBLedr6csmoyvs4BU1')

        ks = create_keystore_from_bip32seed(xtype='standard')  # p2sh
        w = WalletIntegrityHelper.create_multisig_wallet([ks], '1of1')
        self.assertEqual(ks.xprv, 'ToEA6epvY6iUs9r4RUJDav8XBUypExAC3FDBySoXNGfVArdhUSCMbXv1u9ZAwnEWvJSxmBwQj2f35fWd5iHQbPGBXvEFrM6chgqrWniyMEJHdSa')
        self.assertEqual(ks.xpub, 'TDt9EWvD5T5T44hAazXtMm5yLKkeQ2sdBgny47j8LZudX1ujN7Bhte6QxxsYtnLu6VNwZGhCmvXrS44tonCqriGe6Nws2f5xuyRkoB1hUGQqxnY')
        self.assertEqual(w.get_receiving_addresses()[0], '6TmcdztDU2pnVy3Xtq3Zv8Zqig6FVhntzJ')
        self.assertEqual(w.get_change_addresses()[0], '6aqZoBf5eSCHmqtnNRf1Wa4LQBfKAEx1hG')


class TestWalletKeystoreAddressIntegrityForTestnet(TestCaseForTestnet):

    @needs_test_with_all_ecc_implementations
    @mock.patch.object(storage.WalletStorage, '_write')
    def test_bip32_extended_version_bytes(self, mock_write):
        seed_words = 'crouch dumb relax small truck age shine pink invite spatial object tenant'
        self.assertEqual(keystore.bip39_is_checksum_valid(seed_words), (True, True))
        bip32_seed = keystore.bip39_to_seed(seed_words, '')
        self.assertEqual('0df68c16e522eea9c1d8e090cfb2139c3b3a2abed78cbcb3e20be2c29185d3b8df4e8ce4e52a1206a688aeb88bfee249585b41a7444673d1f16c0d45755fa8b9',
                         bh2u(bip32_seed))

        def create_keystore_from_bip32seed(xtype):
            ks = keystore.BIP32_KeyStore({})
            ks.add_xprv_from_seed(bip32_seed, xtype=xtype, derivation='m/')
            return ks

        ks = create_keystore_from_bip32seed(xtype='standard')
        self.assertEqual('033a05ec7ae9a9833b0696eb285a762f17379fa208b3dc28df1c501cf84fe415d0', ks.derive_pubkey(0, 0))
        self.assertEqual('02bf27f41683d84183e4e930e66d64fc8af5508b4b5bf3c473c505e4dbddaeed80', ks.derive_pubkey(1, 0))

        ks = create_keystore_from_bip32seed(xtype='standard')  # p2pkh
        w = WalletIntegrityHelper.create_standard_wallet(ks)
        self.assertEqual(ks.xprv, 'DRKVrRjogj3bNiLD8UciJeYkYQ6F7HGu3Bvn6m2Vf86GRBFWhREMB1FoVCbDTJa5ybZXzrnJGXam5Ei2fEgRKVqGnoYUhn7zxRoUndpXken1Qu4Q')
        self.assertEqual(ks.xpub, 'DRKPuUWy7gEYo13wzP4s1isdk5SZdyZcG4q3qzq9Ah5Up8MLXRzBTR4F46m9BwRosv7NejD8icmj3A2Q5qkKfntuRmbHZhnoDhHt5EcheqW878CP')
        self.assertEqual(w.get_receiving_addresses()[0], 'y5eM6b1aXki2w2VLwh9QDLoLDgnAn4SeiM')
        self.assertEqual(w.get_change_addresses()[0], 'yADMyj15hvCREE2N2uePVWmNUktoSeD8eD')

        ks = create_keystore_from_bip32seed(xtype='standard')  # p2sh
        w = WalletIntegrityHelper.create_multisig_wallet([ks], '1of1')
        self.assertEqual(ks.xprv, 'DRKVrRjogj3bNiLD8UciJeYkYQ6F7HGu3Bvn6m2Vf86GRBFWhREMB1FoVCbDTJa5ybZXzrnJGXam5Ei2fEgRKVqGnoYUhn7zxRoUndpXken1Qu4Q')
        self.assertEqual(ks.xpub, 'DRKPuUWy7gEYo13wzP4s1isdk5SZdyZcG4q3qzq9Ah5Up8MLXRzBTR4F46m9BwRosv7NejD8icmj3A2Q5qkKfntuRmbHZhnoDhHt5EcheqW878CP')
        self.assertEqual(w.get_receiving_addresses()[0], '8soEYefwj7c3QZt43M3UptCZVhduigoYNs')
        self.assertEqual(w.get_change_addresses()[0], '8zsBhqSouWyYgSjJWwevRKh4BDCySjizKi')
