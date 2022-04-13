from typing import Optional

from web3 import Web3
from consideration.abi.ERC1155 import ERC1155_ABI
from consideration.abi.ERC20 import ERC20_ABI
from consideration.abi.ERC721 import ERC721_ABI
from consideration.constants import ItemType
from consideration.types import InputCriteria, Item
from consideration.utils.item import is_erc1155_item, is_erc20_item, is_erc721_item


def balance_of(
    owner: str, item: Item, criteria: Optional[InputCriteria], web3: Web3
) -> int:
    if is_erc721_item(item.itemType):
        contract = web3.eth.contract(
            address=Web3.toChecksumAddress(item.token), abi=ERC721_ABI
        )

        if item.itemType == ItemType.ERC721_WITH_CRITERIA:
            if criteria:
                owner_of: str = contract.functions.ownerOf(criteria.identifier).call()
                return 1 if owner_of.lower() == owner.lower() else 0

            return contract.functions.balanceOf(owner).call()

        owner_of: str = contract.functions.ownerOf(item.identifierOrCriteria).call()
        return 1 if owner_of.lower() == owner.lower() else 0
    elif is_erc1155_item(item.itemType):
        contract = web3.eth.contract(
            address=Web3.toChecksumAddress(item.token), abi=ERC1155_ABI
        )

        if item.itemType == ItemType.ERC1155_WITH_CRITERIA:
            if not criteria:
                # We don't have a good way to determine the balance of an erc1155 criteria item unless explicit
                # identifiers are provided, so just assume the offerer has sufficient balance
                return max(item.startAmount, item.endAmount)

            return contract.functions.balanceOf(owner, criteria.identifier).call()

        return contract.functions.balanceOf(owner, item.identifierOrCriteria).call()

    if is_erc20_item(item.itemType):
        contract = web3.eth.contract(
            address=Web3.toChecksumAddress(item.token), abi=ERC20_ABI
        )
        return contract.functions.balanceOf(owner).call()

    return web3.eth.get_balance(owner)
