from typing import Callable, Literal, Optional, TypedDict, Union
from typing_extensions import NotRequired

from eth_typing.evm import ChecksumAddress
from hexbytes import HexBytes
from pydantic import BaseModel
from web3 import Web3
from web3.constants import ADDRESS_ZERO
from web3.types import TxParams

from consideration.constants import ItemType, OrderType, ProxyStrategy
from consideration.utils.pydantic import BaseModelWithEnumValues


class ContractOverrides(BaseModel):
    contract_address: Optional[ChecksumAddress]
    legacy_proxy_registry_address: Optional[ChecksumAddress]


class ConsiderationConfig(BaseModel):
    # Used because fulfillments may be invalid if confirmations take too long. Default buffer is 30 minutes
    ascending_amount_fulfillment_buffer: int = 1800

    # Allow users to optionally skip balance and approval checks
    balance_and_approval_checks_on_order_creation: bool = True

    # Defaults to use proxy if it would result in zero approvals needed. Otherwise, users can specify the proxy strategy
    # they want to use, relevant for creating orders or fulfilling orders
    proxy_strategy: ProxyStrategy = ProxyStrategy.IF_ZERO_APPROVALS_NEEDED

    overrides: ContractOverrides = ContractOverrides(
        contract_address=Web3.toChecksumAddress(ADDRESS_ZERO),
        legacy_proxy_registry_address=Web3.toChecksumAddress(ADDRESS_ZERO),
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
    totalOriginalConsiderationItems: int


class OrderComponents(OrderParameters):
    nonce: int


class Order(BaseModel):
    parameters: OrderParameters
    signature: str


class AdvancedOrder(Order):
    numerator: int
    denominator: int


class CurrencyItem(TypedDict):
    token: NotRequired[str]
    amount: int
    end_amount: NotRequired[int]


class ConsiderationCurrencyItem(CurrencyItem):
    recipient: NotRequired[str]


class BasicErc721Item(TypedDict):
    item_type: Literal[ItemType.ERC721]
    token: str
    identifier: int


class Erc721ItemWithCriteria(TypedDict):
    item_type: Literal[ItemType.ERC721]
    token: str
    identifiers: list[int]
    # Used for criteria based items i.e. offering to buy 5 NFTs for a collection
    amount: NotRequired[int]
    endAmount: NotRequired[int]


Erc721Item = Union[BasicErc721Item, Erc721ItemWithCriteria]


class BasicConsiderationErc721Item(BasicErc721Item):
    recipient: NotRequired[str]


class BasicConsiderationErc721ItemWithCriteria(Erc721ItemWithCriteria):
    recipient: NotRequired[str]


ConsiderationErc721Item = Union[
    BasicConsiderationErc721Item, BasicConsiderationErc721ItemWithCriteria
]


class BasicErc1155Item(TypedDict):
    item_type: Literal[ItemType.ERC1155]
    token: str
    identifier: int
    amount: int
    end_amount: NotRequired[int]


class Erc1155ItemWithCriteria(TypedDict):
    item_type: Literal[ItemType.ERC1155]
    token: str
    identifiers: list[int]
    amount: int
    end_amount: NotRequired[int]


Erc1155Item = Union[BasicErc1155Item, Erc1155ItemWithCriteria]


class BasicConsiderationErc1155Item(BasicErc1155Item):
    recipient: NotRequired[str]


class BasicConsiderationErc1155ItemWithCriteria(Erc1155ItemWithCriteria):
    recipient: NotRequired[str]


ConsiderationErc1155Item = Union[
    BasicConsiderationErc1155Item, BasicConsiderationErc1155ItemWithCriteria
]


CreateInputItem = Union[Erc721Item, Erc1155Item, CurrencyItem]

ConsiderationInputItem = Union[
    ConsiderationErc721Item, ConsiderationErc1155Item, ConsiderationCurrencyItem
]


class Fee(TypedDict):
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


class BalanceAndApproval(BaseModel):
    token: str
    identifier_or_criteria: int
    balance: int
    owner_approved_amount: int
    proxy_approved_amount: int
    item_type: ItemType


BalancesAndApprovals = list[BalanceAndApproval]


class InsufficientBalance(BaseModel):
    token: str
    identifier_or_criteria: int
    required_amount: int
    amount_have: int
    item_type: ItemType


InsufficientBalances = list[InsufficientBalance]


class InsufficientApproval(BaseModel):
    token: str
    identifier_or_criteria: int
    approved_amount: int
    required_approved_amount: int
    operator: str
    item_type: ItemType


InsufficientApprovals = list[InsufficientApproval]


# export type CreatedOrder = Order & {
#   nonce: number;
# };


class Transaction(BaseModel):
    transact: Callable[[Optional[TxParams]], HexBytes]
    build_transaction: Callable[[Optional[TxParams]], TxParams]


class CreatedOrder(Order):
    nonce: int


class CreateOrderAction(BaseModel):
    type = "create"
    create_order: Callable[[], CreatedOrder]


class ApprovalAction(BaseModel):
    type = "approval"
    token: str
    identifier_or_criteria: int
    item_type: ItemType
    operator: str
    transaction: Transaction


class ExchangeAction(BaseModel):
    type = "exchange"
    transaction: Transaction


CreateOrderActions = list[Union[ApprovalAction, CreateOrderAction]]
OrderExchangeActions = list[Union[ApprovalAction, ExchangeAction]]


class CreateOrderUseCase(BaseModel):
    actions: CreateOrderActions
    execute_all_actions: Callable[[], CreatedOrder]


class FulfillOrderUseCase(BaseModel):
    actions: OrderExchangeActions
    execute_all_actions: Callable[[], HexBytes]


# export type FulfillmentComponent = {
#   orderIndex: number;
#   itemIndex: number;
# };

# export type Fulfillment = {
#   offerComponents: FulfillmentComponent[];
#   considerationComponents: FulfillmentComponent[];
# };
