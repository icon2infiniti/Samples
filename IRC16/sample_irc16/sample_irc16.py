from iconservice import *

TAG = 'SampleIRC16'


class TokenStandard(ABC):
    # ======================================================================
    # IRC 2
    # ======================================================================
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def symbol(self) -> str:
        pass

    @abstractmethod
    def decimals(self) -> int:
        pass

    @abstractmethod
    def totalSupply(self) -> int:
        pass

    @abstractmethod
    def balanceOf(self, _owner: Address) -> int:
        pass

    # ======================================================================
    # Token Information
    # ======================================================================
    @abstractmethod
    def balanceOfByPartition(self, _partition: str, _owner: Address) -> int:
        pass

    @abstractmethod
    def partitionsOf(self, _owner: Address) -> dict:
        pass

    # ======================================================================
    # Document Management
    # ======================================================================
    @abstractmethod
    def getDocument(self, _name: str) -> dict:
        pass

    @abstractmethod
    def setDocument(self, _name: str, _uri: str, _document_hash: str) -> None:
        pass

    # ======================================================================
    # Partition Token Transfer
    # ======================================================================
    @abstractmethod
    def transferByPartition(self, _partition: str, _to: Address, _amount: int, _data: bytes = None) -> None:
        pass

    @abstractmethod
    def operatorTransferByPartition(self, _partition: str, _from: Address, _to: Address, _amount: int, _data: bytes = None) -> None:
        pass

    # ======================================================================
    # Controller Operation
    # ======================================================================
    """
    @abstractmethod
    def isControllable(self) -> bool:
        pass

    @abstractmethod
    def controllerTransfer(self, _from: Address, _to: Address, _amount: int, _data: bytes = None, _operatorData: bytes = None) -> None:
        pass

    @abstractmethod
    def controllerRedeem(self, _owner: Address, _amount: int, _data: bytes = None, _operatorData: bytes = None) -> None:
        pass
    """

    # ======================================================================
    # Operator Management
    # ======================================================================
    @abstractmethod
    def authorizeOperator(self, _operator: Address) -> None:
        pass

    @abstractmethod
    def revokeOperator(self, _operator: Address) -> None:
        pass

    @abstractmethod
    def authorizeOperatorForPartition(self, _partition: str, _operator: Address) -> None:
        pass

    @abstractmethod
    def revokeOperatorForPartition(self, _partition: str, _operator: Address) -> None:
        pass

    # ======================================================================
    # Operator Information
    # ======================================================================
    @abstractmethod
    def isOperator(self, _operator: Address, _owner: Address) -> bool:
        pass

    @abstractmethod
    def isOperatorForPartition(self, _partition: str, _operator: Address, _owner: Address) -> bool:
        pass

    # ======================================================================
    # Token Issuance
    # ======================================================================
    """
    @abstractmethod
    def isIssuable(self) -> bool:
        pass
    """

    @abstractmethod
    def issueByPartition(self, _partition: str, _to: Address, _amount: int, _data: bytes) -> None:
        pass

    # ======================================================================
    # Token Redemption
    # ======================================================================
    @abstractmethod
    def redeemByPartition(self, _partition: str, _from: Address, _amount: int, _data: bytes) -> None:
        pass

    # ======================================================================
    # Transfer Validity
    # ======================================================================
    @abstractmethod
    def canTransferByPartition(self, _partition: str, _to: Address, _amount: int, _data: bytes = None) -> str:
        pass


