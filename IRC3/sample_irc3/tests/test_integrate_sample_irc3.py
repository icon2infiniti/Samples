import os

from iconsdk.builder.transaction_builder import (
    DeployTransactionBuilder,
    CallTransactionBuilder
)

from iconsdk.builder.call_builder import CallBuilder
from iconsdk.libs.in_memory_zip import gen_deploy_data_content
from iconsdk.signed_transaction import SignedTransaction
from tbears.libs.icon_integrate_test import IconIntegrateTestBase, SCORE_INSTALL_ADDRESS

from iconservice import Address, AddressPrefix, IconScoreException

DIR_PATH = os.path.abspath(os.path.dirname(__file__))


class TestTest(IconIntegrateTestBase):
    TEST_HTTP_ENDPOINT_URI_V3 = "http://127.0.0.1:9000/api/v3"
    SCORE_PROJECT = os.path.abspath(os.path.join(DIR_PATH, '..'))

    def setUp(self):
        super().setUp()

        self.icon_service = None
        # if you want to send request to network, uncomment next line and set self.TEST_HTTP_ENDPOINT_URI_V3
        # self.icon_service = IconService(HTTPProvider(self.TEST_HTTP_ENDPOINT_URI_V3))

        # install SCORE
        self._score_address = self._deploy_score()['scoreAddress']

    def _deploy_score(self, to: str = SCORE_INSTALL_ADDRESS) -> dict:
        # Generates an instance of transaction for deploying SCORE.
        transaction = DeployTransactionBuilder()             .from_(self._test1.get_address())             .to(to)             .step_limit(100_000_000_000)             .nid(3)             .nonce(100)             .content_type("application/zip")             .content(gen_deploy_data_content(self.SCORE_PROJECT))             .build()

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, self._test1)

        # process the transaction in local
        tx_result = self.process_transaction(signed_transaction, self.icon_service)

        self.assertEqual(True, tx_result['status'])
        self.assertTrue('scoreAddress' in tx_result)

        return tx_result

    def test_score_update(self):
        # update SCORE
        tx_result = self._deploy_score(self._score_address)

        self.assertEqual(self._score_address, tx_result['scoreAddress'])

    def test_call_name(self):
        call = CallBuilder().from_(self._test1.get_address()) \
            .to(self._score_address) \
            .method("name") \
            .build()

        response = self.process_call(call, self.icon_service)
        self.assertEqual("SampleIrc3", response)

    def test_call_symbol(self):
        call = CallBuilder().from_(self._test1.get_address()) \
            .to(self._score_address) \
            .method("symbol") \
            .build()

        response = self.process_call(call, self.icon_service)
        self.assertEqual("SIT", response)

    def test_transfer_from_approved(self):

        # Mint an NFT token first via 'mint'
        params = {
            '_to': self._test1.get_address(),
            '_tokenId': 1
        }
        transaction = CallTransactionBuilder() \
            .from_(self._test1.get_address()) \
            .to(self._score_address) \
            .step_limit(100_000_000) \
            .method("mint") \
            .params(params) \
            .build()

        signed_transaction = SignedTransaction(transaction, self._test1)
        tx_result = self.process_transaction(signed_transaction, self.icon_service)
        self.assertTrue('status' in tx_result)
        self.assertEqual(1, tx_result['status'])

        # Approve token operation to new wallet via 'approve'
        params = {
            '_to': self._wallet_array[0].get_address(),
            '_tokenId': 1
        }
        transaction = CallTransactionBuilder() \
            .from_(self._test1.get_address()) \
            .to(self._score_address) \
            .step_limit(100_000_000) \
            .method("approve") \
            .params(params) \
            .build()

        signed_transaction = SignedTransaction(transaction, self._test1)
        tx_result = self.process_transaction(signed_transaction, self.icon_service)
        self.assertTrue('status' in tx_result)
        self.assertEqual(1, tx_result['status'])

        # Check approval of token 1 via 'getApproval'
        # owner of token 1 should be self._test1
        # approvee of token 1 should be self._wallet_array[0]

        params = {
            "_tokenId": 1
        }
        call = CallBuilder().from_(self._test1.get_address()) \
            .to(self._score_address) \
            .method("getApproved") \
            .params(params) \
            .build()

        response = self.process_call(call, self.icon_service)
        self.assertEqual(response, self._wallet_array[0].get_address())

        # Transfer ownership of token 1 from self._test1 to self._wallet_array[1] by its operator approvee self._wall_array[0] using 'transferFrom'
        params = {
            '_from': self._test1.get_address(),
            '_to': self._wallet_array[1].get_address(),
            '_tokenId': 1
        }
        transaction = CallTransactionBuilder() \
            .from_(self._test1.get_address()) \
            .to(self._score_address) \
            .step_limit(100_000_000) \
            .method("transferFrom") \
            .params(params) \
            .build()

        signed_transaction = SignedTransaction(transaction, self._test1)
        tx_result = self.process_transaction(signed_transaction, self.icon_service)
        self.assertTrue('status' in tx_result)
        self.assertEqual(1, tx_result['status'])

        # Check new ownership of token 1, expected to be self._wallet_array[1]
        params = {
            "_tokenId": 1
        }
        call = CallBuilder().from_(self._test1.get_address()) \
            .to(self._score_address) \
            .method("ownerOf") \
            .params(params) \
            .build()

        response = self.process_call(call, self.icon_service)
        self.assertEqual(response, self._wallet_array[1].get_address())

        # Check token 1's new approved operator, expected zero address
        params = {
            "_tokenId": 1
        }
        call = CallBuilder().from_(self._test1.get_address()) \
            .to(self._score_address) \
            .method("getApproved") \
            .params(params) \
            .build()

        response = self.process_call(call, self.icon_service)
        self.assertEqual(response, str(Address.from_prefix_and_int(AddressPrefix.EOA, 0)))

        # Check token count of self._test1, expected 0
        params = {
            "_owner": self._test1.get_address()
        }
        call = CallBuilder().from_(self._test1.get_address()) \
            .to(self._score_address) \
            .method("balanceOf") \
            .params(params) \
            .build()

        response = self.process_call(call, self.icon_service)
        self.assertEqual(response, hex(0))

        # Last we burn the token from the new owner self._wallet_array[1]
        params = {
            "_tokenId": 1,
        }
        transaction = CallTransactionBuilder() \
            .from_(self._wallet_array[1].get_address()) \
            .to(self._score_address) \
            .step_limit(100_000_000) \
            .method("burn") \
            .params(params) \
            .build()

        signed_transaction = SignedTransaction(transaction, self._wallet_array[1])
        tx_result = self.process_transaction(signed_transaction, self.icon_service)
        self.assertTrue('status' in tx_result)
        self.assertEqual(1, tx_result['status'])

        # Check owner of token 1, expect invalid owner (zero address)
        params = {
            "_tokenId": 1
        }
        call = CallBuilder().from_(self._test1.get_address()) \
            .to(self._score_address) \
            .method("ownerOf") \
            .params(params) \
            .build()

        with self.assertRaises(IconScoreException) as e:
            self.process_call(call, self.icon_service)
        self.assertEqual(e.exception.code, 32)
        self.assertEqual(e.exception.message, "Invalid _tokenId. NFT is burned")
