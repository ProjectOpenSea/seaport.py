from web3 import Web3

from seaport.constants import ItemType, OrderType
from seaport.seaport import Seaport
from seaport.types import (
    ConsiderationCurrencyItem,
    ConsiderationErc1155Item,
    OfferCurrencyItem,
    OfferErc1155Item,
)

nft_id = 1
erc1155_amount = 10
erc1155_amount2 = 5


def test_partial_erc1155_buy_now(seaport: Seaport, erc1155, offerer, zone, fulfiller):
    erc1155.mint(offerer, nft_id, erc1155_amount)

    use_case = seaport.create_order(
        account_address=offerer.address,
        offer=[
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
        allow_partial_fills=True,
    )

    order = use_case.execute_all_actions()

    assert order.parameters.orderType == OrderType.PARTIAL_OPEN

    fulfill_order_use_case = seaport.fulfill_order(
        order=order, account_address=fulfiller.address, units_to_fill=2
    )

    actions = fulfill_order_use_case.actions
    fulfill_action = actions[0]
    fulfill_action.transaction_methods.transact()

    assert erc1155.balanceOf(fulfiller, nft_id) == 2


def test_partial_erc1155_buy_now_with_erc20(
    seaport: Seaport,
    erc1155,
    erc20,
    second_erc1155,
    offerer,
    zone,
    fulfiller,
):
    erc1155.mint(offerer, nft_id, erc1155_amount)
    erc20.mint(fulfiller, Web3.toWei(11, "ether"))
    use_case = seaport.create_order(
        account_address=offerer.address,
        offer=[
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
        allow_partial_fills=True,
    )

    order = use_case.execute_all_actions()

    fulfill_order_use_case = seaport.fulfill_order(
        order=order, account_address=fulfiller.address, units_to_fill=2
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

    assert erc1155.balanceOf(fulfiller, nft_id) == 2


def test_partial_erc1155_accept_offer(
    seaport: Seaport,
    erc1155,
    second_erc1155,
    erc20,
    offerer,
    zone,
    fulfiller,
):
    erc1155.mint(fulfiller, nft_id, erc1155_amount)
    erc20.mint(offerer, Web3.toWei(11, "ether"))

    use_case = seaport.create_order(
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
            ConsiderationCurrencyItem(
                amount=Web3.toWei(1, "ether"),
                recipient=zone.address,
                token=erc20.address,
            ),
        ],
        allow_partial_fills=True,
    )

    order = use_case.execute_all_actions()

    fulfill_order_use_case = seaport.fulfill_order(
        order=order, account_address=fulfiller.address, units_to_fill=2
    )

    actions = fulfill_order_use_case.actions

    (
        erc1155_approval_action,
        erc20_approval_action,
        fulfill_action,
    ) = actions

    assert erc1155_approval_action.dict() == {
        "type": "approval",
        "token": erc1155.address,
        "identifier_or_criteria": nft_id,
        "item_type": ItemType.ERC1155.value,
        "transaction_methods": erc1155_approval_action.transaction_methods,
        "operator": seaport.contract.address,
    }

    erc1155_approval_action.transaction_methods.transact()

    assert erc20_approval_action.dict() == {
        "type": "approval",
        "token": erc20.address,
        "identifier_or_criteria": 0,
        "item_type": ItemType.ERC20.value,
        "transaction_methods": erc20_approval_action.transaction_methods,
        "operator": seaport.contract.address,
    }

    erc20_approval_action.transaction_methods.transact()

    fulfill_action.transaction_methods.transact()

    assert erc1155.balanceOf(offerer, nft_id) == 2


def test_partial_multiple_erc1155_buy_now(
    seaport: Seaport, erc1155, second_erc1155, offerer, zone, fulfiller
):
    erc1155.mint(offerer, nft_id, erc1155_amount)
    second_erc1155.mint(offerer, nft_id, erc1155_amount2)

    use_case = seaport.create_order(
        account_address=offerer.address,
        offer=[
            OfferErc1155Item(
                token=erc1155.address, identifier=nft_id, amount=erc1155_amount
            ),
            OfferErc1155Item(
                token=second_erc1155.address, identifier=nft_id, amount=erc1155_amount2
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
        allow_partial_fills=True,
    )

    order = use_case.execute_all_actions()

    assert order.parameters.orderType == OrderType.PARTIAL_OPEN

    fulfill_order_use_case = seaport.fulfill_order(
        order=order, account_address=fulfiller.address, units_to_fill=2
    )

    actions = fulfill_order_use_case.actions
    fulfill_action = actions[0]
    fulfill_action.transaction_methods.transact()

    assert erc1155.balanceOf(fulfiller, nft_id) == 4
    assert second_erc1155.balanceOf(fulfiller, nft_id) == 2


def test_partial_erc1155_multiple_buy_now_with_erc20(
    seaport: Seaport,
    erc1155,
    erc20,
    second_erc1155,
    offerer,
    zone,
    fulfiller,
):
    erc1155.mint(offerer, nft_id, erc1155_amount)
    second_erc1155.mint(offerer, nft_id, erc1155_amount2)
    erc20.mint(fulfiller, Web3.toWei(11, "ether"))
    use_case = seaport.create_order(
        account_address=offerer.address,
        offer=[
            OfferErc1155Item(
                token=erc1155.address, identifier=nft_id, amount=erc1155_amount
            ),
            OfferErc1155Item(
                token=second_erc1155.address, identifier=nft_id, amount=erc1155_amount2
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
        allow_partial_fills=True,
    )

    order = use_case.execute_all_actions()

    assert order.parameters.orderType == OrderType.PARTIAL_OPEN

    fulfill_order_use_case = seaport.fulfill_order(
        order=order, account_address=fulfiller.address, units_to_fill=2
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

    assert erc1155.balanceOf(fulfiller, nft_id) == 4
    assert second_erc1155.balanceOf(fulfiller, nft_id) == 2


def test_partial_erc1155_multiple_accept_offer(
    seaport: Seaport,
    erc1155,
    second_erc1155,
    erc20,
    offerer,
    zone,
    fulfiller,
):
    erc1155.mint(fulfiller, nft_id, erc1155_amount)
    second_erc1155.mint(fulfiller, nft_id, erc1155_amount2)
    erc20.mint(offerer, Web3.toWei(11, "ether"))

    use_case = seaport.create_order(
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
                token=second_erc1155.address,
                identifier=nft_id,
                recipient=offerer.address,
                amount=erc1155_amount2,
            ),
            ConsiderationCurrencyItem(
                amount=Web3.toWei(1, "ether"),
                recipient=zone.address,
                token=erc20.address,
            ),
        ],
        allow_partial_fills=True,
    )

    order = use_case.execute_all_actions()

    assert order.parameters.orderType == OrderType.PARTIAL_OPEN

    fulfill_order_use_case = seaport.fulfill_order(
        order=order, account_address=fulfiller.address, units_to_fill=2
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
        "identifier_or_criteria": nft_id,
        "item_type": ItemType.ERC1155.value,
        "transaction_methods": erc1155_approval_action.transaction_methods,
        "operator": seaport.contract.address,
    }

    erc1155_approval_action.transaction_methods.transact()

    assert second_erc1155_approval_action.dict() == {
        "type": "approval",
        "token": second_erc1155.address,
        "identifier_or_criteria": nft_id,
        "item_type": ItemType.ERC1155.value,
        "transaction_methods": second_erc1155_approval_action.transaction_methods,
        "operator": seaport.contract.address,
    }

    second_erc1155_approval_action.transaction_methods.transact()

    assert erc20_approval_action.dict() == {
        "type": "approval",
        "token": erc20.address,
        "identifier_or_criteria": 0,
        "item_type": ItemType.ERC20.value,
        "transaction_methods": erc20_approval_action.transaction_methods,
        "operator": seaport.contract.address,
    }

    erc20_approval_action.transaction_methods.transact()

    fulfill_action.transaction_methods.transact()

    assert erc1155.balanceOf(offerer, nft_id) == 4
    assert second_erc1155.balanceOf(offerer, nft_id) == 2
