import unittest
from unittest import mock
from decimal import Decimal

from zephyr_code.commands import Commands, eval_bool
from zephyr_code import storage
from zephyr_code.wallet import restore_wallet_from_text

from zephyr_code.tests.cases import TestCaseForTestnet


class TestCommands(unittest.TestCase):

    def test_setconfig_non_auth_number(self):
        self.assertEqual(7777, Commands._setconfig_normalize_value('rpcport', "7777"))
        self.assertEqual(7777, Commands._setconfig_normalize_value('rpcport', '7777'))
        self.assertAlmostEqual(Decimal(2.3), Commands._setconfig_normalize_value('somekey', '2.3'))

    def test_setconfig_non_auth_number_as_string(self):
        self.assertEqual("7777", Commands._setconfig_normalize_value('somekey', "'7777'"))

    def test_setconfig_non_auth_boolean(self):
        self.assertEqual(True, Commands._setconfig_normalize_value('show_console_tab', "true"))
        self.assertEqual(True, Commands._setconfig_normalize_value('show_console_tab', "True"))

    def test_setconfig_non_auth_list(self):
        self.assertEqual(['file:///var/www/', 'https://electrum.org'],
            Commands._setconfig_normalize_value('url_rewrite', "['file:///var/www/','https://electrum.org']"))
        self.assertEqual(['file:///var/www/', 'https://electrum.org'],
            Commands._setconfig_normalize_value('url_rewrite', '["file:///var/www/","https://electrum.org"]'))

    def test_setconfig_auth(self):
        self.assertEqual("7777", Commands._setconfig_normalize_value('rpcuser', "7777"))
        self.assertEqual("7777", Commands._setconfig_normalize_value('rpcuser', '7777'))
        self.assertEqual("7777", Commands._setconfig_normalize_value('rpcpassword', '7777'))
        self.assertEqual("2asd", Commands._setconfig_normalize_value('rpcpassword', '2asd'))
        self.assertEqual("['file:///var/www/','https://electrum.org']",
            Commands._setconfig_normalize_value('rpcpassword', "['file:///var/www/','https://electrum.org']"))

    def test_eval_bool(self):
        self.assertFalse(eval_bool("False"))
        self.assertFalse(eval_bool("false"))
        self.assertFalse(eval_bool("0"))
        self.assertTrue(eval_bool("True"))
        self.assertTrue(eval_bool("true"))
        self.assertTrue(eval_bool("1"))

    def test_convert_xkey(self):
        cmds = Commands(config=None, wallet=None, network=None)
        xpubs = {
            ("TDt9EWvD5T5T44hAZuJZXMfHWGsmD66d1YWTp7CVhrX1zjHNuB3VYXnbaKZ2HUkx5KoCtby3iwJaVT7Tn3Cr4vQ9vy5LfFiiqS6cUJfY8HTHzr4", "standard"),
        }
        for xkey1, xtype1 in xpubs:
            for xkey2, xtype2 in xpubs:
                self.assertEqual(xkey2, cmds.convert_xkey(xkey1, xtype2))

        xprvs = {
            ("ToEA6epvY6iUs9r4QP4tkWhqMS6w41PBs6vgjSGtjZGsea1M1W49FRcCWWEeLX5imWRTPcEa5navHfj3u1doNVnfwt3JG78rafcdQj6FqbcDXHn", "standard"),
        }
        for xkey1, xtype1 in xprvs:
            for xkey2, xtype2 in xprvs:
                self.assertEqual(xkey2, cmds.convert_xkey(xkey1, xtype2))

    @mock.patch.object(storage.WalletStorage, '_write')
    def test_encrypt_decrypt(self, mock_write):
        wallet = restore_wallet_from_text('p2pkh:YNimAB1DHy2UrRN2ce8yNVaBHRpU7gjnqY2ogcGjFMMrdWJja5Rb',
                                          path='if_this_exists_mocking_failed_648151893')['wallet']
        cmds = Commands(config=None, wallet=wallet, network=None)
        cleartext = "asdasd this is the message"
        pubkey = "038c9a10827e85c481fd53e662d08c07c16775961e7366c54d8227344a6d3c0e3f"
        ciphertext = cmds.encrypt(pubkey, cleartext)
        self.assertEqual(cleartext, cmds.decrypt(pubkey, ciphertext))


class TestCommandsTestnet(TestCaseForTestnet):

    def test_convert_xkey(self):
        cmds = Commands(config=None, wallet=None, network=None)
        xpubs = {
            ("DRKPuUWy7gEYo13wzMyc2rfgJav8Q42pddrbpaP1uYXhZWL8uzneJwZnZvjKm2e8bsxLpsGN9Wy8bgpKKAvGRLWfTyy4zWLurknPcX1nyHPZj6kh", "standard"),
        }
        for xkey1, xtype1 in xpubs:
            for xkey2, xtype2 in xpubs:
                self.assertEqual(xkey2, cmds.convert_xkey(xkey1, xtype2))

        xprvs = {
            ("DRKVrRjogj3bNiLD8VMdNtZdvw6ynDYPA5WBLQHEGfFwKaowH2zn8YAKvkAiT1Kv2iHYPuFiVzANchztHPqTEnQrsyXxpBuAUZbC8SmqTVyXuchj", "standard"),
        }
        for xkey1, xtype1 in xprvs:
            for xkey2, xtype2 in xprvs:
                self.assertEqual(xkey2, cmds.convert_xkey(xkey1, xtype2))
