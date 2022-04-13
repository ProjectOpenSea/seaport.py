from urllib.parse import MAX_CACHE_SIZE
from brownie import ZERO_ADDRESS, Contract
from pydantic import BaseModel
from web3 import Web3
from consideration.constants import MAX_INT, ItemType
from consideration.types import InputCriteria, Item
from consideration.utils.approval import approved_item_amount
from consideration.utils.criteria import get_item_index_to_criteria_map
from consideration.utils.item import is_erc1155_item, is_erc20_item, is_erc721_item


class BalanceAndApproval(BaseModel):
    token: str
    identifier_or_criteria: str
    balance: int
    owner_approved_amount: int
    proxy_approved_amount: int
    item_type: ItemType


BalancesAndApprovals = list[BalanceAndApproval]


class InsufficientBalance(BaseModel):
    token: str
    identifier_or_criteria: str
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
    owner: str,
    items: list[Item],
    criterias: list[InputCriteria],
    proxy: str,
    consideration_contract: Contract,
    web3: Web3,
):
    item_index_to_criteria = get_item_index_to_criteria_map(
        items=items, criterias=criterias
    )

    def map_item_to_balances_and_approval(item: Item):
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

            if proxy != ZERO_ADDRESS:
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
