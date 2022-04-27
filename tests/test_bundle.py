from web3 import Web3

from consideration.consideration import Consideration
from consideration.constants import ItemType
from consideration.types import (
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


def test_bundle_erc721_buy_now(
    consideration: Consideration, erc721, second_erc721, offerer, zone, fulfiller
):
    erc721.mint(offerer, nft_id)
    erc721.mint(offerer, nft_id2)
    second_erc721.mint(offerer, nft_id)

    use_case = consideration.create_order(
        account_address=offerer.address,
        offer=[
            OfferErc721Item(token=erc721.address, identifier=nft_id),
            OfferErc721Item(token=erc721.address, identifier=nft_id2),
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

    order = use_case.execute_all_actions()

    fulfill_order_use_case = consideration.fulfill_order(
        order=order, account_address=fulfiller.address
    )

    actions = fulfill_order_use_case.actions
    fulfill_action = actions[0]
    fulfill_action.transaction_methods.transact()

    assert erc721.ownerOf(nft_id) == fulfiller
    assert erc721.ownerOf(nft_id2) == fulfiller
    assert second_erc721.ownerOf(nft_id) == fulfiller


def test_bundle_erc721_buy_now_with_erc20(
    consideration: Consideration, erc721, erc20, second_erc721, offerer, zone, fulfiller
):
    erc721.mint(offerer, nft_id)
    erc721.mint(offerer, nft_id2)
    second_erc721.mint(offerer, nft_id)
    erc20.mint(fulfiller, Web3.toWei(11, "ether"))
    use_case = consideration.create_order(
        account_address=offerer.address,
        offer=[
            OfferErc721Item(token=erc721.address, identifier=nft_id),
            OfferErc721Item(token=erc721.address, identifier=nft_id2),
            OfferErc721Item(token=second_erc721.address, identifier=nft_id),
        ],
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

    fulfill_order_use_case = consideration.fulfill_order(
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
        "operator": consideration.contract.address,
    }

    approval_action.transaction_methods.transact()
    fulfill_action.transaction_methods.transact()

    assert erc721.ownerOf(nft_id) == fulfiller
    assert erc721.ownerOf(nft_id2) == fulfiller
    assert second_erc721.ownerOf(nft_id) == fulfiller


def test_bundle_erc721_accept_offer(
    consideration: Consideration, erc721, second_erc721, erc20, offerer, zone, fulfiller
):
    erc721.mint(fulfiller, nft_id)
    erc721.mint(fulfiller, nft_id2)
    second_erc721.mint(fulfiller, nft_id)
    erc20.mint(offerer, Web3.toWei(11, "ether"))

    use_case = consideration.create_order(
        account_address=offerer.address,
        offer=[
            OfferCurrencyItem(
                amount=Web3.toWei(11, "ether"),
                token=erc20.address,
            ),
        ],
        consideration=[
            ConsiderationErc721Item(
                token=erc721.address, identifier=nft_id, recipient=offerer.address
            ),
            ConsiderationErc721Item(
                token=erc721.address, identifier=nft_id2, recipient=offerer.address
            ),
            ConsiderationErc721Item(
                token=second_erc721.address,
                identifier=nft_id,
                recipient=offerer.address,
            ),
            ConsiderationCurrencyItem(
                amount=Web3.toWei(1, "ether"),
                recipient=zone.address,
                token=erc20.address,
            ),
        ],
    )

    order = use_case.execute_all_actions()

    fulfill_order_use_case = consideration.fulfill_order(
        order=order, account_address=fulfiller.address
    )

    actions = fulfill_order_use_case.actions

    (
        erc721_approval_action,
        second_erc721_approval_action,
        erc20_approval_action,
        fulfill_action,
    ) = actions

    assert erc721_approval_action.dict() == {
        "type": "approval",
        "token": erc721.address,
        "identifier_or_criteria": nft_id2,
        "item_type": ItemType.ERC721.value,
        "transaction_methods": erc721_approval_action.transaction_methods,
        "operator": consideration.contract.address,
    }

    erc721_approval_action.transaction_methods.transact()

    assert second_erc721_approval_action.dict() == {
        "type": "approval",
        "token": second_erc721.address,
        "identifier_or_criteria": nft_id,
        "item_type": ItemType.ERC721.value,
        "transaction_methods": second_erc721_approval_action.transaction_methods,
        "operator": consideration.contract.address,
    }

    second_erc721_approval_action.transaction_methods.transact()

    assert erc20_approval_action.dict() == {
        "type": "approval",
        "token": erc20.address,
        "identifier_or_criteria": 0,
        "item_type": ItemType.ERC20.value,
        "transaction_methods": erc20_approval_action.transaction_methods,
        "operator": consideration.contract.address,
    }

    erc20_approval_action.transaction_methods.transact()

    fulfill_action.transaction_methods.transact()

    assert erc721.ownerOf(nft_id) == offerer
    assert erc721.ownerOf(nft_id2) == offerer
    assert second_erc721.ownerOf(nft_id) == offerer


def test_bundle_erc721_and_erc1155_buy_now(
    consideration: Consideration,
    erc721,
    second_erc721,
    erc1155,
    offerer,
    zone,
    fulfiller,
):
    erc721.mint(offerer, nft_id)
    second_erc721.mint(offerer, nft_id)
    erc1155.mint(offerer, nft_id, erc1155_amount)

    use_case = consideration.create_order(
        account_address=offerer.address,
        offer=[
            OfferErc721Item(token=erc721.address, identifier=nft_id),
            OfferErc721Item(token=second_erc721.address, identifier=nft_id),
            OfferErc1155Item(
                token=erc1155.address, identifier=nft_id, amount=erc1155_amount
            ),
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

    fulfill_order_use_case = consideration.fulfill_order(
        order=order, account_address=fulfiller.address
    )

    actions = fulfill_order_use_case.actions
    fulfill_action = actions[0]
    fulfill_action.transaction_methods.transact()

    assert erc721.ownerOf(nft_id) == fulfiller
    assert second_erc721.ownerOf(nft_id) == fulfiller
    assert erc1155.balanceOf(fulfiller, nft_id) == erc1155_amount


def test_bundle_erc721_and_erc1155_buy_now_with_erc20(
    consideration: Consideration,
    erc721,
    erc20,
    second_erc721,
    erc1155,
    offerer,
    zone,
    fulfiller,
):
    erc721.mint(offerer, nft_id)
    second_erc721.mint(offerer, nft_id)
    erc1155.mint(offerer, nft_id, erc1155_amount)
    erc20.mint(fulfiller, Web3.toWei(11, "ether"))
    use_case = consideration.create_order(
        account_address=offerer.address,
        offer=[
            OfferErc721Item(token=erc721.address, identifier=nft_id),
            OfferErc721Item(token=second_erc721.address, identifier=nft_id),
            OfferErc1155Item(
                token=erc1155.address, identifier=nft_id, amount=erc1155_amount
            ),
        ],
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

    fulfill_order_use_case = consideration.fulfill_order(
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
        "operator": consideration.contract.address,
    }

    approval_action.transaction_methods.transact()
    fulfill_action.transaction_methods.transact()

    assert erc721.ownerOf(nft_id) == fulfiller
    assert second_erc721.ownerOf(nft_id) == fulfiller
    assert erc1155.balanceOf(fulfiller, nft_id) == erc1155_amount


def test_bundle_erc721_and_erc1155_accept_offer(
    consideration: Consideration,
    erc721,
    second_erc721,
    erc20,
    erc1155,
    offerer,
    zone,
    fulfiller,
):
    erc721.mint(fulfiller, nft_id)
    second_erc721.mint(fulfiller, nft_id)
    erc1155.mint(fulfiller, nft_id, erc1155_amount)
    erc20.mint(offerer, Web3.toWei(11, "ether"))

    use_case = consideration.create_order(
        account_address=offerer.address,
        offer=[
            OfferCurrencyItem(
                amount=Web3.toWei(11, "ether"),
                token=erc20.address,
            ),
        ],
        consideration=[
            ConsiderationErc721Item(
                token=erc721.address, identifier=nft_id, recipient=offerer.address
            ),
            ConsiderationErc721Item(
                token=second_erc721.address,
                identifier=nft_id,
                recipient=offerer.address,
            ),
            ConsiderationErc1155Item(
                token=erc1155.address,
                identifier=nft_id,
                amount=erc1155_amount,
                recipient=offerer.address,
            ),
            ConsiderationCurrencyItem(
                amount=Web3.toWei(1, "ether"),
                recipient=zone.address,
                token=erc20.address,
            ),
        ],
    )

    order = use_case.execute_all_actions()

    fulfill_order_use_case = consideration.fulfill_order(
        order=order, account_address=fulfiller.address
    )

    actions = fulfill_order_use_case.actions

    (
        erc721_approval_action,
        second_erc721_approval_action,
        erc1155_approval_action,
        erc20_approval_action,
        fulfill_action,
    ) = actions

    assert erc721_approval_action.dict() == {
        "type": "approval",
        "token": erc721.address,
        "identifier_or_criteria": nft_id,
        "item_type": ItemType.ERC721.value,
        "transaction_methods": erc721_approval_action.transaction_methods,
        "operator": consideration.contract.address,
    }

    erc721_approval_action.transaction_methods.transact()

    assert second_erc721_approval_action.dict() == {
        "type": "approval",
        "token": second_erc721.address,
        "identifier_or_criteria": nft_id,
        "item_type": ItemType.ERC721.value,
        "transaction_methods": second_erc721_approval_action.transaction_methods,
        "operator": consideration.contract.address,
    }

    second_erc721_approval_action.transaction_methods.transact()

    assert erc1155_approval_action.dict() == {
        "type": "approval",
        "token": erc1155.address,
        "identifier_or_criteria": nft_id,
        "item_type": ItemType.ERC1155.value,
        "transaction_methods": erc1155_approval_action.transaction_methods,
        "operator": consideration.contract.address,
    }

    erc1155_approval_action.transaction_methods.transact()

    assert erc20_approval_action.dict() == {
        "type": "approval",
        "token": erc20.address,
        "identifier_or_criteria": 0,
        "item_type": ItemType.ERC20.value,
        "transaction_methods": erc20_approval_action.transaction_methods,
        "operator": consideration.contract.address,
    }

    erc20_approval_action.transaction_methods.transact()

    fulfill_action.transaction_methods.transact()

    assert erc721.ownerOf(nft_id) == offerer
    assert second_erc721.ownerOf(nft_id) == offerer
    assert erc1155.balanceOf(offerer, nft_id) == erc1155_amount


def test_bundle_erc1155_buy_now(
    consideration: Consideration, erc1155, second_erc1155, offerer, zone, fulfiller
):
    erc1155.mint(offerer, nft_id, erc1155_amount)
    erc1155.mint(offerer, nft_id2, erc1155_amount)
    second_erc1155.mint(offerer, nft_id, erc1155_amount)

    use_case = consideration.create_order(
        account_address=offerer.address,
        offer=[
            OfferErc1155Item(
                token=erc1155.address, identifier=nft_id, amount=erc1155_amount
            ),
            OfferErc1155Item(
                token=erc1155.address, identifier=nft_id2, amount=erc1155_amount
            ),
            OfferErc1155Item(
                token=second_erc1155.address, identifier=nft_id, amount=erc1155_amount
            ),
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

    fulfill_order_use_case = consideration.fulfill_order(
        order=order, account_address=fulfiller.address
    )

    actions = fulfill_order_use_case.actions
    fulfill_action = actions[0]
    fulfill_action.transaction_methods.transact()

    assert erc1155.balanceOf(fulfiller, nft_id) == erc1155_amount
    assert erc1155.balanceOf(fulfiller, nft_id2) == erc1155_amount
    assert second_erc1155.balanceOf(fulfiller, nft_id) == erc1155_amount


def test_bundle_erc1155_buy_now_with_erc20(
    consideration: Consideration,
    erc1155,
    erc20,
    second_erc1155,
    offerer,
    zone,
    fulfiller,
):
    erc1155.mint(offerer, nft_id, erc1155_amount)
    erc1155.mint(offerer, nft_id2, erc1155_amount)
    second_erc1155.mint(offerer, nft_id, erc1155_amount)
    erc20.mint(fulfiller, Web3.toWei(11, "ether"))
    use_case = consideration.create_order(
        account_address=offerer.address,
        offer=[
            OfferErc1155Item(
                token=erc1155.address, identifier=nft_id, amount=erc1155_amount
            ),
            OfferErc1155Item(
                token=erc1155.address, identifier=nft_id2, amount=erc1155_amount
            ),
            OfferErc1155Item(
                token=second_erc1155.address, identifier=nft_id, amount=erc1155_amount
            ),
        ],
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

    fulfill_order_use_case = consideration.fulfill_order(
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
        "operator": consideration.contract.address,
    }

    approval_action.transaction_methods.transact()
    fulfill_action.transaction_methods.transact()

    assert erc1155.balanceOf(fulfiller, nft_id) == erc1155_amount
    assert erc1155.balanceOf(fulfiller, nft_id2) == erc1155_amount
    assert second_erc1155.balanceOf(fulfiller, nft_id) == erc1155_amount


def test_bundle_erc1155_accept_offer(
    consideration: Consideration,
    erc1155,
    second_erc1155,
    erc20,
    offerer,
    zone,
    fulfiller,
):
    erc1155.mint(fulfiller, nft_id, erc1155_amount)
    erc1155.mint(fulfiller, nft_id2, erc1155_amount)
    second_erc1155.mint(fulfiller, nft_id, erc1155_amount)
    erc20.mint(offerer, Web3.toWei(11, "ether"))

    use_case = consideration.create_order(
        account_address=offerer.address,
        offer=[
            OfferCurrencyItem(
                amount=Web3.toWei(11, "ether"),
                token=erc20.address,
            ),
        ],
        consideration=[
            ConsiderationErc1155Item(
                token=erc1155.address,
                identifier=nft_id,
                recipient=offerer.address,
                amount=erc1155_amount,
            ),
            ConsiderationErc1155Item(
                token=erc1155.address,
                identifier=nft_id2,
                recipient=offerer.address,
                amount=erc1155_amount,
            ),
            ConsiderationErc1155Item(
                token=second_erc1155.address,
                identifier=nft_id,
                recipient=offerer.address,
                amount=erc1155_amount,
            ),
            ConsiderationCurrencyItem(
                amount=Web3.toWei(1, "ether"),
                recipient=zone.address,
                token=erc20.address,
            ),
        ],
    )

    order = use_case.execute_all_actions()

    fulfill_order_use_case = consideration.fulfill_order(
        order=order, account_address=fulfiller.address
    )

    actions = fulfill_order_use_case.actions

    (
        erc1155_approval_action,
        second_erc1155_approval_action,
        erc20_approval_action,
        fulfill_action,
    ) = actions

    assert erc1155_approval_action.dict() == {
        "type": "approval",
        "token": erc1155.address,
        "identifier_or_criteria": nft_id2,
        "item_type": ItemType.ERC1155.value,
        "transaction_methods": erc1155_approval_action.transaction_methods,
        "operator": consideration.contract.address,
    }

    erc1155_approval_action.transaction_methods.transact()

    assert second_erc1155_approval_action.dict() == {
        "type": "approval",
        "token": second_erc1155.address,
        "identifier_or_criteria": nft_id,
        "item_type": ItemType.ERC1155.value,
        "transaction_methods": second_erc1155_approval_action.transaction_methods,
        "operator": consideration.contract.address,
    }

    second_erc1155_approval_action.transaction_methods.transact()

    assert erc20_approval_action.dict() == {
        "type": "approval",
        "token": erc20.address,
        "identifier_or_criteria": 0,
        "item_type": ItemType.ERC20.value,
        "transaction_methods": erc20_approval_action.transaction_methods,
        "operator": consideration.contract.address,
    }

    erc20_approval_action.transaction_methods.transact()

    fulfill_action.transaction_methods.transact()

    assert erc1155.balanceOf(offerer, nft_id) == erc1155_amount
    assert erc1155.balanceOf(offerer, nft_id2) == erc1155_amount
    assert second_erc1155.balanceOf(offerer, nft_id) == erc1155_amount
