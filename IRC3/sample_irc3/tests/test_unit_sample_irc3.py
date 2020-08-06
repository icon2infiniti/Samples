from ..sample_irc3 import SampleIrc3
from tbears.libs.scoretest.score_test_case import ScoreTestCase
from iconservice import *


class TestSampleIrc3(ScoreTestCase):

    def setUp(self):
        super().setUp()

        self.mock_score_address = Address.from_string(f"cx{'1234'*10}")
        self.score = self.get_score_instance(SampleIrc3, self.test_account1)

    def test_get_name(self):
        self.assertEqual("SampleIrc3", self.score.name())

    def test_get_symbol(self):
        self.assertEqual("SIT", self.score.symbol())

    def test_set_mint(self):
        self.set_msg(self.test_account1)
        self.score.mint(self.test_account1, 1)
        self.assertEqual(self.score.ownerOf(1), self.test_account1)
        self.assertEqual(self.score.balanceOf(self.test_account1), 1)

    def test_set_transfer(self):
        self.set_msg(self.test_account1)
        self.score.mint(self.test_account1, 1)
        self.score.transfer(self.test_account2, 1)
        self.assertEqual(self.score.ownerOf(1), self.test_account2)
        self.assertEqual(0, self.score.balanceOf(self.test_account1))
        self.assertEqual(1, self.score.balanceOf(self.test_account2))

    def test_set_approve(self):
        self.set_msg(self.test_account1)
        self.score.mint(self.test_account1, 1)
        self.score.approve(self.test_account2, 1)
        self.assertEqual(self.score.getApproved(1), self.test_account2)

    def test_set_transferFrom(self):
        self.set_msg(self.test_account1)
        self.score.mint(self.test_account1, 1)
        self.score.transferFrom(self.test_account1, self.test_account2, 1)
        self.assertEqual(self.score.ownerOf(1), self.test_account2)
        self.assertEqual(0, self.score.balanceOf(self.test_account1))
        self.assertEqual(1, self.score.balanceOf(self.test_account2))

    def test_get_balanceOf(self):
        self.set_msg(self.test_account1)
        self.score.mint(self.test_account1, 1)
        self.score.mint(self.test_account2, 2)
        self.score.mint(self.test_account1, 3)
        self.score.mint(self.test_account2, 4)
        self.score.mint(self.test_account1, 5)
        self.assertEqual(self.score.balanceOf(self.test_account1), 3)
        self.assertEqual(self.score.balanceOf(self.test_account2), 2)

    def test_set_burn(self):
        self.set_msg(self.test_account1)
        self.score.mint(self.test_account1, 1)
        self.score.burn(1)
        with self.assertRaises(IconScoreException) as e:
            self.score.ownerOf(1)
        self.assertEqual(e.exception.code, 32)
        self.assertEqual(e.exception.message, "Invalid _tokenId. NFT is burned")
        self.assertEqual(self.score.balanceOf(self.test_account1), 0)

    def test_error_transfer(self):
        self.set_msg(self.test_account1)
        self.score.mint(self.test_account1, 1)
        self.score.mint(self.test_account2, 2)
        with self.assertRaises(IconScoreException) as e:
            self.score.transferFrom(self.test_account1, self.test_account2, 2)
        self.assertEqual(e.exception.code, 32)
        self.assertEqual(e.exception.message, "You don't have permission to transfer this NFT")

    def test_erro_ownerOf(self):
        with self.assertRaises(IconScoreException) as e:
            self.score.ownerOf(2)
        self.assertEqual(e.exception.code, 32)
        self.assertEqual(e.exception.message, "Invalid _tokenId. NFT is not minted")
