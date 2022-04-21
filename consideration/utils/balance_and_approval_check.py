from typing import Literal, Optional, Sequence, Union
from pydantic import BaseModel
from web3 import Web3
from web3.contract import Contract
from web3.constants import ADDRESS_ZERO
from consideration.abi.ERC20 import ERC20_ABI
from consideration.abi.ERC721 import ERC721_ABI
from consideration.types import ApprovalAction, Item, TransactionMethods


from consideration.constants import (
    LEGACY_PROXY_CONDUIT,
    MAX_INT,
    ProxyStrategy,
)
from consideration.types import (
    BalanceAndApproval,
    BalancesAndApprovals,
    ConsiderationItem,
    InputCriteria,
    InsufficientApproval,
    InsufficientApprovals,
    InsufficientBalance,
    InsufficientBalances,
    Item,
    OfferItem,
)
from consideration.utils.balance import balance_of
from consideration.utils.item import (
    TimeBasedItemParams,
    TokenAndIdentifierAmounts,
    get_summed_token_and_identifier_amounts,
    is_erc1155_item,
    is_erc20_item,
    is_erc721_item,
    get_item_index_to_criteria_map,
)
from consideration.utils.usecase import get_transaction_methods


def approved_item_amount(owner: str, item: Item, operator: str, web3: Web3) -> int:
    if is_erc721_item(item.itemType) or is_erc1155_item(item.itemType):
        contract = web3.eth.contract(
            address=web3.toChecksumAddress(item.token), abi=ERC721_ABI
        )

        is_approved_for_all = contract.functions.isApprovedForAll(
            owner, operator
        ).call()

        return MAX_INT if is_approved_for_all else 0
    elif is_erc20_item(item.itemType):
        contract = web3.eth.contract(
            address=web3.toChecksumAddress(item.token), abi=ERC20_ABI
        )

        return contract.functions.allowance(owner, operator).call()

    # We don't need to check approvals for native tokens
    return MAX_INT


def get_approval_actions(
    insufficient_approvals: InsufficientApprovals,
    web3: Web3,
    account_address: Optional[str] = None,
) -> list[ApprovalAction]:
    from_account = account_address or web3.eth.accounts[0]

    def map_insufficient_approval_to_action(
        insufficient_approval: InsufficientApproval,
    ):

        if is_erc721_item(insufficient_approval.item_type) or is_erc1155_item(
            insufficient_approval.item_type
        ):
            # setApprovalForAllCheck is the same for both ERC721 and ERC1155, defaulting to ERC721
            contract = web3.eth.contract(
                address=Web3.toChecksumAddress(insufficient_approval.token),
                abi=ERC721_ABI,
            )

            contract_fn = contract.functions.setApprovalForAll(
                insufficient_approval.operator, True
            )

        else:
            contract = web3.eth.contract(
                address=Web3.toChecksumAddress(insufficient_approval.token),
                abi=ERC20_ABI,
            )

            contract_fn = contract.functions.approve(
                insufficient_approval.operator, MAX_INT
            )

        return ApprovalAction(
            token=insufficient_approval.token,
            identifier_or_criteria=insufficient_approval.identifier_or_criteria,
            item_type=insufficient_approval.item_type,
            operator=insufficient_approval.operator,
            transaction_methods=get_transaction_methods(
                contract_fn, {"from": from_account}
            ),
        )

    return list(map(map_insufficient_approval_to_action, insufficient_approvals))


def find_balance_and_approval(
    balances_and_approvals: BalancesAndApprovals,
    token: str,
    identifier_or_criteria: int,
) -> BalanceAndApproval:
    for balance_and_approval in balances_and_approvals:
        if (
            token.lower() == balance_and_approval.token.lower()
            and identifier_or_criteria == balance_and_approval.identifier_or_criteria
        ):
            return balance_and_approval

    raise ValueError("Balances and approvals didn't contain all tokens and identifiers")


