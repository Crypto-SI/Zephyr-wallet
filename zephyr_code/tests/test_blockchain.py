import shutil
import tempfile
import os

from zephyr_code import constants, blockchain
from zephyr_code.simple_config import SimpleConfig
from zephyr_code.blockchain import Blockchain, deserialize_header, hash_header
from zephyr_code.util import bh2u, bfh, make_dir

from zephyr_code.tests.cases import SequentialTestCase


class TestBlockchain(SequentialTestCase):

    HEADERS = {
        'A': deserialize_header(bfh("0100000000000000000000000000000000000000000000000000000000000000000000009bc36d2ba74b96d57bf98bebdf25d1dc2977ae7773273a1014e98bf2e2f62e1bbb2eac56f0ff0f1edfa62400 0000000000000000000000000000000000000000000000000000000000000000"), 0),
        'B': deserialize_header(bfh("0300000018f80e68784ac79737df761bc38e0b5c407384b4ef8ed991969b2b481e0400005fcfd6b2153c917370c077393ab776fdc10f204a411adbc06891a4b3dcd18be09f37ac56ffff0f1e4d000000 0000000000000000000000000000000000000000000000000000000000000000"), 1),
        'C': deserialize_header(bfh("030000002dd1cb1a43d41f2416f4845b30d76f27cd213f2c2a4b856e76a6a44f500500005d018582887dca8f110d54200b6bfb5202364ddce34048cc6be44a7138b2153c5b18ad56ffff0f1e627e0600 0000000000000000000000000000000000000000000000000000000000000000"), 2),
        'D': deserialize_header(bfh("030000007db43d5c00036b7389f4e2b5db0c97bd6c84e24d1a13a306a5450176bf0f0000fd86f76876637a7c49b793d6e544903bb76c4f1bbafbfcd05449f59e9bb0f8d76018ad56ffff0f1e74ec0100 0000000000000000000000000000000000000000000000000000000000000000"), 3),
        'E': deserialize_header(bfh("0300000041dfafa9a67dcac531390b56261e9822fac9050f92673653e5de8354e30d0000031603f2c47e490a5100a7c20fa625c513a41ba02b513a061079ac10737abf537018ad56ffff0f1ec4e00600 0000000000000000000000000000000000000000000000000000000000000000"), 4),
        'F': deserialize_header(bfh("03000000994d19c2fb53b9c54c1e1128624b3e9fffe7b58d2b7c61dbc7684c6970090000ad32e2610822ce6db85709ea14b0b2e42f0bd5373d9cf659aa69e39909dc487a7718ad56ffff0f1ee8140300 0000000000000000000000000000000000000000000000000000000000000000"), 5),
        'O': deserialize_header(bfh("03000000f76a7a0cf908c954d6bbd0d6f7034b826fc1910ec5ac09e1122e07ae3108000000000000000000000000000000000000000000000000000000000000000000007918ad56ffff0f1e0a920100 0000000000000000000000000000000000000000000000000000000000000000"), 6),
        'P': deserialize_header(bfh("03000000f94cdf70a249d552f5d68fe1e62436eea338479b6a288d812d8186e54b0c000000000000000000000000000000000000000000000000000000000000000000007a18ad56ffff0f1eb3652600 0000000000000000000000000000000000000000000000000000000000000000"), 7),
        'Q': deserialize_header(bfh("030000002b228573f03263ad4e5e4584d47a23a171605a76a4755c674232a9c53700000000000000000000000000000000000000000000000000000000000000000000007b18ad56ffff0f1e177f2800 0000000000000000000000000000000000000000000000000000000000000000"), 8),
        'R': deserialize_header(bfh("030000008c96f3adcd2aac5e2eb796c5b6dc9b6ba403b44a939aa98ca5f74dc0d40f000000000000000000000000000000000000000000000000000000000000000000007c18ad56ffff0f1e96ca4300 0000000000000000000000000000000000000000000000000000000000000000"), 9),
        'S': deserialize_header(bfh("03000000e760d464c7b0c17790e4f98b03f733a39cf6d2cd2838bce56eac1531830c000000000000000000000000000000000000000000000000000000000000000000007d18ad56ffff0f1e8fed4400 0000000000000000000000000000000000000000000000000000000000000000"), 10),
        'T': deserialize_header(bfh("030000003f1fd63697629c9c1ceac37bf5172e394211ef0b6585a9fb198fb0c4240a000000000000000000000000000000000000000000000000000000000000000000007e18ad56ffff0f1ee6d54800 0000000000000000000000000000000000000000000000000000000000000000"), 11),
        'U': deserialize_header(bfh("030000006251adf05dbf3ce7bdc58cdfb9cd18ffe732ad2d923ab8b12f7508304a06000000000000000000000000000000000000000000000000000000000000000000007f18ad56ffff0f1ee22d8400 0000000000000000000000000000000000000000000000000000000000000000"), 12),

        'G': deserialize_header(bfh("03000000f76a7a0cf908c954d6bbd0d6f7034b826fc1910ec5ac09e1122e07ae31080000a1bd47688215ca64b4870d7ee64182b14398fa31144f8136bca374139d84b1b67918ad56ffff0f1e2b9c0000 0000000000000000000000000000000000000000000000000000000000000000"), 6),
        'H': deserialize_header(bfh("03000000651e85e4650d59016b2de7b07122e1bef4b431342e4a4484cc3bcfc9550900005b5801c3ea930574539685760c616d8728289fafd3b0a2a97adb9c20217da5648118ad56ffff0f1eeb1e0300 0000000000000000000000000000000000000000000000000000000000000000"), 7),
        'I': deserialize_header(bfh("03000000a0096f01bb2f932cdbdc89b485f47413788499b5d993f0e068f7b6dd3608000059ccdfb3fabd4497224e8bce6e9c1f5c38fa45ad5a6b978dcb1fe5a566f64c178218ad56ffff0f1e912e0000 0000000000000000000000000000000000000000000000000000000000000000"), 8),
        'J': deserialize_header(bfh("03000000db04abf3a4d2bec99d642f7225d0c6062668782fd0a8be77829390f0ec03000000000000000000000000000000000000000000000000000000000000000000008018ad56ffff0f1e485e8b00 0000000000000000000000000000000000000000000000000000000000000000"), 9),
        'K': deserialize_header(bfh("030000001d54b1f2baf052af975a5510b9dd4cf0ca24bf244816068e551ad65c7e03000000000000000000000000000000000000000000000000000000000000000000008118ad56ffff0f1e264f8c00 0000000000000000000000000000000000000000000000000000000000000000"), 10),
        'L': deserialize_header(bfh("03000000fc095f9fe89c6823729af1fe81ac8b62a7b5c868d0c28e725af7bc09f605000000000000000000000000000000000000000000000000000000000000000000008218ad56ffff0f1ef3fa9000 0000000000000000000000000000000000000000000000000000000000000000"), 11),

        'M': deserialize_header(bfh("03000000db04abf3a4d2bec99d642f7225d0c6062668782fd0a8be77829390f0ec030000dc4217cf357c1682e3284498d29129fd4b74d8238dcc2c6ddbd0a7b2e139bf9f7d1ead56ffff0f1e894f0800 0000000000000000000000000000000000000000000000000000000000000000"), 9),
        'N': deserialize_header(bfh("0300000061c51e95037a5d35d2af268e251d8933164b9e4d8e440bf2653d79d2c2020000c40e6efe24e8abd413902cede19a94c8bee9147b54ce890c36772655ebd4daca841ead56ffff0f1e46630200 0000000000000000000000000000000000000000000000000000000000000000"), 10),
        'X': deserialize_header(bfh("030000005d66515807d72352b2102f498feb5910b7eb19499ca07a9e1abc903c230e0000679057e7db7fecfcdb764b2eaf43fd03cbfc3539501d4c91c8fc73c566b1ee9e851ead56ffff0f1e035b0000 0000000000000000000000000000000000000000000000000000000000000000"), 11),
        'Y': deserialize_header(bfh("0300000067cd438969e15c0eb51179cd18c1223ad63101ac6236e6960484b781900d0000cd5310a89b82528eed220222df258cfd93ae4eaa05f435a17dbc4e4d6060aa61891ead56ffff0f1eb94b0100 0000000000000000000000000000000000000000000000000000000000000000"), 12),
        'Z': deserialize_header(bfh("0300000083bc0a94b0915870199985cc0618029cfc599270f81839d556ef54f78b070000d40f5a290cd4f44993da756e271a54d225f5ca07e35634bbaeb7236fe293cfd18a1ead56ffff0f1e722f0000 0000000000000000000000000000000000000000000000000000000000000000"), 13),
    }
    # tree of headers:
    #                                            - M <- N <- X <- Y <- Z
    #                                          /
    #                             - G <- H <- I <- J <- K <- L
    #                           /
    # A <- B <- C <- D <- E <- F <- O <- P <- Q <- R <- S <- T <- U

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        constants.set_regtest()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        constants.set_mainnet()

    def setUp(self):
        super().setUp()
        self.data_dir = tempfile.mkdtemp()
        make_dir(os.path.join(self.data_dir, 'forks'))
        self.config = SimpleConfig({'electrum_path': self.data_dir})
        blockchain.blockchains = {}

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.data_dir)

    def _append_header(self, chain: Blockchain, header: dict):
        self.assertTrue(chain.can_connect(header))
        chain.save_header(header)

    def test_get_height_of_last_common_block_with_chain(self):
        blockchain.blockchains[constants.net.GENESIS] = chain_u = Blockchain(
            config=self.config, forkpoint=0, parent=None,
            forkpoint_hash=constants.net.GENESIS, prev_hash=None)
        open(chain_u.path(), 'w+').close()
        self._append_header(chain_u, self.HEADERS['A'])
        self._append_header(chain_u, self.HEADERS['B'])
        self._append_header(chain_u, self.HEADERS['C'])
        self._append_header(chain_u, self.HEADERS['D'])
        self._append_header(chain_u, self.HEADERS['E'])
        self._append_header(chain_u, self.HEADERS['F'])
        self._append_header(chain_u, self.HEADERS['O'])
        self._append_header(chain_u, self.HEADERS['P'])
        self._append_header(chain_u, self.HEADERS['Q'])

        chain_l = chain_u.fork(self.HEADERS['G'])
        self._append_header(chain_l, self.HEADERS['H'])
        self._append_header(chain_l, self.HEADERS['I'])
        self._append_header(chain_l, self.HEADERS['J'])
        self._append_header(chain_l, self.HEADERS['K'])
        self._append_header(chain_l, self.HEADERS['L'])

        self.assertEqual({chain_u:  8, chain_l: 5}, chain_u.get_parent_heights())
        self.assertEqual({chain_l: 11},             chain_l.get_parent_heights())

        chain_z = chain_l.fork(self.HEADERS['M'])
        self._append_header(chain_z, self.HEADERS['N'])
        self._append_header(chain_z, self.HEADERS['X'])
        self._append_header(chain_z, self.HEADERS['Y'])
        self._append_header(chain_z, self.HEADERS['Z'])

        self.assertEqual({chain_u:  8, chain_z: 5}, chain_u.get_parent_heights())
        self.assertEqual({chain_l: 11, chain_z: 8}, chain_l.get_parent_heights())
        self.assertEqual({chain_z: 13},             chain_z.get_parent_heights())
        self.assertEqual(5, chain_u.get_height_of_last_common_block_with_chain(chain_l))
        self.assertEqual(5, chain_l.get_height_of_last_common_block_with_chain(chain_u))
        self.assertEqual(5, chain_u.get_height_of_last_common_block_with_chain(chain_z))
        self.assertEqual(5, chain_z.get_height_of_last_common_block_with_chain(chain_u))
        self.assertEqual(8, chain_l.get_height_of_last_common_block_with_chain(chain_z))
        self.assertEqual(8, chain_z.get_height_of_last_common_block_with_chain(chain_l))

        self._append_header(chain_u, self.HEADERS['R'])
        self._append_header(chain_u, self.HEADERS['S'])
        self._append_header(chain_u, self.HEADERS['T'])
        self._append_header(chain_u, self.HEADERS['U'])

        self.assertEqual({chain_u: 12, chain_z: 5}, chain_u.get_parent_heights())
        self.assertEqual({chain_l: 11, chain_z: 8}, chain_l.get_parent_heights())
        self.assertEqual({chain_z: 13},             chain_z.get_parent_heights())
        self.assertEqual(5, chain_u.get_height_of_last_common_block_with_chain(chain_l))
        self.assertEqual(5, chain_l.get_height_of_last_common_block_with_chain(chain_u))
        self.assertEqual(5, chain_u.get_height_of_last_common_block_with_chain(chain_z))
        self.assertEqual(5, chain_z.get_height_of_last_common_block_with_chain(chain_u))
        self.assertEqual(8, chain_l.get_height_of_last_common_block_with_chain(chain_z))
        self.assertEqual(8, chain_z.get_height_of_last_common_block_with_chain(chain_l))

    def test_parents_after_forking(self):
        blockchain.blockchains[constants.net.GENESIS] = chain_u = Blockchain(
            config=self.config, forkpoint=0, parent=None,
            forkpoint_hash=constants.net.GENESIS, prev_hash=None)
        open(chain_u.path(), 'w+').close()
        self._append_header(chain_u, self.HEADERS['A'])
        self._append_header(chain_u, self.HEADERS['B'])
        self._append_header(chain_u, self.HEADERS['C'])
        self._append_header(chain_u, self.HEADERS['D'])
        self._append_header(chain_u, self.HEADERS['E'])
        self._append_header(chain_u, self.HEADERS['F'])
        self._append_header(chain_u, self.HEADERS['O'])
        self._append_header(chain_u, self.HEADERS['P'])
        self._append_header(chain_u, self.HEADERS['Q'])

        self.assertEqual(None, chain_u.parent)

        chain_l = chain_u.fork(self.HEADERS['G'])
        self._append_header(chain_l, self.HEADERS['H'])
        self._append_header(chain_l, self.HEADERS['I'])
        self._append_header(chain_l, self.HEADERS['J'])
        self._append_header(chain_l, self.HEADERS['K'])
        self._append_header(chain_l, self.HEADERS['L'])

        self.assertEqual(None,    chain_l.parent)
        self.assertEqual(chain_l, chain_u.parent)

        chain_z = chain_l.fork(self.HEADERS['M'])
        self._append_header(chain_z, self.HEADERS['N'])
        self._append_header(chain_z, self.HEADERS['X'])
        self._append_header(chain_z, self.HEADERS['Y'])
        self._append_header(chain_z, self.HEADERS['Z'])

        self.assertEqual(chain_z, chain_u.parent)
        self.assertEqual(chain_z, chain_l.parent)
        self.assertEqual(None,    chain_z.parent)

        self._append_header(chain_u, self.HEADERS['R'])
        self._append_header(chain_u, self.HEADERS['S'])
        self._append_header(chain_u, self.HEADERS['T'])
        self._append_header(chain_u, self.HEADERS['U'])

        self.assertEqual(chain_z, chain_u.parent)
        self.assertEqual(chain_z, chain_l.parent)
        self.assertEqual(None,    chain_z.parent)

    def test_forking_and_swapping(self):
        blockchain.blockchains[constants.net.GENESIS] = chain_u = Blockchain(
            config=self.config, forkpoint=0, parent=None,
            forkpoint_hash=constants.net.GENESIS, prev_hash=None)
        open(chain_u.path(), 'w+').close()

        self._append_header(chain_u, self.HEADERS['A'])
        self._append_header(chain_u, self.HEADERS['B'])
        self._append_header(chain_u, self.HEADERS['C'])
        self._append_header(chain_u, self.HEADERS['D'])
        self._append_header(chain_u, self.HEADERS['E'])
        self._append_header(chain_u, self.HEADERS['F'])
        self._append_header(chain_u, self.HEADERS['O'])
        self._append_header(chain_u, self.HEADERS['P'])
        self._append_header(chain_u, self.HEADERS['Q'])
        self._append_header(chain_u, self.HEADERS['R'])

        chain_l = chain_u.fork(self.HEADERS['G'])
        self._append_header(chain_l, self.HEADERS['H'])
        self._append_header(chain_l, self.HEADERS['I'])
        self._append_header(chain_l, self.HEADERS['J'])

        # do checks
        self.assertEqual(2, len(blockchain.blockchains))
        self.assertEqual(1, len(os.listdir(os.path.join(self.data_dir, "forks"))))
        self.assertEqual(0, chain_u.forkpoint)
        self.assertEqual(None, chain_u.parent)
        self.assertEqual(constants.net.GENESIS, chain_u._forkpoint_hash)
        self.assertEqual(None, chain_u._prev_hash)
        self.assertEqual(os.path.join(self.data_dir, "blockchain_headers"), chain_u.path())
        self.assertEqual(10 * 112, os.stat(chain_u.path()).st_size)
        self.assertEqual(6, chain_l.forkpoint)
        self.assertEqual(chain_u, chain_l.parent)
        self.assertEqual(hash_header(self.HEADERS['G']), chain_l._forkpoint_hash)
        self.assertEqual(hash_header(self.HEADERS['F']), chain_l._prev_hash)
        self.assertEqual(os.path.join(self.data_dir, "forks", "fork2_6_831ae072e12e109acc50e91c16f824b03f7d6d0bbd654c908f90c7a6af7_955c9cf3bcc84444a2e3431b4f4bee12271b0e72d6b01590d65e4851e65"), chain_l.path())
        self.assertEqual(4 * 112, os.stat(chain_l.path()).st_size)

        self._append_header(chain_l, self.HEADERS['K'])

        # chains were swapped, do checks
        self.assertEqual(2, len(blockchain.blockchains))
        self.assertEqual(1, len(os.listdir(os.path.join(self.data_dir, "forks"))))
        self.assertEqual(6, chain_u.forkpoint)
        self.assertEqual(chain_l, chain_u.parent)
        self.assertEqual(hash_header(self.HEADERS['O']), chain_u._forkpoint_hash)
        self.assertEqual(hash_header(self.HEADERS['F']), chain_u._prev_hash)
        self.assertEqual(os.path.join(self.data_dir, "forks", "fork2_6_831ae072e12e109acc50e91c16f824b03f7d6d0bbd654c908f90c7a6af7_c4be586812d818d286a9b4738a3ee3624e6e18fd6f552d549a270df4cf9"), chain_u.path())
        self.assertEqual(4 * 112, os.stat(chain_u.path()).st_size)
        self.assertEqual(0, chain_l.forkpoint)
        self.assertEqual(None, chain_l.parent)
        self.assertEqual(constants.net.GENESIS, chain_l._forkpoint_hash)
        self.assertEqual(None, chain_l._prev_hash)
        self.assertEqual(os.path.join(self.data_dir, "blockchain_headers"), chain_l.path())
        self.assertEqual(11 * 112, os.stat(chain_l.path()).st_size)
        for b in (chain_u, chain_l):
            self.assertTrue(all([b.can_connect(b.read_header(i), False) for i in range(b.height())]))

        self._append_header(chain_u, self.HEADERS['S'])
        self._append_header(chain_u, self.HEADERS['T'])
        self._append_header(chain_u, self.HEADERS['U'])
        self._append_header(chain_l, self.HEADERS['L'])

        chain_z = chain_l.fork(self.HEADERS['M'])
        self._append_header(chain_z, self.HEADERS['N'])
        self._append_header(chain_z, self.HEADERS['X'])
        self._append_header(chain_z, self.HEADERS['Y'])
        self._append_header(chain_z, self.HEADERS['Z'])

        # chain_z became best chain, do checks
        self.assertEqual(3, len(blockchain.blockchains))
        self.assertEqual(2, len(os.listdir(os.path.join(self.data_dir, "forks"))))
        self.assertEqual(0, chain_z.forkpoint)
        self.assertEqual(None, chain_z.parent)
        self.assertEqual(constants.net.GENESIS, chain_z._forkpoint_hash)
        self.assertEqual(None, chain_z._prev_hash)
        self.assertEqual(os.path.join(self.data_dir, "blockchain_headers"), chain_z.path())
        self.assertEqual(14 * 112, os.stat(chain_z.path()).st_size)
        self.assertEqual(9, chain_l.forkpoint)
        self.assertEqual(chain_z, chain_l.parent)
        self.assertEqual(hash_header(self.HEADERS['J']), chain_l._forkpoint_hash)
        self.assertEqual(hash_header(self.HEADERS['I']), chain_l._prev_hash)
        self.assertEqual(os.path.join(self.data_dir, "forks", "fork2_9_3ecf090938277bea8d02f78682606c6d025722f649dc9bed2a4f3ab04db_37e5cd61a558e06164824bf24caf04cddb910555a97af52f0baf2b1541d"), chain_l.path())
        self.assertEqual(3 * 112, os.stat(chain_l.path()).st_size)
        self.assertEqual(6, chain_u.forkpoint)
        self.assertEqual(chain_z, chain_u.parent)
        self.assertEqual(hash_header(self.HEADERS['O']), chain_u._forkpoint_hash)
        self.assertEqual(hash_header(self.HEADERS['F']), chain_u._prev_hash)
        self.assertEqual(os.path.join(self.data_dir, "forks", "fork2_6_831ae072e12e109acc50e91c16f824b03f7d6d0bbd654c908f90c7a6af7_c4be586812d818d286a9b4738a3ee3624e6e18fd6f552d549a270df4cf9"), chain_u.path())
        self.assertEqual(7 * 112, os.stat(chain_u.path()).st_size)
        for b in (chain_u, chain_l, chain_z):
            self.assertTrue(all([b.can_connect(b.read_header(i), False) for i in range(b.height())]))

        self.assertEqual(constants.net.GENESIS, chain_z.get_hash(0))
        self.assertEqual(hash_header(self.HEADERS['F']), chain_z.get_hash(5))
        self.assertEqual(hash_header(self.HEADERS['G']), chain_z.get_hash(6))
        self.assertEqual(hash_header(self.HEADERS['I']), chain_z.get_hash(8))
        self.assertEqual(hash_header(self.HEADERS['M']), chain_z.get_hash(9))
        self.assertEqual(hash_header(self.HEADERS['Z']), chain_z.get_hash(13))

    def test_doing_multiple_swaps_after_single_new_header(self):
        blockchain.blockchains[constants.net.GENESIS] = chain_u = Blockchain(
            config=self.config, forkpoint=0, parent=None,
            forkpoint_hash=constants.net.GENESIS, prev_hash=None)
        open(chain_u.path(), 'w+').close()

        self._append_header(chain_u, self.HEADERS['A'])
        self._append_header(chain_u, self.HEADERS['B'])
        self._append_header(chain_u, self.HEADERS['C'])
        self._append_header(chain_u, self.HEADERS['D'])
        self._append_header(chain_u, self.HEADERS['E'])
        self._append_header(chain_u, self.HEADERS['F'])
        self._append_header(chain_u, self.HEADERS['O'])
        self._append_header(chain_u, self.HEADERS['P'])
        self._append_header(chain_u, self.HEADERS['Q'])
        self._append_header(chain_u, self.HEADERS['R'])
        self._append_header(chain_u, self.HEADERS['S'])

        self.assertEqual(1, len(blockchain.blockchains))
        self.assertEqual(0, len(os.listdir(os.path.join(self.data_dir, "forks"))))

        chain_l = chain_u.fork(self.HEADERS['G'])
        self._append_header(chain_l, self.HEADERS['H'])
        self._append_header(chain_l, self.HEADERS['I'])
        self._append_header(chain_l, self.HEADERS['J'])
        self._append_header(chain_l, self.HEADERS['K'])
        # now chain_u is best chain, but it's tied with chain_l

        self.assertEqual(2, len(blockchain.blockchains))
        self.assertEqual(1, len(os.listdir(os.path.join(self.data_dir, "forks"))))

        chain_z = chain_l.fork(self.HEADERS['M'])
        self._append_header(chain_z, self.HEADERS['N'])
        self._append_header(chain_z, self.HEADERS['X'])

        self.assertEqual(3, len(blockchain.blockchains))
        self.assertEqual(2, len(os.listdir(os.path.join(self.data_dir, "forks"))))

        # chain_z became best chain, do checks
        self.assertEqual(0, chain_z.forkpoint)
        self.assertEqual(None, chain_z.parent)
        self.assertEqual(constants.net.GENESIS, chain_z._forkpoint_hash)
        self.assertEqual(None, chain_z._prev_hash)
        self.assertEqual(os.path.join(self.data_dir, "blockchain_headers"), chain_z.path())
        self.assertEqual(12 * 112, os.stat(chain_z.path()).st_size)
        self.assertEqual(9, chain_l.forkpoint)
        self.assertEqual(chain_z, chain_l.parent)
        self.assertEqual(hash_header(self.HEADERS['J']), chain_l._forkpoint_hash)
        self.assertEqual(hash_header(self.HEADERS['I']), chain_l._prev_hash)
        self.assertEqual(os.path.join(self.data_dir, "forks", "fork2_9_3ecf090938277bea8d02f78682606c6d025722f649dc9bed2a4f3ab04db_37e5cd61a558e06164824bf24caf04cddb910555a97af52f0baf2b1541d"), chain_l.path())
        self.assertEqual(2 * 112, os.stat(chain_l.path()).st_size)
        self.assertEqual(6, chain_u.forkpoint)
        self.assertEqual(chain_z, chain_u.parent)
        self.assertEqual(hash_header(self.HEADERS['O']), chain_u._forkpoint_hash)
        self.assertEqual(hash_header(self.HEADERS['F']), chain_u._prev_hash)
        self.assertEqual(os.path.join(self.data_dir, "forks", "fork2_6_831ae072e12e109acc50e91c16f824b03f7d6d0bbd654c908f90c7a6af7_c4be586812d818d286a9b4738a3ee3624e6e18fd6f552d549a270df4cf9"), chain_u.path())
        self.assertEqual(5 * 112, os.stat(chain_u.path()).st_size)

        self.assertEqual(constants.net.GENESIS, chain_z.get_hash(0))
        self.assertEqual(hash_header(self.HEADERS['F']), chain_z.get_hash(5))
        self.assertEqual(hash_header(self.HEADERS['G']), chain_z.get_hash(6))
        self.assertEqual(hash_header(self.HEADERS['I']), chain_z.get_hash(8))
        self.assertEqual(hash_header(self.HEADERS['M']), chain_z.get_hash(9))
        self.assertEqual(hash_header(self.HEADERS['X']), chain_z.get_hash(11))

        for b in (chain_u, chain_l, chain_z):
            self.assertTrue(all([b.can_connect(b.read_header(i), False) for i in range(b.height())]))
