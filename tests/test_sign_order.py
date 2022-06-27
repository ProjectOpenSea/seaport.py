from brownie.network.account import Accounts
from web3 import Web3
from web3.constants import ADDRESS_ZERO

from seaport.constants import MAX_INT, NO_CONDUIT_KEY, ItemType, OrderType
from seaport.seaport import Seaport
from seaport.types import ConsiderationItem, OfferItem, OrderParameters
from seaport.utils.hex_utils import bytes_to_hex
from seaport.utils.order import generate_random_salt


def test_valid_order(
    seaport: Seaport,
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

    counter = seaport.get_counter(offerer.address)

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
        zoneHash=bytes_to_hex(counter.to_bytes(32, "little")),
        conduitKey=NO_CONDUIT_KEY,
    )

    signature = seaport.sign_order(
        order_parameters=order_parameters,
        counter=counter,
        account_address=offerer.address,
    )

    order = {
        "parameters": {
            **order_parameters.dict(),
        },
        "signature": signature,
    }

    # Use a random address to verify that the signature is valid
    is_valid = seaport.contract.functions.validate([order]).call(
        {"from": random_signer.address}
    )

    assert is_valid == True