def get_balances_and_approvals(
    *,
    owner: str,
    items: Sequence[Item],
    criterias: list[InputCriteria],
    proxy: str,
    consideration_contract: Contract,
    web3: Web3,
):
    item_index_to_criteria = get_item_index_to_criteria_map(
        items=items, criterias=criterias
    )

    def map_item_to_balances_and_approval(index_and_item: tuple[int, Item]):
        index, item = index_and_item
        owner_approved_amount = 0
        proxy_approved_amount = 0

        # If erc721 or erc1155 check both consideration and proxy approvals unless config says ignore proxy
        if is_erc721_item(item.itemType) or is_erc1155_item(item.itemType):
            owner_approved_amount = approved_item_amount(
                owner=owner,
                item=item,
                operator=consideration_contract.address,
                web3=web3,
            )

            if proxy != ADDRESS_ZERO:
                proxy_approved_amount = approved_item_amount(
                    owner=owner,
                    item=item,
                    operator=proxy,
                    web3=web3,
                )
        # If erc20 check just consideration contract for approvals
        elif is_erc20_item(item.itemType):
            owner_approved_amount = approved_item_amount(
                owner=owner,
                item=item,
                operator=consideration_contract.address,
                web3=web3,
            )
            # There technically is no proxy approved amount for ERC-20s.
            # Making it the same as the owner approved amount except changing the operator
            # to be the consideration contract
            proxy_approved_amount = owner_approved_amount
        else:
            # If native token, we don't need to check for approvals
            owner_approved_amount = MAX_INT
            proxy_approved_amount = MAX_INT

        return BalanceAndApproval(
            token=item.token,
            identifier_or_criteria=item_index_to_criteria[index].identifier
            if index in item_index_to_criteria
            else item.identifierOrCriteria,
            balance=balance_of(
                owner=owner,
                item=item,
                criteria=item_index_to_criteria.get(index),
                web3=web3,
            ),
            owner_approved_amount=owner_approved_amount,
            proxy_approved_amount=proxy_approved_amount,
            item_type=item.itemType,
        )

    return list(map(map_item_to_balances_and_approval, enumerate(items)))


class InsufficientBalanceAndApprovalAmounts(BaseModel):
    insufficient_balances: InsufficientBalances
    insufficient_owner_approvals: InsufficientApprovals
    insufficient_proxy_approvals: InsufficientApprovals


