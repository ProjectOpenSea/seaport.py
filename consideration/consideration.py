from itertools import chain
from time import time
from typing import Optional, cast
from hexbytes import HexBytes

from web3 import Web3
from web3.constants import ADDRESS_ZERO
from web3.contract import Contract
from web3.providers.base import BaseProvider
from web3.types import RPCEndpoint

from consideration.abi.Consideration import CONSIDERATION_ABI
from consideration.abi.ProxyRegistryInterface import PROXY_REGISTRY_INTERFACE_ABI
from consideration.constants import (
    CONSIDERATION_CONTRACT_NAME,
    CONSIDERATION_CONTRACT_VERSION,
    EIP_712_ORDER_TYPE,
    LEGACY_PROXY_CONDUIT,
    MAX_INT,
    NO_CONDUIT,
    OrderType,
)
from consideration.utils.fulfill import (
    fulfill_basic_order,
    should_use_basic_fulfill,
    validate_and_sanitize_from_order_status,
)
from consideration.types import (
    ConsiderationConfig,
    ConsiderationInputItem,
    ConsiderationItem,
    CreatedOrder,
    CreateInputItem,
    CreateOrderAction,
    CreateOrderUseCase,
    Fee,
    FulfillOrderUseCase,
    InputCriteria,
    Order,
    OrderComponents,
    OrderParameters,
    OrderStatus,
    TransactionMethods,
)
from consideration.utils.balance_and_approval_check import (
    get_approval_actions,
    get_balances_and_approvals,
    get_insufficient_balance_and_approval_amounts,
    use_proxy_from_approvals,
    validate_offer_balances_and_approvals,
)
from consideration.utils.hex_utils import bytes_to_hex
from consideration.utils.item import (
    TimeBasedItemParams,
    get_summed_token_and_identifier_amounts,
    is_currency_item,
)
from consideration.utils.order import (
    are_all_currencies_same,
    deduct_fees,
    fee_to_consideration_item,
    generate_random_salt,
    map_input_item_to_offer_item,
    total_items_amount,
)
from consideration.utils.pydantic import dict_int_to_str, parse_model_list
from consideration.utils.usecase import execute_all_actions, get_transaction_methods


