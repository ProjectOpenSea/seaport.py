import pytest
from brownie.network.account import Accounts, _PrivateKeyAccount
from web3 import Web3

from seaport.seaport import Seaport
from seaport.constants import ItemType
from seaport.types import (
    OfferErc721Item,
    ConsiderationCurrencyItem,
    FulfillOrderDetails,
)


@pytest.fixture(scope="module")
def second_offerer(accounts: Accounts) -> _PrivateKeyAccount:
    return accounts[3]


nft_id = 1
nft_id2 = 2
erc1155_amount = 3


def test_multiple_orders_erc721_buy_now(
    seaport: Seaport,
    erc721,
    second_erc721,
    offerer,
    zone,
    fulfiller,
    second_offerer,
):
    # These will be used in three separate orders
    erc721.mint(offerer, nft_id)
    erc721.mint(offerer, nft_id2)
    second_erc721.mint(second_offerer, nft_id)

    use_case = seaport.create_order(
        account_address=offerer.address,
        offer=[
            OfferErc721Item(token=erc721.address, identifier=nft_id),
        ],
        consideration=[
            ConsiderationCurrencyItem(
                amount=Web3.toWei(10, "ether"), recipient=offerer.address
            ),
            ConsiderationCurrencyItem(
                amount=Web3.toWei(1, "ether"), recipient=zone.address
            ),
        ],
    )

    order = use_case.execute_all_actions()

    use_case = seaport.create_order(
        account_address=offerer.address,
        offer=[
            OfferErc721Item(token=erc721.address, identifier=nft_id2),
        ],
        consideration=[
            ConsiderationCurrencyItem(
                amount=Web3.toWei(10, "ether"), recipient=offerer.address
            ),
            ConsiderationCurrencyItem(
                amount=Web3.toWei(1, "ether"), recipient=zone.address
            ),
        ],
    )

    second_order = use_case.execute_all_actions()

    use_case = seaport.create_order(
        account_address=second_offerer.address,
        offer=[
            OfferErc721Item(token=second_erc721.address, identifier=nft_id),
        ],
        consideration=[
            ConsiderationCurrencyItem(
                amount=Web3.toWei(10, "ether"), recipient=offerer.address
            ),
            ConsiderationCurrencyItem(
                amount=Web3.toWei(1, "ether"), recipient=zone.address
            ),
        ],
    )

    third_order = use_case.execute_all_actions()

    fulfill_order_use_case = seaport.fulfill_orders(
        fulfill_order_details=[
            FulfillOrderDetails(order=order),
            FulfillOrderDetails(order=second_order),
            FulfillOrderDetails(order=third_order),
        ],
        account_address=fulfiller.address,
    )

    actions = fulfill_order_use_case.actions
    fulfill_action = actions[0]
    fulfill_action.transaction_methods.transact()

    assert erc721.ownerOf(nft_id) == fulfiller
    assert erc721.ownerOf(nft_id2) == fulfiller
    assert second_erc721.ownerOf(nft_id) == fulfiller


# TODO ADD TESTS
