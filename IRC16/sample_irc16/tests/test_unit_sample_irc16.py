from ..sample_irc16 import SampleIRC16
from tbears.libs.scoretest.score_test_case import ScoreTestCase
from iconservice import Address, AddressPrefix, IconScoreException

import hashlib


class TestSampleIRC16(ScoreTestCase):

    def setUp(self):
        super().setUp()
        self.name = "IconHouseToken"
        self.symbol = "IHT"
        self.decimals = 18
        self.total_supply = 10000 # In tokens count, before applying demicals
        #self.controllable = 1

        params = {
            'name': self.name,
            'symbol': self.symbol,
            'decimals': self.decimals,
            'total_supply': self.total_supply,
            #'controllable': self.controllable,
        }
        self.score = self.get_score_instance(SampleIRC16, self.test_account1, params)
        self.set_msg(self.test_account1)

        # self.test_account1 = hxe48913df85da204d99ac22e0180e017c82a5dc9b
        # self.test_account2 = hx541441378726178b4bce6d411765ee0b51bd7a03
        self.test_account3 = Address.from_string(f"hx{'12345'*8}")
        self.test_account4 = Address.from_string(f"hx{'1234'*10}")
        self.test_account5 = Address.from_string(f"hx{'4321'*10}")        

    def test_issue_and_redeem(self):
        self.score.issueByPartition("default", self.test_account3, 1000 * 10 ** self.decimals, b'minting 1000 tokens to test_account3 in default partition')
        self.score.issueByPartition("reserved", self.test_account3, 500 * 10 ** self.decimals, b'minting 500 tokens to test_account3 in reserved partition')
        self.assertEqual(self.score.issuedSupply(), 1500 * 10 ** self.decimals)
        self.assertEqual(self.score.balanceOfByPartition("default", self.test_account3), 1000 * 10 ** self.decimals)
        self.assertEqual(self.score.balanceOfByPartition("reserved", self.test_account3), 500 * 10 ** self.decimals)
        self.assertEqual(self.score.balanceOf(self.test_account3), 1500 * 10 ** self.decimals)

        # Should fail to redeem the tokens as the value is 0
        with self.assertRaises(IconScoreException) as e:
            self.score.redeemByPartition("default", 0, None)
        self.assertEqual(e.exception.code, 32)
        self.assertEqual(e.exception.message, "Invalid amount")

        # Change to test_account3 to test redeemByPartition
        self.set_msg(self.test_account3)
        self.score.redeemByPartition("default", 500 * 10 ** self.decimals, None)
        self.assertEqual(self.score.balanceOfByPartition("default", self.test_account3), 500 * 10 ** self.decimals)
        self.assertEqual(self.score.balanceOfByPartition("reserved", self.test_account3), 500 * 10 ** self.decimals)

        # Authorize all partitions of test_account3 to test_account4
        self.score.authorizeOperator(self.test_account4)
        self.set_msg(self.test_account4)
        self.score.operatorRedeemByPartition("default", self.test_account3, 200 * 10 ** self.decimals, None)
        self.assertEqual(self.score.balanceOfByPartition("default", self.test_account3), 300 * 10 ** self.decimals)

        # Authorize 'reserved' parition of test_account3 to test_account5
        self.set_msg(self.test_account3)  # Need to authorize from test_account3
        self.score.authorizeOperatorForPartition("reserved", self.test_account5)
        self.set_msg(self.test_account5)  # Switch to test_account5 as operator

        with self.assertRaises(IconScoreException) as e:
            self.score.operatorRedeemByPartition("default", self.test_account3, 300 * 10 ** self.decimals, None)
        self.assertEqual(e.exception.code, 32)
        self.assertEqual(e.exception.message, "No operator privilege")

        self.score.operatorRedeemByPartition("reserved", self.test_account3, 500 * 10 ** self.decimals, None)
        self.assertEqual(self.score.balanceOfByPartition("reserved", self.test_account3), 0)

        # Test over issuance by 1        
        self.set_msg(self.test_account1)

        with self.assertRaises(IconScoreException) as e:
            self.score.issueByPartition("default", self.test_account3, 9701 * 10 ** self.decimals, b'over minting')
        self.assertEqual(e.exception.code, 32)
        self.assertEqual(e.exception.message, "Cap reached, available tokens: 9700000000000000000000")

    def test_operators(self):
        # When operator is authorized by owner
        self.score.authorizeOperator(self.test_account2)
        self.assertTrue(self.score.isOperator(self.test_account2, self.test_account1))

        # When operator is revoked
        self.score.revokeOperator(self.test_account2)
        self.assertFalse(self.score.isOperator(self.test_account2, self.test_account1))

    def test_operatorsByPartition(self):
        # Authorize token owner's 'default' partition to test_account2
        self.score.authorizeOperatorForPartition("default", self.test_account2)
        self.assertTrue(self.score.isOperatorForPartition("default", self.test_account2, self.test_account1))

        # Revoke operator privilege
        self.score.revokeOperatorForPartition("default", self.test_account2)
        self.assertFalse(self.score.isOperatorForPartition("default", self.test_account2, self.test_account1))

    def test_setDocument(self):
        doc_name = "myKYC"
        doc_uri = "https://dropbox.com/mykyc.pdf"
        doc_hash = hashlib.sha3_256(doc_name.encode()).hexdigest()

        # This should fail from setting document from a non-owner
        self.set_msg(self.test_account4)
        with self.assertRaises(IconScoreException) as e:
            self.score.setDocument(doc_name, doc_uri, doc_hash)
        self.assertEqual(e.exception.code, 32)
        self.assertEqual(e.exception.message, "Only owner of the contract can set documents")

        self.set_msg(self.test_account1)
        self.score.setDocument(doc_name, doc_uri, doc_hash)

    def test_transferByPartition(self):
        # User owner to mint tokens to test_account2
        self.set_msg(self.test_account1)
        self.score.issueByPartition("default", self.test_account2, 1000 * 10 ** self.decimals, b'minting 1000 tokens to test_account2 in default partition')
        self.score.issueByPartition("reserved", self.test_account2, 500 * 10 ** self.decimals, b'minting 500 tokens to test_account2 in reserved partition')
        # Transfer from test_account2 to test_account3
        self.set_msg(self.test_account2)
        self.score.transferByPartition("default", self.test_account3, 200 * 10 ** self.decimals, b'transfer 200 tokens from default to test_account3')
        self.assertEqual(self.score.balanceOfByPartition("default", self.test_account2), 800 * 10 ** self.decimals)
        self.assertEqual(self.score.balanceOfByPartition("default", self.test_account3), 200 * 10 ** self.decimals)

        # Authorize test_account4 for reserved partition
        self.score.authorizeOperatorForPartition("reserved", self.test_account4)
        self.set_msg(self.test_account4)
        self.score.operatorTransferByPartition("reserved", self.test_account2, self.test_account5, 500 * 10 ** self.decimals, b'transfer 500 reserved token from test_account2 to test_account5 from test_account4')
        self.assertEqual(self.score.balanceOfByPartition("reserved", self.test_account2), 0)
        self.assertEqual(self.score.balanceOfByPartition("reserved", self.test_account5), 500 * 10 ** self.decimals)

    def test_canTransferByPartition(self):
        self.set_msg(self.test_account1)
        self.score.issueByPartition("default", self.test_account2, 1000 * 10 ** self.decimals, b'minting 1000 tokens to test_account2 in default partition')
        self.score.issueByPartition("locked", self.test_account2, 1000 * 10 ** self.decimals, b'minting 1000 tokens to test_account2 in locked partition')
        self.score.issueByPartition("reserved", self.test_account2, 1000 * 10 ** self.decimals, b'minting 1000 tokens to test_account2 in reserved partition')

        self.set_msg(self.test_account2)
        reason = self.score.canTransferByPartition("random", self.test_account2, self.test_account3, 1000 * 10 ** self.decimals, None)
        self.assertEqual(reason, "0x50 Invalid Partition")
        reason = self.score.canTransferByPartition("default", self.test_account2, self.test_account3, 1001 * 10 ** self.decimals, None)
        self.assertEqual(reason, "0x52 Insufficient Balance")
        reason = self.score.canTransferByPartition("default", self.test_account2, Address.from_prefix_and_int(AddressPrefix.EOA, 0), 1000 * 10 ** self.decimals, None)
        self.assertEqual(reason, "0x57 Invalid Receiver")
        reason = self.score.canTransferByPartition("default", self.test_account2, self.test_account3, 1000 * 10 ** self.decimals, None)
        self.assertEqual(reason, "0x51 Transfer Successful")