def get_insufficient_balance_and_approval_amounts(
    *,
    balances_and_approvals: BalancesAndApprovals,
    token_and_identifier_amounts: TokenAndIdentifierAmounts,
    proxy: str,
    proxy_strategy: ProxyStrategy,
    consideration_contract: Contract,
):
    token_and_identifier_and_amount_needed: list[tuple[str, int, int]] = []

    for token, identifier_to_amount in token_and_identifier_amounts.items():
        for identifier_or_criteria, amount_needed in identifier_to_amount.items():
            token_and_identifier_and_amount_needed.append(
                (token, identifier_or_criteria, amount_needed)
            )

    def filter_balances_or_approvals(
        filter_key: Union[
            Literal["balance"],
            Literal["owner_approved_amount"],
            Literal["proxy_approved_amount"],
        ]
    ):
        def filter_balance_or_approval(
            token_and_identifier_and_amount_needed: tuple[str, int, int]
        ):
            (
                token,
                identifier_or_criteria,
                amount_needed,
            ) = token_and_identifier_and_amount_needed

            amount: int = find_balance_and_approval(
                balances_and_approvals=balances_and_approvals,
                token=token,
                identifier_or_criteria=identifier_or_criteria,
            ).dict()[filter_key]

            return amount < amount_needed

        def map_to_balance(
            token_and_identifier_and_amount_needed: tuple[str, int, int]
        ) -> InsufficientBalance:
            (
                token,
                identifier_or_criteria,
                amount_needed,
            ) = token_and_identifier_and_amount_needed

            balance_and_approval = find_balance_and_approval(
                balances_and_approvals=balances_and_approvals,
                token=token,
                identifier_or_criteria=identifier_or_criteria,
            )

            return InsufficientBalance(
                token=token,
                identifier_or_criteria=identifier_or_criteria,
                required_amount=amount_needed,
                amount_have=balance_and_approval.dict()[filter_key],
                item_type=balance_and_approval.item_type,
            )

        return list(
            map(
                map_to_balance,
                filter(
                    filter_balance_or_approval, token_and_identifier_and_amount_needed
                ),
            )
        )

    def map_to_approval(insufficient_balance: InsufficientBalance):
        return InsufficientApproval(
            token=insufficient_balance.token,
            identifier_or_criteria=insufficient_balance.identifier_or_criteria,
            approved_amount=insufficient_balance.amount_have,
            required_approved_amount=insufficient_balance.required_amount,
            item_type=insufficient_balance.item_type,
            operator="",
        )

    (
        insufficient_balances,
        insufficient_owner_approvals,
        insufficient_proxy_approvals,
    ) = (
        filter_balances_or_approvals("balance"),
        list(
            map(map_to_approval, filter_balances_or_approvals("owner_approved_amount"))
        ),
        list(
            map(map_to_approval, filter_balances_or_approvals("proxy_approved_amount"))
        ),
    )

    def map_operator(
        insufficient_approval: InsufficientApproval,
    ) -> InsufficientApproval:
        # We always use the consideration contract as the operator for ERC-20s
        if is_erc20_item(insufficient_approval.item_type):
            operator = consideration_contract.address
        else:
            operator = (
                proxy
                if use_proxy_from_approvals(
                    insufficient_owner_approvals=insufficient_owner_approvals,
                    insufficient_proxy_approvals=insufficient_proxy_approvals,
                    proxy_strategy=proxy_strategy,
                )
                else consideration_contract.address
            )

        return insufficient_approval.copy(update={"operator": operator})

    return InsufficientBalanceAndApprovalAmounts(
        insufficient_balances=insufficient_balances,
        insufficient_owner_approvals=list(
            map(map_operator, insufficient_owner_approvals)
        ),
        insufficient_proxy_approvals=list(
            map(map_operator, insufficient_proxy_approvals)
        ),
    )


# 1. The offerer should have sufficient balance of all offered items.
# 2. If the order does not indicate proxy utilization, the offerer should have sufficient approvals set
#    for the Consideration contract for all offered ERC20, ERC721, and ERC1155 items.
# 3. If the order does indicate proxy utilization, the offerer should have sufficient approvals set
#    for their respective proxy contract for all offered ERC20, ERC721, and ERC1155 items.
def validate_offer_balances_and_approvals(
    *,
    offer: list[OfferItem],
    conduit: str,
    criterias: list[InputCriteria],
    balances_and_approvals: BalancesAndApprovals,
    time_based_item_params: Optional[TimeBasedItemParams] = None,
    consideration_contract: Contract,
    proxy: str,
    proxy_strategy: ProxyStrategy,
    throw_on_insufficient_balances=True,
    throw_on_insufficient_approvals=False,
):
    insufficient_balance_and_approval_amounts = (
        get_insufficient_balance_and_approval_amounts(
            balances_and_approvals=balances_and_approvals,
            token_and_identifier_amounts=get_summed_token_and_identifier_amounts(
                items=offer,
                criterias=criterias,
                time_based_item_params=time_based_item_params.copy(
                    update={"is_consideration_item": False}
                )
                if time_based_item_params
                else None,
            ),
            consideration_contract=consideration_contract,
            proxy=proxy,
            proxy_strategy=proxy_strategy,
        )
    )

    if (
        throw_on_insufficient_balances
        and insufficient_balance_and_approval_amounts.insufficient_balances
    ):
        raise ValueError(
            "The offerer does not have the amount needed to create or fulfill."
        )

    approvals_to_check = (
        insufficient_balance_and_approval_amounts.insufficient_proxy_approvals
        if use_offerer_proxy(conduit)
        else insufficient_balance_and_approval_amounts.insufficient_owner_approvals
    )

    if throw_on_insufficient_approvals and len(approvals_to_check) > 0:
        raise ValueError("The offerer does not have the sufficient approvals.")

    return approvals_to_check


