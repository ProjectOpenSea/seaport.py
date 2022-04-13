from secrets import token_hex
from consideration.constants import ItemType
from typing import cast, Union
from consideration.types import (
    BasicErc1155Item,
    BasicErc721Item,
    CreateInputItem,
    CurrencyItem,
    Erc1155Item,
    Erc1155ItemWithCriteria,
    Erc721Item,
    Erc721ItemWithCriteria,
    OfferItem,
)
from web3.constants import ADDRESS_ZERO


def map_input_item_to_offer_item(item: CreateInputItem) -> OfferItem:
    # Item is an NFT
    if "item_type" in item:
        # Convert this into a criteria based item
        if "identifiers" in item:
            item = cast(Union[Erc721ItemWithCriteria, Erc1155ItemWithCriteria], item)
            return OfferItem(
                itemType=ItemType.ERC721_WITH_CRITERIA
                if item["item_type"] == ItemType.ERC721
                else ItemType.ERC1155_WITH_CRITERIA,
                token=item["token"],
                identifierOrCriteria=0,
                startAmount=item.get("amount", 1),
                endAmount=item.get("endAmount", item.get("amount", 1)),
            )

        if "amount" in item or "end_amount" in item:
            item = cast(Union[BasicErc721Item, BasicErc1155Item], item)
            return OfferItem(
                itemType=item["item_type"],
                token=item["token"],
                identifierOrCriteria=item["identifier"],
                startAmount=item.get("amount", 1),
                endAmount=item.get("endAmount", item.get("amount", 1)),
            )

        return OfferItem(
            itemType=item["item_type"],
            token=item["token"],
            identifierOrCriteria=item["identifier"],
            startAmount=1,
            endAmount=1,
        )

    # Item is a currency
    item = cast(CurrencyItem, item)

    return OfferItem(
        itemType=ItemType.ERC20
        if "token" in item and item["token"] != ADDRESS_ZERO
        else ItemType.NATIVE,
        token=item["token"] or ADDRESS_ZERO,
        identifierOrCriteria=0,
        startAmount=item["amount"],
        endAmount=item.get("end_amount", item["amount"]),
    )


def generate_random_salt():
    return int(token_hex(32), 16)
