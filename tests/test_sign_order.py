from brownie.network.account import Accounts
from web3 import Web3
from web3.constants import ADDRESS_ZERO

from consideration.consideration import Consideration
from consideration.constants import MAX_INT, ItemType, OrderType
from consideration.types import ConsiderationItem, OfferItem, OrderParameters
from consideration.utils.hex_utils import bytes_to_hex
from consideration.utils.order import generate_random_salt


def test_valid_order(
    consideration: Consideration,
    erc721,
    accounts: Accounts,
):
    offerer, zone, random_signer, *_ = accounts

    start_time = 0
    end_time = MAX_INT
    salt = generate_random_salt()

    offer: list[OfferItem] = [
        OfferItem(
            itemType=ItemType.ERC721,
            token=erc721.address,
            identifierOrCriteria=0,
            startAmount=1,
            endAmount=1,
        )
    ]

    consideration_items: list[ConsiderationItem] = [
        ConsiderationItem(
            itemType=ItemType.NATIVE,
            token=ADDRESS_ZERO,
            identifierOrCriteria=0,
            startAmount=Web3.toWei("10", "ether"),
            endAmount=Web3.toWei("10", "ether"),
            recipient=offerer.address,
        ),
        ConsiderationItem(
            itemType=ItemType.NATIVE,
            token=ADDRESS_ZERO,
            identifierOrCriteria=0,
            startAmount=Web3.toWei("1", "ether"),
            endAmount=Web3.toWei("1", "ether"),
            recipient=zone.address,
        ),
    ]

    nonce = consideration.get_nonce(offerer.address)

    order_parameters = OrderParameters(
        offerer=offerer.address,
        zone=ADDRESS_ZERO,
        offer=offer,
        consideration=consideration_items,
        orderType=OrderType.FULL_OPEN,
        totalOriginalConsiderationItems=len(consideration_items),
        salt=salt,
        startTime=start_time,
        endTime=end_time,
        zoneHash=bytes_to_hex(nonce.to_bytes(32, "little")),
        conduit=ADDRESS_ZERO,
    )

    signature = consideration.sign_order(
        order_parameters=order_parameters, nonce=nonce, account_address=offerer.address
    )

    order = {
        "parameters": {
            **order_parameters.dict(),
        },
        "signature": signature,
    }

    # Use a random address to verify that the signature is valid
    is_valid = consideration.contract.functions.validate([order]).call(
        {"from": random_signer.address}
    )

    assert is_valid == True
