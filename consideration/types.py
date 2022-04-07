from dataclasses import dataclass
from typing import Optional, TypeVar
from consideration.constants import ItemType, OrderType
from pydantic import BaseModel

from consideration.utils.proxy import ProxyStrategy


@dataclass
class ContractOverrides:
    contract_address: Optional[str]
    legacy_proxy_registry_address: Optional[str]


@dataclass
class ConsiderationConfig:
    # Used because fulfillments may be invalid if confirmations take too long. Default buffer is 30 minutes
    ascending_amount_fulfillment_buffer: int = 1800

    # Allow users to optionally skip balance and approval checks
    balance_and_approval_checks_on_order_creation: bool = True

    # Defaults to use proxy if it would result in zero approvals needed. Otherwise, users can specify the proxy strategy
    # they want to use, relevant for creating orders or fulfilling orders
    proxy_strategy: ProxyStrategy = ProxyStrategy.IF_ZERO_APPROVALS_NEEDED

    overrides: ContractOverrides = ContractOverrides(
        contract_address="", legacy_proxy_registry_address=""
    )


@dataclass
class OfferItem:
    itemType: ItemType
    token: str
    identifierOrCriteria: str
    startAmount: str
    endAmount: str


@dataclass
class ConsiderationItem:
    itemType: ItemType
    token: str
    identifierOrCriteria: str
    startAmount: str
    endAmount: str
    recipient: str


Item = TypeVar("Item", OfferItem, ConsiderationItem)


@dataclass
class OrderParameters:
    offerer: str
    zone: str
    orderType: OrderType
    startTime: str
    endTime: str
    salt: str
    offer: list[OfferItem]
    consideration: list[ConsiderationItem]
    totalOriginalConsiderationItems: int


@dataclass
class OrderComponents(OrderParameters):
    nonce: int


# @dataclass
# class Order:
#     parameters: OrderParameters
#     signature: str


class Order(BaseModel):
    parameters: OrderParameters
    signature: str


@dataclass
class AdvancedOrder(Order):
    numerator: int
    denominator: int


# export type BasicErc721Item = {
#   itemType: ItemType.ERC721;
#   token: string;
#   identifier: string;
# };

# export type Erc721ItemWithCriteria = {
#   itemType: ItemType.ERC721;
#   token: string;
#   identifiers: string[];
#   // Used for criteria based items i.e. offering to buy 5 NFTs for a collection
#   amount?: string;
#   endAmount?: string;
# };

# type Erc721Item = BasicErc721Item | Erc721ItemWithCriteria;

# export type BasicErc1155Item = {
#   itemType: ItemType.ERC1155;
#   token: string;
#   identifier: string;
#   amount: string;
#   endAmount?: string;
# };

# export type Erc1155ItemWithCriteria = {
#   itemType: ItemType.ERC1155;
#   token: string;
#   identifiers: string[];
#   amount: string;
#   endAmount?: string;
# };

# type Erc1155Item = BasicErc1155Item | Erc1155ItemWithCriteria;

# export type CurrencyItem = {
#   token?: string;
#   amount: string;
#   endAmount?: string;
# };

# export type CreateInputItem = Erc721Item | Erc1155Item | CurrencyItem;

# export type ConsiderationInputItem = CreateInputItem & { recipient?: string };

# export type Fee = {
#   recipient: string;
#   basisPoints: number;
# };

# export type CreateOrderInput = {
#   zone?: string;
#   startTime?: string;
#   endTime?: string;
#   offer: readonly CreateInputItem[];
#   consideration: readonly ConsiderationInputItem[];
#   nonce?: number;
#   fees?: readonly Fee[];
#   allowPartialFills?: boolean;
#   restrictedByZone?: boolean;
#   useProxy?: boolean;
#   salt?: string;
# };

# export type InputCriteria = {
#   identifier: string;
#   validIdentifiers: string[];
# };

# export type OrderStatus = {
#   isValidated: boolean;
#   isCancelled: boolean;
#   totalFilled: BigNumber;
#   totalSize: BigNumber;
# };

# export type CreatedOrder = Order & {
#   nonce: number;
# };

# type TransactionRequest = {
#   send: () => Promise<ContractTransaction>;
#   populatedTransaction: Promise<PopulatedTransaction>;
# };

# export type ApprovalAction = {
#   type: "approval";
#   token: string;
#   identifierOrCriteria: string;
#   itemType: ItemType;
#   operator: string;
#   transactionRequest: TransactionRequest;
# };

# export type ExchangeAction = {
#   type: "exchange";
#   transactionRequest: TransactionRequest;
# };

# export type CreateOrderAction = {
#   type: "create";
#   createOrder: () => Promise<CreatedOrder>;
# };

# export type TransactionAction = ApprovalAction | ExchangeAction;

# export type CreateOrderActions = readonly [
#   ...ApprovalAction[],
#   CreateOrderAction
# ];

# export type OrderExchangeActions = readonly [
#   ...ApprovalAction[],
#   ExchangeAction
# ];

# export type OrderUseCase<T extends CreateOrderAction | ExchangeAction> = {
#   actions: T extends CreateOrderAction
#     ? CreateOrderActions
#     : OrderExchangeActions;
#   executeAllActions: () => Promise<
#     T extends CreateOrderAction ? CreatedOrder : ContractTransaction
#   >;
# };

# export type FulfillmentComponent = {
#   orderIndex: number;
#   itemIndex: number;
# };

# export type Fulfillment = {
#   offerComponents: FulfillmentComponent[];
#   considerationComponents: FulfillmentComponent[];
# };
