from web3 import Web3
from web3.types import RPCEndpoint

from consideration.consideration import Consideration
from consideration.constants import ItemType
from consideration.types import (
    BasicOfferErc721Item,
    BasicOfferErc1155Item,
    ConsiderationCurrencyItem,
)

nft_id = 1
erc1155_amount = 5
seconds_in_week = 604800
gas_cost_buffer = Web3.toWei(0.001, "ether")


def test_erc721_ascending_auction(
    consideration: Consideration, erc721, offerer, zone, fulfiller
):
    erc721.mint(offerer, nft_id)
    start_time = consideration.web3.eth.get_block("latest").get("timestamp", 0)
    end_time = start_time + seconds_in_week
    next_block_timestamp = (start_time + end_time) // 2

    use_case = consideration.create_order(
        start_time=start_time,
        end_time=end_time,
        account_address=offerer.address,
        offer=[BasicOfferErc721Item(token=erc721.address, identifier=nft_id)],
        consideration=[
            ConsiderationCurrencyItem(
                amount=Web3.toWei(10, "ether"),
                recipient=offerer.address,
                end_amount=Web3.toWei(20, "ether"),
            ),
            ConsiderationCurrencyItem(
                amount=Web3.toWei(1, "ether"),
                recipient=zone.address,
                end_amount=Web3.toWei(2, "ether"),
            ),
        ],
    )

    order = use_case.execute_all_actions()

    consideration.web3.provider.make_request(
        RPCEndpoint("evm_setNextBlockTimestamp"),
        [next_block_timestamp],
    )
    consideration.web3.provider.make_request(
        RPCEndpoint("evm_mine"),
        [],
    )

    fulfill_order_use_case = consideration.fulfill_order(
        order=order, account_address=fulfiller.address
    )

    actions = fulfill_order_use_case.actions
    fulfill_action = actions[0]

    balance_before = consideration.web3.eth.get_balance(fulfiller.address)

    fulfill_action.transaction_methods.transact()

    expected_balance_after = balance_before - Web3.toWei("16.5", "ether")

    assert erc721.ownerOf(nft_id) == fulfiller

    assert (
        expected_balance_after - gas_cost_buffer
        <= consideration.web3.eth.get_balance(fulfiller.address)
        <= expected_balance_after
    )


def test_erc721_for_erc20_ascending_auction(
    consideration: Consideration, erc721, erc20, offerer, zone, fulfiller
):
    erc721.mint(offerer, nft_id)
    erc20.mint(fulfiller, Web3.toWei(20, "ether"))
    start_time = consideration.web3.eth.get_block("latest").get("timestamp", 0)
    end_time = start_time + seconds_in_week
    next_block_timestamp = (start_time + end_time) // 2

    use_case = consideration.create_order(
        start_time=start_time,
        end_time=end_time,
        account_address=offerer.address,
        offer=[
            BasicOfferErc721Item(token=erc721.address, identifier=nft_id),
        ],
        consideration=[
            ConsiderationCurrencyItem(
                token=erc20.address,
                amount=Web3.toWei(10, "ether"),
                end_amount=Web3.toWei(20, "ether"),
            ),
            ConsiderationCurrencyItem(
                token=erc20.address,
                amount=Web3.toWei(1, "ether"),
                recipient=zone.address,
                end_amount=Web3.toWei(2, "ether"),
            ),
        ],
    )

    order = use_case.execute_all_actions()

    consideration.web3.provider.make_request(
        RPCEndpoint("evm_setNextBlockTimestamp"),
        # Needed due to the transactions before fulfill
        [next_block_timestamp - 2],
    )
    consideration.web3.provider.make_request(
        RPCEndpoint("evm_mine"),
        [],
    )
    fulfill_order_use_case = consideration.fulfill_order(
        order=order, account_address=fulfiller.address
    )

    actions = fulfill_order_use_case.actions
    erc20_approval_action, fulfill_action = actions

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

    assert erc721.ownerOf(nft_id) == fulfiller
    assert erc20.balanceOf(offerer) == Web3.toWei(15, "ether")
    assert erc20.balanceOf(fulfiller) == Web3.toWei(3.5, "ether")
    assert erc20.balanceOf(zone) == Web3.toWei(1.5, "ether")