class SampleIRC16(IconScoreBase, TokenStandard):
    # Token
    _NAME = 'name'
    _SYMBOL = 'symbol'
    _DECIMALS = 'decimals'
    _TOTAL_SUPPLY = 'total_supply'
    _BALANCES = 'balances'
    _PARTITIONS = 'partitions'
    # Operators
    _APPROVALS = 'approvals'
    _PARTITION_APPROVALS = 'partition_approvals'
    # Documents
    _DOCUMENT = 'document'
    # Controller (force transfer)
    #_CONTROLLABLE = 'controllable'
    #_CONTROLLERS = 'controllers'

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        # Token
        self._name = VarDB(self._NAME, db, value_type=str)
        self._symbol = VarDB(self._SYMBOL, db, value_type=str)
        self._decimals = VarDB(self._DECIMALS, db, value_type=int)
        self._total_supply = VarDB(self._TOTAL_SUPPLY, db, value_type=int)
        self._balances = DictDB(self._BALANCES, db, value_type=int)
        self._partitions = DictDB(self._PARTITIONS, db, value_type=int, depth=2)
        # Operators
        self._approvals = DictDB(self._APPROVALS, db, value_type=bool, depth=2)
        self._partition_approvals = DictDB(self._PARTITION_APPROVALS, db, value_type=bool, depth=3)
        # Document
        self._document = DictDB(self._DOCUMENT, db, value_type=str, depth=2)
        # Controller (force transfer)
        #self._controllable = VarDB(self._CONTROLLABLE, db, value_type=bool)
        #self._controllers = DictDB(self._CONTROLLERS, db, value_type=bool)

    def on_install(self,
                   name: str,
                   symbol: str,
                   decimals: int,
                   initial_supply: int,
                   operator: Address,
                   # controllable: bool,
                   ) -> None:
        super().on_install()

        total_supply = initial_supply * 10 ** decimals

        self._name.set(name)
        self._symbol.set(symbol)
        self._total_supply.set(total_supply)
        self._decimals.set(decimals)
        # self._controllable.set(controllable)
        self.authorizeOperator(operator)

    def on_update(self) -> None:
        super().on_update()

    # ======================================================================
    # IRC 2
    # ======================================================================
    @external(readonly=True)
    def name(self) -> str:
        return self._name.get()

    @external(readonly=True)
    def symbol(self) -> str:
        return self._symbol.get()

    @external(readonly=True)
    def decimals(self) -> int:
        return self._decimals.get()

    @external(readonly=True)
    def totalSupply(self) -> int:
        return self._total_supply.get()

    @external(readonly=True)
    def balanceOf(self, _owner: Address) -> int:
        return self._balances[_owner]

    # ======================================================================
    # Token Information
    # ======================================================================
    @external(readonly=True)
    def balanceOfByPartition(self, _partition: str, _owner: Address) -> int:
        return self._partitions[_owner][_partition]

    @external(readonly=True)
    def partitionsOf(self, _owner: Address) -> dict:
        return self._partitions[_owner]

    # ======================================================================
    # Document Management
    # ======================================================================
    @external(readonly=True)
    def getDocument(self, _name: str) -> dict:
        return {
            'name': _name,
            'uri': self._document[_name]['uri'],
            'document_hash': self._document[_name]['document_hash']
        }

    @external
    def setDocument(self, _name: str, _uri: str, _document_hash: str) -> None:
        if self.msg.sender != self.owner:
            revert("Only owner of the contract can set documents")

        self._document[_name]['uri'] = _uri
        self._document[_name]['document_hash'] = _document_hash
        self.SetDocument(_name, _uri, _document_hash)

    # ======================================================================
    # Partition Token Transfer
    # ======================================================================
    @external
    def transferByPartition(self, _partition: str, _to: Address, _amount: int, _data: bytes = None) -> None:
        self._transferByPartition(_partition, self.msg.sender, self.msg.sender, _to, _amount, _data)

    @external
    def operatorTransferByPartition(self, _partition: str, _from: Address, _to: Address, _amount: int, _data: bytes = None) -> None:
        if self.isOperator(self.msg.sender, _from) or self.isOperatorForPartition(_partition, self.msg.sender, _from):
            self._transferByPartition(_partition, self.msg.sender, _from, _to, _amount, _data)
        else:
            revert("Not authorized to transfer partition")

    def _transferByPartition(self, _partition: str, _operator: Address, _from: Address, _to: Address, _amount: int, _data: bytes) -> None:
        if self._partitions[_from][_partition] < _amount:
            revert("Insufficient balance")

        self._partitions[_from][_partition] -= _amount
        self._balances[_from] -= _amount
        self._partitions[_to][_partition] = self._partitions[_to][_partition] + _amount
        self._balances[_to] = self._balances[_to] + _amount
        data = b'Transfer by partition' if _data is None else _data
        self.TransferByPartition(_partition, _operator, _from, _to, _amount, _data)

    # ======================================================================
    # Controller Operation (force transfer)
    # ======================================================================
    """
    @external(readonly=True)
    def isControllable(self) -> bool:
        return self._controllable.get()

    @external
    def controllerTransfer(self, _from: Address, _to: Address, _amount: int, _data: bytes = None, _operatorData: bytes: None) -> None:
        pass

    @external
    def controllerRedeem(self, _owner: Address, _amount: int, _data: bytes = None, _operatorData: bytes: None) -> None:
        pass
    """

    # ======================================================================
    # Operator Management
    # ======================================================================
    def authorizeOperator(self, _operator: Address) -> None:
        self._approvals[self.msg.sender][_operator] = True
        self.AuthorizeOperator(_operator, self.msg.sender)

    def revokeOperator(self, _operator: Address) -> None:
        self._approvals[self.msg.sender][_operator] = False
        self.RevokeOperator(_operator, self.msg.sender)

    def authorizeOperatorForPartition(self, _partition: str, _operator: Address) -> None:
        self._partition_approvals[self.msg.sender][_partition][_operator] = True
        self.AuthorizeOperatorForPartition(_partition, _operator, self.msg.sender)

    def revokeOperatorForPartition(self, _partition: str, _operator: Address) -> None:
        self._partition_approvals[self.msg.sender][_partition][_operator] = False
        self.RevokeOperatorForPartition(_partition, _operator, self.msg.sender)

    # ======================================================================
    # Operator Information
    # ======================================================================
    @external(readonly=True)
    def isOperator(self, _operator: Address, _owner: Address) -> bool:
        return self._approvals[_owner][_operator]

    @external(readonly=True)
    def isOperatorForPartition(self, _partition: str, _operator: Address, _owner: Address) -> bool:
        return self._partition_approvals[_owner][_partition][_operator]

    # ======================================================================
    # Token Issuance
    # ======================================================================
    @external
    def issueByPartition(self, _partition: str, _to: Address, _amount: int, _data: bytes) -> None:
        if self.msg.sender != self.owner:
            revert('Only owner of the contract can issue new tokens')
        if _amount <= 0:
            revert('Invalid amount')

        self._issueByPartition(_partition, _to, _amount, _data)

    def _issueByPartition(self, _partition: str, _to: Address, _amount: int, _data: bytes) -> None:
        self._total_supply.set(self._total_supply.get() + _amount)
        self._balances[_to] = self._balances[_to] + _amount
        self._partitions[_to][_partition] = self._partitions[_to][_partition] + _amount
        data = b'Issue by partition' if _data is None else _data
        self.IssueByPartition(_partition, _to, _amount, data)

    # ======================================================================
    # Token Redemption
    # ======================================================================
    @external
    def redeemByPartition(self, _partition: str, _amount: int, _data: bytes) -> None:
        self._redeemByPartition(_partition, self.msg.sender, self.msg.sender, _amount, _data)

    @external
    def operatorRedeemByPartition(self, _partition: str, _owner: Address, _amount: int, _data: bytes) -> None:
        if self.isOperator(self.msg.sender, _owner) or self.isOperatorForPartition(_partition, self.msg.sender, _owner):
            self._redeemByPartition(_partition, _owner, self.msg.sender, _amount, _data)
        else:
            revert("No operator privilege")

    def _redeemByPartition(self, _partition: str, _owner: Address, _operator: Address, _amount: int, _data: bytes) -> None:
        if _amount <= 0 or self._partitions[_owner][_partition] < _amount:
            revert("Invalid amount")

        self._total_supply.set(self._total_supply.get() - _amount)
        self._partitions[_owner][_partition] -= _amount
        self._balances[_owner] -= _amount
        data = b'Redeem by partition' if _data is None else _data
        self.RedeemByPartition(_partition, _operator, _owner, _amount, data)

    # ======================================================================
    # Transfer Validity
    # ======================================================================
    @external(readonly=True)
    def canTransferByPartition(self, _partition: str, _to: Address, _amount: int, _data: bytes = None) -> str:
        # Define all error codes
        pass

    # ======================================================================
    # Misc API
    # ======================================================================
    """
    @external(readonly=True)
    def information(self) -> dict:
        return {
            'name': self._name.get(),
            'symbol': self._symbol.get(),
            'total_supply': self._total_supply.get(),
            'decimals': self._decimals.get()
        }
    """

    # ======================================================================
    # Event Logs
    # ======================================================================
    @eventlog(indexed=2)
    def TransferByPartition(self, _partition: str, _operator: Address, _from: Address, _to: Address, _amount: int, _data: bytes):
        pass

    @eventlog(indexed=3)
    def IssueByPartition(self, _partition: str, _to: Address, _amount: int, _data: bytes):
        pass

    @eventlog(indexed=3)
    def RedeemByPartition(self, _partition: str, _operator: Address, _owner: Address, _amount: int, _data: bytes):
        pass

    @eventlog(indexed=2)
    def AuthorizeOperator(self, _operator: Address, _sender: Address):
        pass

    @eventlog(indexed=2)
    def RevokeOperator(self, _operator: Address, _sender: Address):
        pass

    @eventlog(indexed=3)
    def AuthorizeOperatorForPartition(self, _owner: Address, _partition: str, _operator: Address):
        pass

    @eventlog(indexed=3)
    def RevokeOperatorForPartition(self, _owner: Address, _partition: str, _operator: Address):
        pass

    @eventlog(indexed=3)
    def SetDocument(self, _name: str, _uri: str, _document_hash: str):
        pass