# When fulfilling a basic order, the following requirements need to be checked to ensure that the order will be fulfillable:
# 1. Offer checks need to be performed to ensure that the offerer still has sufficient balance and approvals
# 2. The fulfiller should have sufficient balance of all consideration items except for those with an
#    item type that matches the order's offered item type — by way of example, if the fulfilled order offers
#    an ERC20 item and requires an ERC721 item to the offerer and the same ERC20 item to another recipient,
#    the fulfiller needs to own the ERC721 item but does not need to own the ERC20 item as it will be sourced from the offerer.
# 3. If the fulfiller does not elect to utilize a proxy, they need to have sufficient approvals set for the
#    Consideration contract for all ERC20, ERC721, and ERC1155 consideration items on the fulfilled order except
#    for ERC20 items with an item type that matches the order's offered item type.
# 4. If the fulfiller does elect to utilize a proxy, they need to have sufficient approvals set for their
#    respective proxy contract for all ERC20, ERC721, and ERC1155 consideration items on the fulfilled order
#    except for ERC20 items with an item type that matches the order's offered item type.
# 5. If the fulfilled order specifies Ether (or other native tokens) as consideration items, the fulfiller must
#    be able to supply the sum total of those items as msg.value.
def validate_basic_fulfill_balances_and_approvals(
    *,
    offer: list[OfferItem],
    conduit: str,
    consideration: list[ConsiderationItem],
    offerer_balances_and_approvals: BalancesAndApprovals,
    fulfiller_balances_and_approvals: BalancesAndApprovals,
    time_based_item_params: Optional[TimeBasedItemParams],
    consideration_contract: Contract,
    offerer_proxy: str,
    fulfiller_proxy: str,
    proxy_strategy: ProxyStrategy,
):
    validate_offer_balances_and_approvals(
        offer=offer,
        conduit=conduit,
        criterias=[],
        balances_and_approvals=offerer_balances_and_approvals,
        time_based_item_params=time_based_item_params,
        throw_on_insufficient_approvals=True,
        consideration_contract=consideration_contract,
        proxy=offerer_proxy,
        proxy_strategy=proxy_strategy,
    )

    consideration_without_offer_item_type = list(
        filter(lambda x: x.itemType != offer[0].itemType, consideration)
    )

    insufficient_balance_and_approval_amounts = (
        get_insufficient_balance_and_approval_amounts(
            balances_and_approvals=fulfiller_balances_and_approvals,
            token_and_identifier_amounts=get_summed_token_and_identifier_amounts(
                items=consideration_without_offer_item_type,
                criterias=[],
                time_based_item_params=time_based_item_params.copy(
                    update={"is_consideration_item": True}
                )
                if time_based_item_params
                else None,
            ),
            consideration_contract=consideration_contract,
            proxy=fulfiller_proxy,
            proxy_strategy=proxy_strategy,
        )
    )

    if insufficient_balance_and_approval_amounts.insufficient_balances:
        raise ValueError("The fulfiller does not have the balances needed to fulfill")

    return insufficient_balance_and_approval_amounts