def test_erc721_descending_auction(
    consideration: Consideration, erc721, offerer, zone, fulfiller
):
    erc721.mint(offerer, nft_id)
    start_time = consideration.web3.eth.get_block("latest").get("timestamp", 0)
    end_time = start_time + seconds_in_week
    next_block_timestamp = (start_time + end_time) // 2

    use_case = consideration.create_order(
        start_time=start_time,
        end_time=end_time,
        account_address=offerer.address,
        offer=[BasicOfferErc721Item(token=erc721.address, identifier=nft_id)],
        consideration=[
            ConsiderationCurrencyItem(
                amount=Web3.toWei(20, "ether"),
                recipient=offerer.address,
                end_amount=Web3.toWei(10, "ether"),
            ),
            ConsiderationCurrencyItem(
                amount=Web3.toWei(1, "ether"),
                recipient=zone.address,
                end_amount=Web3.toWei(2, "ether"),
            ),
        ],
    )

    order = use_case.execute_all_actions()

    consideration.web3.provider.make_request(
        RPCEndpoint("evm_setNextBlockTimestamp"),
        [next_block_timestamp],
    )
    consideration.web3.provider.make_request(
        RPCEndpoint("evm_mine"),
        [],
    )

    fulfill_order_use_case = consideration.fulfill_order(
        order=order, account_address=fulfiller.address
    )

    actions = fulfill_order_use_case.actions
    fulfill_action = actions[0]

    balance_before = consideration.web3.eth.get_balance(fulfiller.address)

    fulfill_action.transaction_methods.transact()

    expected_balance_after = balance_before - Web3.toWei("16.5", "ether")

    assert erc721.ownerOf(nft_id) == fulfiller

    assert (
        expected_balance_after - gas_cost_buffer
        <= consideration.web3.eth.get_balance(fulfiller.address)
        <= expected_balance_after
    )


def test_erc721_for_erc20_descending_auction(
    consideration: Consideration, erc721, erc20, offerer, zone, fulfiller
):
    erc721.mint(offerer, nft_id)
    erc20.mint(fulfiller, Web3.toWei(20, "ether"))
    start_time = consideration.web3.eth.get_block("latest").get("timestamp", 0)
    end_time = start_time + seconds_in_week
    next_block_timestamp = (start_time + end_time) // 2

    use_case = consideration.create_order(
        start_time=start_time,
        end_time=end_time,
        account_address=offerer.address,
        offer=[
            BasicOfferErc721Item(token=erc721.address, identifier=nft_id),
        ],
        consideration=[
            ConsiderationCurrencyItem(
                token=erc20.address,
                end_amount=Web3.toWei(10, "ether"),
                amount=Web3.toWei(20, "ether"),
            ),
            ConsiderationCurrencyItem(
                token=erc20.address,
                amount=Web3.toWei(2, "ether"),
                recipient=zone.address,
                end_amount=Web3.toWei(1, "ether"),
            ),
        ],
    )

    order = use_case.execute_all_actions()

    consideration.web3.provider.make_request(
        RPCEndpoint("evm_setNextBlockTimestamp"),
        # Needed due to the transactions before fulfill
        [next_block_timestamp - 2],
    )
    consideration.web3.provider.make_request(
        RPCEndpoint("evm_mine"),
        [],
    )

    fulfill_order_use_case = consideration.fulfill_order(
        order=order, account_address=fulfiller.address
    )

    actions = fulfill_order_use_case.actions
    erc20_approval_action, fulfill_action = actions

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

    assert erc721.ownerOf(nft_id) == fulfiller
    assert erc20.balanceOf(offerer) == Web3.toWei(15, "ether")
    assert erc20.balanceOf(fulfiller) == Web3.toWei(3.5, "ether")
    assert erc20.balanceOf(zone) == Web3.toWei(1.5, "ether")


