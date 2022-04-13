from web3 import Web3
from consideration.abi.ERC20 import ERC20_ABI
from consideration.abi.ERC721 import ERC721_ABI
from consideration.constants import MAX_INT
from consideration.types import ApprovalAction, Item, Transaction
from consideration.utils.balance_and_approval_check import (
    InsufficientApproval,
    InsufficientApprovals,
)
from consideration.utils.item import is_erc1155_item, is_erc20_item, is_erc721_item


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
    insufficient_approvals: InsufficientApprovals, web3: Web3
) -> list[ApprovalAction]:
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
            transaction=Transaction(
                transact=contract_fn.transact,
                build_transaction=contract_fn.buildTransaction,
            ),
        )

    return list(map(map_insufficient_approval_to_action, insufficient_approvals))
