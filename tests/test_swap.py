from web3 import Web3

from seaport.constants import ItemType
from seaport.seaport import Seaport
from seaport.types import (
    ConsiderationCurrencyItem,
    ConsiderationErc721Item,
    ConsiderationErc1155Item,
    OfferCurrencyItem,
    OfferErc721Item,
    OfferErc1155Item,
)

nft_id = 1
nft_id2 = 2
erc1155_amount = 3


def test_swap_erc721_for_erc721(
    seaport: Seaport, erc721, second_erc721, offerer, zone, fulfiller
):
    erc721.mint(offerer, nft_id)
    erc721.mint(offerer, nft_id2)
    second_erc721.mint(fulfiller, nft_id)

    use_case = seaport.create_order(
        account_address=offerer.address,
        offer=[
            OfferErc721Item(token=erc721.address, identifier=nft_id),
            OfferErc721Item(token=erc721.address, identifier=nft_id2),
        ],
        consideration=[
            ConsiderationErc721Item(token=second_erc721.address, identifier=nft_id),
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
        "token": second_erc721.address,
        "identifier_or_criteria": nft_id,
        "item_type": ItemType.ERC721.value,
        "transaction_methods": approval_action.transaction_methods,
        "operator": seaport.contract.address,
    }

    approval_action.transaction_methods.transact()

    fulfill_action.transaction_methods.transact()

    assert erc721.ownerOf(nft_id) == fulfiller
    assert erc721.ownerOf(nft_id2) == fulfiller
    assert second_erc721.ownerOf(nft_id) == offerer


def test_swap_erc1155_for_erc1155(
    seaport: Seaport, erc1155, second_erc1155, offerer, zone, fulfiller
):
    erc1155.mint(offerer, nft_id, erc1155_amount)
    erc1155.mint(offerer, nft_id2, erc1155_amount)
    second_erc1155.mint(fulfiller, nft_id, erc1155_amount)

    use_case = seaport.create_order(
        account_address=offerer.address,
        offer=[
            OfferErc1155Item(
                token=erc1155.address, identifier=nft_id, amount=erc1155_amount
            ),
            OfferErc1155Item(
                token=erc1155.address, identifier=nft_id2, amount=erc1155_amount
            ),
        ],
        consideration=[
            ConsiderationErc1155Item(
                token=second_erc1155.address, identifier=nft_id, amount=erc1155_amount
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
        "token": second_erc1155.address,
        "identifier_or_criteria": nft_id,
        "item_type": ItemType.ERC1155.value,
        "transaction_methods": approval_action.transaction_methods,
        "operator": seaport.contract.address,
    }

    approval_action.transaction_methods.transact()

    fulfill_action.transaction_methods.transact()

    assert erc1155.balanceOf(fulfiller, nft_id) == erc1155_amount
    assert erc1155.balanceOf(fulfiller, nft_id2) == erc1155_amount
    assert second_erc1155.balanceOf(offerer, nft_id) == erc1155_amount


def test_swap_erc721_and_erc20_for_erc721_and_erc20(
    seaport: Seaport,
    erc721,
    second_erc721,
    offerer,
    fulfiller,
    erc20,
):
    erc721.mint(offerer, nft_id)
    erc721.mint(offerer, nft_id2)
    second_erc721.mint(fulfiller, nft_id)
    erc20.mint(offerer, Web3.toWei("5", "ether"))
    erc20.mint(fulfiller, Web3.toWei("10", "ether"))

    use_case = seaport.create_order(
        account_address=offerer.address,
        offer=[
            OfferErc721Item(
                token=erc721.address,
                identifier=nft_id,
            ),
            OfferErc721Item(
                token=erc721.address,
                identifier=nft_id2,
            ),
            OfferCurrencyItem(token=erc20.address, amount=Web3.toWei("5", "ether")),
        ],
        consideration=[
            ConsiderationErc721Item(token=second_erc721.address, identifier=nft_id),
            ConsiderationCurrencyItem(
                token=erc20.address, amount=Web3.toWei("10", "ether")
            ),
        ],
    )

    order = use_case.execute_all_actions()

    fulfill_order_use_case = seaport.fulfill_order(
        order=order, account_address=fulfiller.address
    )

    actions = fulfill_order_use_case.actions

    approval_action, second_approval_action, fulfill_action = actions

    assert approval_action.dict() == {
        "type": "approval",
        "token": second_erc721.address,
        "identifier_or_criteria": nft_id,
        "item_type": ItemType.ERC721.value,
        "transaction_methods": approval_action.transaction_methods,
        "operator": seaport.contract.address,
    }

    approval_action.transaction_methods.transact()

    assert second_approval_action.dict() == {
        "type": "approval",
        "token": erc20.address,
        "identifier_or_criteria": 0,
        "item_type": ItemType.ERC20.value,
        "transaction_methods": second_approval_action.transaction_methods,
        "operator": seaport.contract.address,
    }

    second_approval_action.transaction_methods.transact()

    fulfill_action.transaction_methods.transact()

    assert erc721.ownerOf(nft_id) == fulfiller
    assert erc721.ownerOf(nft_id2) == fulfiller
    assert second_erc721.ownerOf(nft_id) == offerer
    assert erc20.balanceOf(offerer) == Web3.toWei("10", "ether")
    assert erc20.balanceOf(fulfiller) == Web3.toWei("5", "ether")