def test_erc1155_ascending_auction(
    consideration: Consideration, erc1155, offerer, zone, fulfiller
):
    erc1155.mint(offerer, nft_id, erc1155_amount)
    start_time = consideration.web3.eth.get_block("latest").get("timestamp", 0)
    end_time = start_time + seconds_in_week
    next_block_timestamp = (start_time + end_time) // 2

    use_case = consideration.create_order(
        start_time=start_time,
        end_time=end_time,
        account_address=offerer.address,
        offer=[
            BasicOfferErc1155Item(
                token=erc1155.address,
                identifier=nft_id,
                amount=1,
                end_amount=erc1155_amount,
            )
        ],
        consideration=[
            ConsiderationCurrencyItem(
                amount=Web3.toWei(10, "ether"),
                recipient=offerer.address,
                end_amount=Web3.toWei(20, "ether"),
            ),
            ConsiderationCurrencyItem(
                amount=Web3.toWei(1, "ether"),
                recipient=zone.address,
                end_amount=Web3.toWei(2, "ether"),
            ),
        ],
    )

    order = use_case.execute_all_actions()

    consideration.web3.provider.make_request(
        RPCEndpoint("evm_setNextBlockTimestamp"),
        [next_block_timestamp],
    )
    consideration.web3.provider.make_request(
        RPCEndpoint("evm_mine"),
        [],
    )

    fulfill_order_use_case = consideration.fulfill_order(
        order=order, account_address=fulfiller.address
    )

    actions = fulfill_order_use_case.actions
    fulfill_action = actions[0]

    balance_before = consideration.web3.eth.get_balance(fulfiller.address)

    fulfill_action.transaction_methods.transact()

    expected_balance_after = balance_before - Web3.toWei("16.5", "ether")

    assert erc1155.balanceOf(fulfiller, nft_id) == 3
    assert erc1155.balanceOf(offerer, nft_id) == 2

    assert (
        expected_balance_after - gas_cost_buffer
        <= consideration.web3.eth.get_balance(fulfiller.address)
        <= expected_balance_after
    )


def test_erc1155_for_erc20_ascending_auction(
    consideration: Consideration, erc1155, erc20, offerer, zone, fulfiller
):
    erc1155.mint(offerer, nft_id, erc1155_amount)
    erc20.mint(fulfiller, Web3.toWei(20, "ether"))
    start_time = consideration.web3.eth.get_block("latest").get("timestamp", 0)
    end_time = start_time + seconds_in_week
    next_block_timestamp = (start_time + end_time) // 2

    use_case = consideration.create_order(
        start_time=start_time,
        end_time=end_time,
        account_address=offerer.address,
        offer=[
            BasicOfferErc1155Item(
                token=erc1155.address,
                identifier=nft_id,
                amount=1,
                end_amount=erc1155_amount,
            ),
        ],
        consideration=[
            ConsiderationCurrencyItem(
                token=erc20.address,
                amount=Web3.toWei(10, "ether"),
                end_amount=Web3.toWei(20, "ether"),
            ),
            ConsiderationCurrencyItem(
                token=erc20.address,
                amount=Web3.toWei(1, "ether"),
                recipient=zone.address,
                end_amount=Web3.toWei(2, "ether"),
            ),
        ],
    )

    order = use_case.execute_all_actions()
    consideration.web3.provider.make_request(
        RPCEndpoint("evm_setNextBlockTimestamp"),
        # Needed due to the transactions before fulfill
        [next_block_timestamp - 2],
    )
    consideration.web3.provider.make_request(
        RPCEndpoint("evm_mine"),
        [],
    )
    fulfill_order_use_case = consideration.fulfill_order(
        order=order, account_address=fulfiller.address
    )

    actions = fulfill_order_use_case.actions
    erc20_approval_action, fulfill_action = actions

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

    assert erc1155.balanceOf(offerer, nft_id) == 2
    assert erc1155.balanceOf(fulfiller, nft_id) == 3
    assert erc20.balanceOf(offerer) == Web3.toWei(15, "ether")
    assert erc20.balanceOf(fulfiller) == Web3.toWei(3.5, "ether")
    assert erc20.balanceOf(zone) == Web3.toWei(1.5, "ether")


