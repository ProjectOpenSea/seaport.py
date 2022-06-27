from typing import Any, Callable, Optional, Protocol, Union, runtime_checkable

from eth_typing.evm import ChecksumAddress
from hexbytes import HexBytes
from pydantic import BaseModel
from web3 import Web3
from web3.constants import ADDRESS_ZERO
from web3.types import TxParams

from seaport.constants import NO_CONDUIT_KEY, ItemType, OrderType, Side
from seaport.utils.pydantic import BaseModelWithEnumValues


class ContractOverrides(BaseModel):
    contract_address: Optional[ChecksumAddress] = Web3.toChecksumAddress(ADDRESS_ZERO)
    default_conduit_key: Optional[str] = NO_CONDUIT_KEY


class SeaportConfig(BaseModel):
    # Used because fulfillments may be invalid if confirmations take too long. Default buffer is 30 minutes
    ascending_amount_fulfillment_buffer: int = 1800

    # Allow users to optionally skip balance and approval checks
    balance_and_approval_checks_on_order_creation: bool = True

    # A mapping of conduit key to conduit
    conduit_key_to_conduit: dict[str, str] = {}

    overrides: ContractOverrides = ContractOverrides(
        contract_address=Web3.toChecksumAddress(ADDRESS_ZERO),
        default_conduit_key=NO_CONDUIT_KEY,
    )


class OfferItem(BaseModelWithEnumValues):
    itemType: ItemType
    token: str
    identifierOrCriteria: int
    startAmount: int
    endAmount: int


class ConsiderationItem(BaseModelWithEnumValues):
    itemType: ItemType
    token: str
    identifierOrCriteria: int
    startAmount: int
    endAmount: int
    recipient: str


Item = Union[OfferItem, ConsiderationItem]


class OrderParameters(BaseModelWithEnumValues):
    offerer: str
    zone: str
    orderType: OrderType
    startTime: int
    endTime: int
    salt: int
    offer: list[OfferItem]
    consideration: list[ConsiderationItem]
    zoneHash: str
    totalOriginalConsiderationItems: int
    conduitKey: str


class OrderComponents(OrderParameters):
    counter: int


class Order(BaseModel):
    parameters: OrderParameters
    signature: str


class OrderWithCounter(Order):
    parameters: OrderComponents
    signature: str


FulfillableOrder = Union[Order, OrderWithCounter]


class AdvancedOrder(Order):
    numerator: int
    denominator: int


class OfferCurrencyItem(BaseModel):
    token: Optional[str] = None
    amount: int
    end_amount: Optional[int] = None


class ConsiderationCurrencyItem(OfferCurrencyItem):
    recipient: Optional[str] = None


class OfferErc721Item(BaseModel):
    item_type = ItemType.ERC721
    token: str
    identifier: int


class OfferErc721ItemWithCriteria(BaseModel):
    item_type = ItemType.ERC721_WITH_CRITERIA
    token: str
    identifiers: list[int]
    # Used for criteria based items i.e. offering to buy 5 NFTs for a collection
    amount: Optional[int] = 1
    end_amount: Optional[int] = 1


OfferErc721InputItem = Union[OfferErc721Item, OfferErc721ItemWithCriteria]


class ConsiderationErc721Item(OfferErc721Item):
    recipient: Optional[str] = None


class ConsiderationErc721ItemWithCriteria(OfferErc721ItemWithCriteria):
    recipient: Optional[str] = None


ConsiderationErc721InputItem = Union[
    ConsiderationErc721Item, ConsiderationErc721ItemWithCriteria
]


class OfferErc1155Item(BaseModel):
    item_type = ItemType.ERC1155
    token: str
    identifier: int
    amount: int
    end_amount: Optional[int] = None


class OfferErc1155ItemWithCriteria(BaseModel):
    item_type = ItemType.ERC1155_WITH_CRITERIA
    token: str
    identifiers: list[int]
    amount: int
    end_amount: Optional[int] = None


