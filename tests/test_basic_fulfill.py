import pytest
from web3 import Web3

from seaport.seaport import Seaport
from seaport.constants import ItemType
from seaport.types import (
    ConsiderationCurrencyItem,
    ConsiderationErc721Item,
    ConsiderationErc1155Item,
    OfferCurrencyItem,
    OfferErc721Item,
    OfferErc1155Item,
)

nft_id = 1


def test_erc721_buy_now(seaport: Seaport, erc721, offerer, zone, fulfiller):
    erc721.mint(offerer, nft_id)
    use_case = seaport.create_order(
        account_address=offerer.address,
        offer=[OfferErc721Item(token=erc721.address, identifier=nft_id)],
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

    fulfill_order_use_case = seaport.fulfill_order(
        order=order, account_address=fulfiller.address
    )

    actions = fulfill_order_use_case.actions
    fulfill_action = actions[0]
    fulfill_action.transaction_methods.transact()

    assert erc721.ownerOf(nft_id) == fulfiller


def test_erc721_buy_now_already_validated_order(
    seaport: Seaport,
    erc721,
    offerer,
    zone,
    fulfiller,
):
    erc721.mint(offerer, nft_id)
    use_case = seaport.create_order(
        account_address=offerer.address,
        offer=[OfferErc721Item(token=erc721.address, identifier=nft_id)],
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
    order.signature = "0x"

    fulfill_order_use_case = seaport.fulfill_order(
        order=order, account_address=fulfiller.address
    )

    actions = fulfill_order_use_case.actions
    fulfill_action = actions[0]

    with pytest.raises(Exception):
        fulfill_action.transaction_methods.transact()

    seaport.validate([order]).transact()
    fulfill_action.transaction_methods.transact()
    assert erc721.ownerOf(nft_id) == fulfiller


def test_erc721_buy_now_with_erc20(
    seaport: Seaport, erc721, erc20, offerer, zone, fulfiller
):
    erc721.mint(offerer, nft_id)
    erc20.mint(fulfiller, Web3.toWei(11, "ether"))
    use_case = seaport.create_order(
        account_address=offerer.address,
        offer=[OfferErc721Item(token=erc721.address, identifier=nft_id)],
        consideration=[
            ConsiderationCurrencyItem(
                amount=Web3.toWei(10, "ether"),
                recipient=offerer.address,
                token=erc20.address,
            ),
            ConsiderationCurrencyItem(
                amount=Web3.toWei(1, "ether"),
                recipient=zone.address,
                token=erc20.address,
            ),
        ],
    )

    order = use_case.execute_all_actions()

    fulfill_order_use_case = seaport.fulfill_order(
        order=order, account_address=fulfiller.address
    )

    actions = fulfill_order_use_case.actions
    approval_action, fulfill_action = actions

    assert approval_action.dict() == {
        "type": "approval",
        "token": erc20.address,
        "identifier_or_criteria": 0,
        "item_type": ItemType.ERC20.value,
        "transaction_methods": approval_action.transaction_methods,
        "operator": seaport.contract.address,
    }

    approval_action.transaction_methods.transact()
    fulfill_action.transaction_methods.transact()

    assert erc721.ownerOf(nft_id) == fulfiller


def test_erc721_accept_offer(seaport: Seaport, erc721, erc20, offerer, zone, fulfiller):
    erc721.mint(fulfiller, nft_id)
    erc20.mint(offerer, Web3.toWei(11, "ether"))
    use_case = seaport.create_order(
        account_address=offerer.address,
        offer=[
            OfferCurrencyItem(
                amount=Web3.toWei(10, "ether"),
                token=erc20.address,
            ),
        ],
        consideration=[
            ConsiderationErc721Item(
                token=erc721.address, identifier=nft_id, recipient=offerer.address
            ),
            ConsiderationCurrencyItem(
                amount=Web3.toWei(1, "ether"),
                recipient=zone.address,
                token=erc20.address,
            ),
        ],
    )

    order = use_case.execute_all_actions()

    fulfill_order_use_case = seaport.fulfill_order(
        order=order, account_address=fulfiller.address
    )

    actions = fulfill_order_use_case.actions
    approval_action, fulfill_action = actions

    assert approval_action.dict() == {
        "type": "approval",
        "token": erc721.address,
        "identifier_or_criteria": nft_id,
        "item_type": ItemType.ERC721.value,
        "transaction_methods": approval_action.transaction_methods,
        "operator": seaport.contract.address,
    }

    approval_action.transaction_methods.transact()
    fulfill_action.transaction_methods.transact()

    assert erc721.ownerOf(nft_id) == offerer


def test_erc1155_buy_now(seaport: Seaport, erc1155, offerer, zone, fulfiller):
    erc1155.mint(offerer, nft_id, 1)
    use_case = seaport.create_order(
        account_address=offerer.address,
        offer=[OfferErc1155Item(token=erc1155.address, identifier=nft_id, amount=1)],
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

    fulfill_order_use_case = seaport.fulfill_order(
        order=order, account_address=fulfiller.address
    )

    actions = fulfill_order_use_case.actions
    fulfill_action = actions[0]
    fulfill_action.transaction_methods.transact()

    assert erc1155.balanceOf(fulfiller, nft_id) == 1


def test_erc1155_buy_now_already_validated_order(
    seaport: Seaport,
    erc1155,
    offerer,
    zone,
    fulfiller,
):
    erc1155.mint(offerer, nft_id, 1)
    use_case = seaport.create_order(
        account_address=offerer.address,
        offer=[OfferErc1155Item(token=erc1155.address, identifier=nft_id, amount=1)],
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
    order.signature = "0x"

    fulfill_order_use_case = seaport.fulfill_order(
        order=order, account_address=fulfiller.address
    )

    actions = fulfill_order_use_case.actions
    fulfill_action = actions[0]

    with pytest.raises(Exception):
        fulfill_action.transaction_methods.transact()

    seaport.validate([order]).transact()
    fulfill_action.transaction_methods.transact()
    assert erc1155.balanceOf(fulfiller, nft_id) == 1


def test_erc1155_buy_now_with_erc20(
    seaport: Seaport, erc1155, erc20, offerer, zone, fulfiller
):
    erc1155.mint(offerer, nft_id, 1)
    erc20.mint(fulfiller, Web3.toWei(11, "ether"))
    use_case = seaport.create_order(
        account_address=offerer.address,
        offer=[OfferErc1155Item(token=erc1155.address, identifier=nft_id, amount=1)],
        consideration=[
            ConsiderationCurrencyItem(
                amount=Web3.toWei(10, "ether"),
                recipient=offerer.address,
                token=erc20.address,
            ),
            ConsiderationCurrencyItem(
                amount=Web3.toWei(1, "ether"),
                recipient=zone.address,
                token=erc20.address,
            ),
        ],
    )

    order = use_case.execute_all_actions()

    fulfill_order_use_case = seaport.fulfill_order(
        order=order, account_address=fulfiller.address
    )

    actions = fulfill_order_use_case.actions
    approval_action, fulfill_action = actions

    assert approval_action.dict() == {
        "type": "approval",
        "token": erc20.address,
        "identifier_or_criteria": 0,
        "item_type": ItemType.ERC20.value,
        "transaction_methods": approval_action.transaction_methods,
        "operator": seaport.contract.address,
    }

    approval_action.transaction_methods.transact()
    fulfill_action.transaction_methods.transact()

    assert erc1155.balanceOf(fulfiller, nft_id) == 1


def test_erc1155_accept_offer(
    seaport: Seaport, erc1155, erc20, offerer, zone, fulfiller
):
    erc1155.mint(fulfiller, nft_id, 1)
    erc20.mint(offerer, Web3.toWei(11, "ether"))
    use_case = seaport.create_order(
        account_address=offerer.address,
        offer=[
            OfferCurrencyItem(
                amount=Web3.toWei(10, "ether"),
                token=erc20.address,
            ),
        ],
        consideration=[
            ConsiderationErc1155Item(
                token=erc1155.address,
                identifier=nft_id,
                recipient=offerer.address,
                amount=1,
            ),
            ConsiderationCurrencyItem(
                amount=Web3.toWei(1, "ether"),
                recipient=zone.address,
                token=erc20.address,
            ),
        ],
    )

    order = use_case.execute_all_actions()

    fulfill_order_use_case = seaport.fulfill_order(
        order=order, account_address=fulfiller.address
    )

    actions = fulfill_order_use_case.actions
    approval_action, fulfill_action = actions

    assert approval_action.dict() == {
        "type": "approval",
        "token": erc1155.address,
        "identifier_or_criteria": nft_id,
        "item_type": ItemType.ERC1155.value,
        "transaction_methods": approval_action.transaction_methods,
        "operator": seaport.contract.address,
    }

    approval_action.transaction_methods.transact()
    fulfill_action.transaction_methods.transact()

    assert erc1155.balanceOf(offerer, nft_id) == 1