# When fulfilling a standard order, the following requirements need to be checked to ensure that the order will be fulfillable:
# 1. Offer checks need to be performed to ensure that the offerer still has sufficient balance and approvals
# 2. The fulfiller should have sufficient balance of all consideration items after receiving all offered items
#    — by way of example, if the fulfilled order offers an ERC20 item and requires an ERC721 item to the offerer
#    and the same ERC20 item to another recipient with an amount less than or equal to the offered amount,
#    the fulfiller does not need to own the ERC20 item as it will first be received from the offerer.
# 3. If the fulfiller does not elect to utilize a proxy, they need to have sufficient approvals set for the
#    Consideration contract for all ERC20, ERC721, and ERC1155 consideration items on the fulfilled order.
# 4. If the fulfiller does elect to utilize a proxy, they need to have sufficient approvals set for their
#    respective proxy contract for all ERC20, ERC721, and ERC1155 consideration items on the fulfilled order.
# 5. If the fulfilled order specifies Ether (or other native tokens) as consideration items, the fulfiller must
#    be able to supply the sum total of those items as msg.value.
def validate_standard_fulfill_balances_and_approvals(
    *,
    offer: list[OfferItem],
    conduit: str,
    consideration: list[ConsiderationItem],
    offer_criteria: list[InputCriteria],
    consideration_criteria: list[InputCriteria],
    offerer_balances_and_approvals: BalancesAndApprovals,
    fulfiller_balances_and_approvals: BalancesAndApprovals,
    time_based_item_params: Optional[TimeBasedItemParams],
    consideration_contract: Contract,
    proxy: str,
    proxy_strategy: ProxyStrategy,
):
    validate_offer_balances_and_approvals(
        offer=offer,
        conduit=conduit,
        criterias=[],
        balances_and_approvals=offerer_balances_and_approvals,
        time_based_item_params=time_based_item_params,
        throw_on_insufficient_approvals=True,
        consideration_contract=consideration_contract,
        proxy=proxy,
        proxy_strategy=proxy_strategy,
    )

    summed_offer_amounts = get_summed_token_and_identifier_amounts(
        items=offer,
        criterias=offer_criteria,
        time_based_item_params=time_based_item_params.copy(
            update={"is_consideration_item": False}
        )
        if time_based_item_params
        else None,
    )

    # Deep clone existing balances
    fulfiller_balances_and_approvals_after_receiving_offered_items = list(
        map(lambda x: x.copy(), fulfiller_balances_and_approvals)
    )

    for token, identifier_or_criteria_to_amount in summed_offer_amounts.items():
        for identifier_or_criteria, amount in identifier_or_criteria_to_amount.items():
            balance_and_approval = find_balance_and_approval(
                balances_and_approvals=fulfiller_balances_and_approvals_after_receiving_offered_items,
                token=token,
                identifier_or_criteria=identifier_or_criteria,
            )

            balance_and_approval_index = (
                fulfiller_balances_and_approvals_after_receiving_offered_items.index(
                    balance_and_approval
                )
            )

            fulfiller_balances_and_approvals_after_receiving_offered_items[
                balance_and_approval_index
            ].balance += amount

    insufficient_balance_and_approval_amounts = get_insufficient_balance_and_approval_amounts(
        balances_and_approvals=fulfiller_balances_and_approvals_after_receiving_offered_items,
        token_and_identifier_amounts=get_summed_token_and_identifier_amounts(
            items=consideration,
            criterias=consideration_criteria,
            time_based_item_params=time_based_item_params.copy(
                update={"is_consideration_item": True}
            )
            if time_based_item_params
            else None,
        ),
        consideration_contract=consideration_contract,
        proxy=proxy,
        proxy_strategy=proxy_strategy,
    )

    if insufficient_balance_and_approval_amounts.insufficient_balances:
        raise ValueError("The fulfiller does not have the balances needed to fulfill.")

    return insufficient_balance_and_approval_amounts


def use_offerer_proxy(conduit: str):
    return conduit == LEGACY_PROXY_CONDUIT


def use_proxy_from_approvals(
    insufficient_owner_approvals: InsufficientApprovals,
    insufficient_proxy_approvals: InsufficientApprovals,
    proxy_strategy: ProxyStrategy,
):
    if proxy_strategy == ProxyStrategy.IF_ZERO_APPROVALS_NEEDED:
        return (
            len(insufficient_proxy_approvals) < len(insufficient_owner_approvals)
            and len(insufficient_owner_approvals) != 0
        )
    return proxy_strategy == ProxyStrategy.ALWAYS