OfferErc1155InputItem = Union[OfferErc1155Item, OfferErc1155ItemWithCriteria]


class ConsiderationErc1155Item(OfferErc1155Item):
    recipient: Optional[str] = None


class ConsiderationErc1155ItemWithCriteria(OfferErc1155ItemWithCriteria):
    recipient: Optional[str] = None


ConsiderationErc1155InputItem = Union[
    ConsiderationErc1155Item, ConsiderationErc1155ItemWithCriteria
]


CreateInputItem = Union[OfferErc721InputItem, OfferErc1155InputItem, OfferCurrencyItem]

ConsiderationInputItem = Union[
    ConsiderationErc721InputItem,
    ConsiderationErc1155InputItem,
    ConsiderationCurrencyItem,
]


class Fee(BaseModel):
    recipient: str
    basis_points: int


class InputCriteria(BaseModel):
    identifier: int
    valid_identifiers: list[int]


class OrderStatus(BaseModel):
    is_validated: bool
    is_cancelled: bool
    total_filled: int
    total_size: int


class BalanceAndApproval(BaseModelWithEnumValues):
    token: str
    identifier_or_criteria: int
    balance: int
    approved_amount: int
    item_type: ItemType


BalancesAndApprovals = list[BalanceAndApproval]


class InsufficientBalance(BaseModelWithEnumValues):
    token: str
    identifier_or_criteria: int
    required_amount: int
    amount_have: int
    item_type: ItemType


InsufficientBalances = list[InsufficientBalance]


class InsufficientApproval(BaseModelWithEnumValues):
    token: str
    identifier_or_criteria: int
    approved_amount: int
    required_approved_amount: int
    operator: str
    item_type: ItemType


InsufficientApprovals = list[InsufficientApproval]


@runtime_checkable
class BuildTransaction(Protocol):
    def __call__(self, transaction: Optional[TxParams] = None) -> TxParams:
        ...


@runtime_checkable
class CallStatic(Protocol):
    def __call__(self, transaction: Optional[TxParams] = None) -> Any:
        ...


@runtime_checkable
class EstimateGas(Protocol):
    def __call__(self, transaction: Optional[TxParams] = None) -> int:
        ...


@runtime_checkable
class Transact(Protocol):
    def __call__(self, transaction: Optional[TxParams] = None) -> HexBytes:
        ...


class TransactionMethods(BaseModel):
    build_transaction: BuildTransaction
    call_static: CallStatic
    estimate_gas: EstimateGas
    transact: Transact

    class Config:
        arbitrary_types_allowed = True


class CreateOrderAction(BaseModel):
    type = "create"
    get_message_to_sign: Callable[[], str]
    create_order: Callable[[], OrderWithCounter]


class ApprovalAction(BaseModelWithEnumValues):
    type = "approval"
    token: str
    identifier_or_criteria: int
    item_type: ItemType
    operator: str
    transaction_methods: TransactionMethods


class ExchangeAction(BaseModel):
    type = "exchange"
    transaction_methods: TransactionMethods


CreateOrderActions = list[Union[ApprovalAction, CreateOrderAction]]
OrderExchangeActions = list[Union[ApprovalAction, ExchangeAction]]


class CreateOrderUseCase(BaseModel):
    actions: CreateOrderActions
    execute_all_actions: Callable[[], OrderWithCounter]


class FulfillOrderUseCase(BaseModel):
    actions: OrderExchangeActions
    execute_all_actions: Callable[[], HexBytes]


class CriteriaResolver(BaseModelWithEnumValues):
    orderIndex: int
    side: Side
    index: int
    identifier: int
    criteriaProof: list[str]


class FulfillOrderDetails(BaseModel):
    order: OrderWithCounter
    units_to_fill: int = 0
    offer_criteria: list[InputCriteria] = []
    consideration_criteria: list[InputCriteria] = []
    tips: list[ConsiderationInputItem] = []
    extra_data: str = "0x"


class FulfillmentComponent(BaseModel):
    orderIndex: int
    itemIndex: int