def test_erc1155_descending_auction(
    consideration: Consideration, erc1155, offerer, zone, fulfiller
):
    erc1155.mint(offerer, nft_id, erc1155_amount)
    start_time = consideration.web3.eth.get_block("latest").get("timestamp", 0)
    end_time = start_time + seconds_in_week
    next_block_timestamp = (start_time + end_time) // 2

    use_case = consideration.create_order(
        start_time=start_time,
        end_time=end_time,
        account_address=offerer.address,
        offer=[
            BasicOfferErc1155Item(
                token=erc1155.address,
                identifier=nft_id,
                amount=erc1155_amount,
                end_amount=1,
            )
        ],
        consideration=[
            ConsiderationCurrencyItem(
                amount=Web3.toWei(20, "ether"),
                recipient=offerer.address,
                end_amount=Web3.toWei(10, "ether"),
            ),
            ConsiderationCurrencyItem(
                amount=Web3.toWei(1, "ether"),
                recipient=zone.address,
                end_amount=Web3.toWei(2, "ether"),
            ),
        ],
    )

    order = use_case.execute_all_actions()

    consideration.web3.provider.make_request(
        RPCEndpoint("evm_setNextBlockTimestamp"),
        [next_block_timestamp],
    )
    consideration.web3.provider.make_request(
        RPCEndpoint("evm_mine"),
        [],
    )

    fulfill_order_use_case = consideration.fulfill_order(
        order=order, account_address=fulfiller.address
    )

    actions = fulfill_order_use_case.actions
    fulfill_action = actions[0]

    balance_before = consideration.web3.eth.get_balance(fulfiller.address)

    fulfill_action.transaction_methods.transact()

    expected_balance_after = balance_before - Web3.toWei("16.5", "ether")

    assert erc1155.balanceOf(offerer, nft_id) == 3
    assert erc1155.balanceOf(fulfiller, nft_id) == 2

    assert (
        expected_balance_after - gas_cost_buffer
        <= consideration.web3.eth.get_balance(fulfiller.address)
        <= expected_balance_after
    )


def test_erc1155_for_erc20_descending_auction(
    consideration: Consideration, erc1155, erc20, offerer, zone, fulfiller
):
    erc1155.mint(offerer, nft_id, erc1155_amount)
    erc20.mint(fulfiller, Web3.toWei(20, "ether"))
    start_time = consideration.web3.eth.get_block("latest").get("timestamp", 0)
    end_time = start_time + seconds_in_week
    next_block_timestamp = (start_time + end_time) // 2

    use_case = consideration.create_order(
        start_time=start_time,
        end_time=end_time,
        account_address=offerer.address,
        offer=[
            BasicOfferErc1155Item(
                token=erc1155.address,
                identifier=nft_id,
                amount=erc1155_amount,
                end_amount=1,
            ),
        ],
        consideration=[
            ConsiderationCurrencyItem(
                token=erc20.address,
                amount=Web3.toWei(20, "ether"),
                end_amount=Web3.toWei(10, "ether"),
            ),
            ConsiderationCurrencyItem(
                token=erc20.address,
                amount=Web3.toWei(2, "ether"),
                recipient=zone.address,
                end_amount=Web3.toWei(1, "ether"),
            ),
        ],
    )

    order = use_case.execute_all_actions()

    consideration.web3.provider.make_request(
        RPCEndpoint("evm_setNextBlockTimestamp"),
        # buffer needed due to transactions before fulfill
        [next_block_timestamp - 2],
    )
    consideration.web3.provider.make_request(
        RPCEndpoint("evm_mine"),
        [],
    )

    fulfill_order_use_case = consideration.fulfill_order(
        order=order, account_address=fulfiller.address
    )

    actions = fulfill_order_use_case.actions
    erc20_approval_action, fulfill_action = actions

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

    assert erc1155.balanceOf(offerer, nft_id) == 2
    assert erc1155.balanceOf(fulfiller, nft_id) == 3
    assert erc20.balanceOf(offerer) == Web3.toWei(15, "ether")
    assert erc20.balanceOf(fulfiller) == Web3.toWei(3.5, "ether")
    assert erc20.balanceOf(zone) == Web3.toWei(1.5, "ether")
