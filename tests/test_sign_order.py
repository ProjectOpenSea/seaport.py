from brownie.network.account import Accounts
from consideration.consideration import Consideration

from consideration.constants import MAX_INT, ItemType, OrderType
from consideration.types import ConsiderationItem, OfferItem, OrderParameters
from consideration.utils.order import generate_random_salt
from web3.constants import ADDRESS_ZERO
from web3.contract import Contract
from web3 import Web3

from consideration.utils.pydantic import to_struct


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
            recipient=zone.address,
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
    )

    nonce = consideration.get_nonce(offerer.address, zone.address)

    assert nonce == 0

    # signature = consideration.sign_order(
    #     order_parameters=order_parameters, nonce=nonce, account_address=offerer.address
    # )

    # order = {
    #     "parameters": {
    #         **order_parameters.dict(),
    #         "totalOriginalConsiderationItems": len(order_parameters.consideration),
    #     },
    #     "signature": signature,
    # }

    # structed = to_struct(order)

    test_order = [
        (
            (
                "0x66aB6D9362d4F35596279692F0251Db635165871",
                "0x0000000000000000000000000000000000000000",
                0,
                0,
                1000,
                0,
                [(2, "0xDc64a140Aa3E981100a9becA4E685f962f0cF6C9", 0, 1, 1)],
                [
                    (
                        0,
                        "0x0000000000000000000000000000000000000000",
                        0,
                        1,
                        1,
                        "0x66aB6D9362d4F35596279692F0251Db635165871",
                    )
                ],
                1,
            ),
            "0xc56d86a1d6338b13e54bf87cb8fc91e4e013b13d234447e4ab085a44fab8c4f1447efdcd84841c424aa83bc40bd4bd42834a584c8b364f9e5444d93bacfb10ca",
        )
    ]

    # structed = to_struct(test_order)

    # import pdb

    # pdb.set_trace()

    # Use a random address to verify that the signature is valid
    is_valid = consideration.contract.functions.validate(test_order).call(
        {"from": random_signer.address}
    )

    assert is_valid == True