class Consideration:
    contract: Contract
    web3: Web3
    config: ConsiderationConfig
    legacy_proxy_registry_address: str

    def __init__(
        self,
        provider: BaseProvider,
        config: ConsiderationConfig = ConsiderationConfig(),
    ):
        self.web3 = Web3(provider=provider)
        self.config = config
        self.legacy_proxy_registry_address = (
            config.overrides.legacy_proxy_registry_address or ADDRESS_ZERO
        )
        self.contract = self.web3.eth.contract(
            address=config.overrides.contract_address
            or Web3.toChecksumAddress(ADDRESS_ZERO),
            abi=CONSIDERATION_ABI,
        )

    def _get_order_type_from_options(
        self, *, allow_partial_fills: bool, restricted_by_zone: bool
    ):
        if allow_partial_fills:
            return (
                OrderType.PARTIAL_RESTRICTED
                if restricted_by_zone
                else OrderType.PARTIAL_OPEN
            )
        return OrderType.FULL_RESTRICTED if restricted_by_zone else OrderType.FULL_OPEN

    def _get_legacy_conduit_proxy(self, address: str) -> str:
        proxy_registry = self.web3.eth.contract(
            address=Web3.toChecksumAddress(self.legacy_proxy_registry_address),
            abi=PROXY_REGISTRY_INTERFACE_ABI,
        )

        return proxy_registry.functions.proxies(address).call()

    def create_order(
        self,
        *,
        account_address: Optional[str] = None,
        allow_partial_fills=False,
        consideration: list[ConsiderationInputItem],
        fees: list[Fee] = [],
        nonce: Optional[int] = None,
        offer: list[CreateInputItem],
        restricted_by_zone=False,
        salt=generate_random_salt(),
        start_time: int = int(time()),
        zone: str = ADDRESS_ZERO,
        end_time: int = MAX_INT,
    ) -> CreateOrderUseCase:
        """
        Returns a use case that will create an order.
        The use case will contain the list of actions necessary to finish creating an order.
        The list of actions will either be an approval if approvals are necessary
        or a signature request that will then be supplied into the final Order struct, ready to be fulfilled.

        Args:
            offer (list[CreateInputItem]): The items you are willing to offer. This is a condensed version of the Consideration struct OfferItem for convenience
            consideration (list[ConsiderationInputItem]): The items that will go to their respective recipients upon receiving your offer.
            nonce (Optional[int], optional): The nonce from which to create the order with. Automatically fetched from the contract if not provided.
            fees (list[Fee], optional): Convenience array to apply fees onto the order. The fees will be deducted from the
                                        existing consideration items and then tacked on as new
                                        consideration items. Defaults to [].
            account_address (Optional[str], optional): Optional address for which to create the order with.
                                                       The account will be the first account from the provider if not specified.
            allow_partial_fills (bool, optional): Whether to allow the order to be partially filled. Defaults to False.
            restricted_by_zone (bool, optional): Whether the order should be restricted by zone. Defaults to False.
            salt (_type_, optional): Random salt. Defaults to a randomly generated salt.
            zone (str, optional): The zone of the order. Defaults to ADDRESS_ZERO.
            start_time (int, optional): The start time of the order in unix time. Defaults to the current time.
            end_time (int, optional): The end time of the order. Defaults to "never end".
                                      It is HIGHLY recommended to pass in an explicit end time

        Returns:
            CreateOrderUseCase: a use case containing the list of actions needed to be performed in order to create the order
        """
        offerer = account_address or self.web3.eth.accounts[0]
        offer_items = list(map(map_input_item_to_offer_item, offer))
        consideration_items = list(
            map(
                lambda c: ConsiderationItem(
                    **map_input_item_to_offer_item(c).dict(),
                    recipient=c.recipient or offerer,
                ),
                consideration,
            )
        )

        if not are_all_currencies_same(
            offer=offer_items, consideration=consideration_items
        ):
            raise ValueError("All currency tokens in the order must be the same token")

        currencies = list(
            filter(
                lambda item: is_currency_item(item.itemType),
                chain(offer_items, consideration_items),
            )
        )

        total_currency_start_amount, total_currency_end_amount = total_items_amount(
            currencies
        )

        proxy = self._get_legacy_conduit_proxy(
            address=offerer,
        )

        resolved_nonce = nonce or self.get_nonce(offerer=offerer)

        balances_and_approvals = get_balances_and_approvals(
            owner=offerer,
            items=offer_items,
            criterias=[],
            proxy=proxy,
            consideration_contract=self.contract,
            web3=self.web3,
        )

        insufficient_approval_amounts = get_insufficient_balance_and_approval_amounts(
            balances_and_approvals=balances_and_approvals,
            token_and_identifier_amounts=get_summed_token_and_identifier_amounts(
                items=offer_items,
                criterias=[],
            ),
            consideration_contract=self.contract,
            proxy=proxy,
            proxy_strategy=self.config.proxy_strategy,
        )

        use_proxy = use_proxy_from_approvals(
            insufficient_owner_approvals=insufficient_approval_amounts.insufficient_owner_approvals,
            insufficient_proxy_approvals=insufficient_approval_amounts.insufficient_proxy_approvals,
            proxy_strategy=self.config.proxy_strategy,
        )

        order_type = self._get_order_type_from_options(
            allow_partial_fills=allow_partial_fills,
            restricted_by_zone=restricted_by_zone,
        )

        consideration_items_with_fees = list(
            chain(
                deduct_fees(consideration_items, fees),
                list(
                    map(
                        lambda fee: fee_to_consideration_item(
                            fee=fee,
                            token=currencies[0].token,
                            base_amount=total_currency_start_amount,
                            base_end_amount=total_currency_end_amount,
                        ),
                        fees,
                    )
                    if currencies
                    else []
                ),
            )
        )

        conduit = LEGACY_PROXY_CONDUIT if use_proxy else NO_CONDUIT

        order_parameters = OrderParameters(
            offerer=offerer,
            zone=zone,
            startTime=start_time,
            endTime=end_time,
            orderType=order_type,
            offer=offer_items,
            consideration=consideration_items_with_fees,
            totalOriginalConsiderationItems=len(consideration_items_with_fees),
            # TODO: Placeholder
            zoneHash=bytes_to_hex(resolved_nonce.to_bytes(32, "little")),
            conduit=conduit,
            salt=salt,
        )

        check_balances_and_approvals = (
            self.config.balance_and_approval_checks_on_order_creation
        )

        insufficient_approvals = validate_offer_balances_and_approvals(
            offer=order_parameters.offer,
            conduit=order_parameters.conduit,
            criterias=[],
            balances_and_approvals=balances_and_approvals,
            throw_on_insufficient_balances=check_balances_and_approvals,
            consideration_contract=self.contract,
            proxy=proxy,
            proxy_strategy=self.config.proxy_strategy,
        )

        approval_actions = (
            get_approval_actions(
                insufficient_approvals=insufficient_approvals, web3=self.web3
            )
            if check_balances_and_approvals
            else []
        )

        def create_order_fn():
            signature = self.sign_order(
                order_parameters=order_parameters,
                nonce=resolved_nonce,
                account_address=offerer,
            )

            return CreatedOrder(
                parameters=order_parameters, nonce=resolved_nonce, signature=signature
            )

        create_order_action = CreateOrderAction(create_order=create_order_fn)

        actions = list(chain(approval_actions, [create_order_action]))

        return CreateOrderUseCase(
            actions=actions,
            execute_all_actions=lambda: cast(
                CreatedOrder, execute_all_actions(actions, {"from": offerer})
            ),
        )

    def sign_order(
        self,
        *,
        order_parameters: OrderParameters,
        nonce: int,
        account_address: str,
    ):
        domain_data = {
            "name": CONSIDERATION_CONTRACT_NAME,
            "version": CONSIDERATION_CONTRACT_VERSION,
            "chainId": self.web3.eth.chain_id,
            "verifyingContract": self.contract.address,
        }

        # We need to convert ints to str when signing due to limitations of certain RPC providers
        order_components = {
            **dict_int_to_str(order_parameters.dict()),
            "nonce": nonce,
            "offer": list(
                map(lambda x: dict_int_to_str(x.dict()), order_parameters.offer)
            ),
            "consideration": list(
                map(lambda x: dict_int_to_str(x.dict()), order_parameters.consideration)
            ),
        }

        payload = {
            "domain": domain_data,
            "message": order_components,
            "types": EIP_712_ORDER_TYPE,
            "primaryType": "OrderComponents",
        }

        # Default to using signTypedData_v4. If that's not possible, fallback to signTypedData
        response = self.web3.provider.make_request(
            RPCEndpoint("eth_signTypedData_v4"),
            [
                account_address or self.web3.eth.accounts[0],
                payload,
            ],
        )
        if "error" in response:
            response = self.web3.provider.make_request(
                RPCEndpoint("eth_signTypedData"),
                [
                    account_address or self.web3.eth.accounts[0],
                    payload,
                ],
            )

        if "result" not in response and "error" in response:
            raise ValueError(
                f"There was a problem generating the signature for the order: {response['error']}"
            )

        return response["result"]

    def cancel_orders(self, orders: list[OrderComponents]) -> TransactionMethods:
        """
        Cancels a list of orders so that they are no longer fulfillable.

        Args:
            orders (list[OrderComponents]): list of order components

        Returns:
            TransactionMethods: the set of transaction methods that can be used
        """
        return get_transaction_methods(
            self.contract.functions.cancel(parse_model_list(orders))
        )

    def bulk_cancel_orders(self) -> TransactionMethods:
        """
        Bulk cancels all existing orders for a given account

        Returns:
            TransactionMethods: set of transaction methods that can be used
        """
        return get_transaction_methods(self.contract.functions.incrementNonce)

    def approve_orders(self, orders: list[Order]) -> TransactionMethods:
        """
        Approves a list of orders on-chain. This allows accounts to fulfill the order without requiring
        a signature

        Args:
            orders (list[Order]): list of order models

        Returns:
            TransactionMethods: set of transaction methods that can be used
        """
        return get_transaction_methods(
            self.contract.functions.validate(parse_model_list(orders))
        )

    def get_order_status(self, order_hash: str) -> OrderStatus:
        """
        Returns the order status given an order hash

        Args:
            order_hash (str): the hash of the order

        Returns:
            OrderStatus: order status model
        """
        (
            is_validated,
            is_cancelled,
            total_filled,
            total_size,
        ) = self.contract.functions.getOrderStatus(order_hash).call()

        return OrderStatus(
            is_validated=is_validated,
            is_cancelled=is_cancelled,
            total_filled=total_filled,
            total_size=total_size,
        )

    def get_nonce(self, offerer: str) -> int:
        """
        Gets the nonce of a given offerer

        Args:
            offerer (str): the offerer to get the nonce of

        Returns:
            int: nonce
        """
        return self.contract.functions.getNonce(offerer).call()

    def get_order_hash(self, order_components: OrderComponents) -> str:
        """
        Calculates the order hash of order components so we can forgo executing a request to the contract
        This saves us RPC calls and latency.

        Args:
            order_components (OrderComponents): order components model

        Returns:
            str: the order hash
        """
        offer_item_type_string = "OfferItem(uint8 itemType,address token,uint256 identifierOrCriteria,uint256 startAmount,uint256 endAmount)"
        consideration_item_type_string = "ConsiderationItem(uint8 itemType,address token,uint256 identifierOrCriteria,uint256 startAmount,uint256 endAmount,address recipient)"
        order_components_partial_type_str = "OrderComponents(address offerer,address zone,OfferItem[] offer,ConsiderationItem[] consideration,uint8 orderType,uint256 startTime,uint256 endTime,uint256 salt,uint256 nonce)"
        order_type_str = f"{order_components_partial_type_str}{consideration_item_type_string}{offer_item_type_string}"
        offer_item_type_hash = Web3.solidityKeccak(
            abi_types=["bytes"], values=[offer_item_type_string.encode("utf-8")]
        ).hex()
        consideration_item_type_hash = Web3.solidityKeccak(
            abi_types=["bytes"], values=[offer_item_type_string.encode("utf-8")]
        ).hex()
        order_type_hash = Web3.solidityKeccak(
            abi_types=["bytes"], values=[order_type_str.encode("utf-8")]
        ).hex()

        offer_hash = Web3.solidityKeccak(
            abi_types=["bytes"],
            values=[
                "0x"
                + "".join(
                    map(
                        lambda item: Web3.solidityKeccak(
                            abi_types=["bytes"],
                            values=[
                                "0x"
                                + "".join(
                                    [
                                        offer_item_type_hash[2:],
                                        str(item.itemType).zfill(64),
                                        item.token[2:].zfill(64),
                                        hex(item.identifierOrCriteria)[2:].zfill(64),
                                        hex(item.startAmount)[2:].zfill(64),
                                        hex(item.endAmount)[2:].zfill(64),
                                    ]
                                )
                            ],
                        ).hex()[2:],
                        order_components.offer,
                    )
                )
            ],
        ).hex()

        consideration_hash = Web3.solidityKeccak(
            abi_types=["bytes"],
            values=[
                "0x"
                + "".join(
                    map(
                        lambda item: Web3.solidityKeccak(
                            abi_types=["bytes"],
                            values=[
                                "0x"
                                + "".join(
                                    [
                                        consideration_item_type_hash[2:],
                                        str(item.itemType).zfill(64),
                                        item.token[2:].zfill(64),
                                        hex(item.identifierOrCriteria)[2:].zfill(64),
                                        hex(item.startAmount)[2:].zfill(64),
                                        hex(item.endAmount)[2:].zfill(64),
                                        item.recipient[2:].zfill(64),
                                    ]
                                )
                            ],
                        ).hex()[2:],
                        order_components.consideration,
                    )
                )
            ],
        ).hex()

        derived_order_hash = Web3.solidityKeccak(
            abi_types=["bytes"],
            values=[
                "0x"
                + "".join(
                    [
                        order_type_hash[2:],
                        order_components.offerer[2:].zfill(64),
                        order_components.zone[2:].zfill(64),
                        offer_hash[2:],
                        consideration_hash[2:],
                        str(order_components.orderType).zfill(64),
                        hex(order_components.startTime)[2:].zfill(64),
                        hex(order_components.endTime)[2:].zfill(64),
                        hex(order_components.salt)[2:].zfill(64),
                        hex(order_components.nonce)[2:].zfill(64),
                    ]
                )
            ],
        )

        return derived_order_hash.hex()

    def fulfill_order(
        self,
        *,
        order: Order,
        units_to_fill: Optional[int] = None,
        offer_criteria: list[InputCriteria] = [],
        consideration_criteria: list[InputCriteria] = [],
        tips: list[ConsiderationInputItem] = [],
        extra_data: Optional[str] = "0x",
        account_address: Optional[str] = None,
    ) -> FulfillOrderUseCase:
        """
        Fulfills an order through either the basic method or the standard method
        Units to fill are denominated by the max possible size of the order, which is the greatest common denominator (GCD).
        We expose a helper to get this: getMaximumSizeForOrder
        i.e. If the maximum size of an order is 4, supplying 2 as the units to fulfill will fill half of the order

        Args:
            order (Order): standard order struct
            units_to_fill (Optional[int], optional): the number of units to fill for the given order. Only used if you wish to partially fill an order
            offer_criteria (list[InputCriteria], optional): an array of criteria with length equal to the number of offer criteria items. Defaults to [].
            consideration_criteria (list[InputCriteria], optional): an array of criteria with length equal to the number of consideration criteria items. Defaults to [].
            tips (list[ConsiderationInputItem], optional): an array of optional condensed consideration items to be added onto a fulfillment. Defaults to [].
            extra_data (Optional[str], optional): extra data supplied to the order. Defaults to None.
            extra_data (Optional[str], optional): extra data supplied to the order. Defaults to None.
        """
        fulfiller = account_address or self.web3.eth.accounts[0]
        offerer = order.parameters.offerer
        offerer_proxy = self._get_legacy_conduit_proxy(offerer)
        fulfiller_proxy = self._get_legacy_conduit_proxy(fulfiller)
        nonce = self.get_nonce(offerer)

        offerer_balances_and_approvals = get_balances_and_approvals(
            owner=offerer,
            items=order.parameters.offer,
            criterias=offer_criteria,
            proxy=offerer_proxy,
            consideration_contract=self.contract,
            web3=self.web3,
        )

        # Get fulfiller balances and approvals of all items in the set, as offer items
        # may be received by the fulfiller for standard fulfills
        fulfiller_balances_and_approvals = get_balances_and_approvals(
            owner=fulfiller,
            items=list(chain(order.parameters.offer, order.parameters.consideration)),
            criterias=list(chain(offer_criteria, consideration_criteria)),
            proxy=fulfiller_proxy,
            consideration_contract=self.contract,
            web3=self.web3,
        )

        current_block = self.web3.eth.get_block("latest")
        order_status = self.get_order_status(
            self.get_order_hash(OrderComponents(**order.parameters.dict(), nonce=nonce))
        )

        current_block_timestamp = current_block.get("timestamp", int(time()))
        sanitized_order = validate_and_sanitize_from_order_status(order, order_status)
        time_based_item_params = TimeBasedItemParams(
            start_time=sanitized_order.parameters.startTime,
            end_time=sanitized_order.parameters.endTime,
            current_block_timestamp=current_block_timestamp,
            ascending_amount_timestamp_buffer=self.config.ascending_amount_fulfillment_buffer,
        )
        tip_consideration_items = list(
            map(
                lambda tip: ConsiderationItem(
                    **map_input_item_to_offer_item(tip).dict(),
                    recipient=tip.recipient or offerer,
                ),
                tips,
            )
        )

        if not units_to_fill and should_use_basic_fulfill(
            sanitized_order.parameters, order_status.total_filled
        ):
            return fulfill_basic_order(
                order=sanitized_order,
                consideration_contract=self.contract,
                offerer_balances_and_approvals=offerer_balances_and_approvals,
                fulfiller_balances_and_approvals=fulfiller_balances_and_approvals,
                time_based_item_params=time_based_item_params,
                offerer_proxy=offerer_proxy,
                fulfiller_proxy=fulfiller_proxy,
                fulfiller=fulfiller,
                proxy_strategy=self.config.proxy_strategy,
                tips=tip_consideration_items,
                web3=self.web3,
            )
        return FulfillOrderUseCase(actions=[], execute_all_actions=lambda: HexBytes(1))
