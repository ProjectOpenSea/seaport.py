import pytest
from web3 import Web3
from consideration.consideration import Consideration
from consideration.constants import LEGACY_PROXY_CONDUIT, ItemType
from consideration.types import (
    BasicConsiderationErc721Item,
    BasicOfferErc721Item,
    ConsiderationCurrencyItem,
    OfferCurrencyItem,
)
from web3.constants import ADDRESS_ZERO


nft_id = 1


# def test_erc721_buy_now(consideration: Consideration, erc721, offerer, zone, fulfiller):
#     erc721.mint(offerer, nft_id)
#     use_case = consideration.create_order(
#         account_address=offerer.address,
#         offer=[BasicOfferErc721Item(token=erc721.address, identifier=nft_id)],
#         consideration=[
#             ConsiderationCurrencyItem(
#                 amount=Web3.toWei(10, "ether"), recipient=offerer.address
#             ),
#             ConsiderationCurrencyItem(
#                 amount=Web3.toWei(1, "ether"), recipient=zone.address
#             ),
#         ],
#     )

#     order = use_case.execute_all_actions()

#     fulfill_order_use_case = consideration.fulfill_order(
#         order=order, account_address=fulfiller.address
#     )

#     actions = fulfill_order_use_case.actions
#     fulfill_action = actions[0]
#     fulfill_action.transaction_methods.transact()

#     assert erc721.ownerOf(nft_id) == fulfiller


# def test_erc721_buy_now_offer_via_proxy(
#     consideration: Consideration,
#     erc721,
#     offerer,
#     zone,
#     fulfiller,
#     legacy_proxy_registry,
# ):
#     erc721.mint(offerer, nft_id)
#     legacy_proxy_registry.registerProxy({"from": offerer})
#     offerer_proxy = legacy_proxy_registry.proxies(offerer.address)
#     erc721.setApprovalForAll(offerer_proxy, True)

#     use_case = consideration.create_order(
#         account_address=offerer.address,
#         offer=[BasicOfferErc721Item(token=erc721.address, identifier=nft_id)],
#         consideration=[
#             ConsiderationCurrencyItem(
#                 amount=Web3.toWei(10, "ether"), recipient=offerer.address
#             ),
#             ConsiderationCurrencyItem(
#                 amount=Web3.toWei(1, "ether"), recipient=zone.address
#             ),
#         ],
#     )

#     order = use_case.execute_all_actions()
#     assert order.parameters.conduit == LEGACY_PROXY_CONDUIT

#     fulfill_order_use_case = consideration.fulfill_order(
#         order=order, account_address=fulfiller.address
#     )

#     actions = fulfill_order_use_case.actions
#     assert len(actions) == 1
#     fulfill_action = actions[0]
#     fulfill_action.transaction_methods.transact()

#     assert erc721.ownerOf(nft_id) == fulfiller


# def test_erc721_buy_now_already_validated_order(
#     consideration: Consideration,
#     erc721,
#     offerer,
#     zone,
#     fulfiller,
# ):
#     erc721.mint(offerer, nft_id)
#     use_case = consideration.create_order(
#         account_address=offerer.address,
#         offer=[BasicOfferErc721Item(token=erc721.address, identifier=nft_id)],
#         consideration=[
#             ConsiderationCurrencyItem(
#                 amount=Web3.toWei(10, "ether"), recipient=offerer.address
#             ),
#             ConsiderationCurrencyItem(
#                 amount=Web3.toWei(1, "ether"), recipient=zone.address
#             ),
#         ],
#     )

#     order = use_case.execute_all_actions()
#     order.signature = "0x"

#     fulfill_order_use_case = consideration.fulfill_order(
#         order=order, account_address=fulfiller.address
#     )

#     actions = fulfill_order_use_case.actions
#     fulfill_action = actions[0]

#     with pytest.raises(Exception):
#         fulfill_action.transaction_methods.transact()

#     consideration.approve_orders([order]).transact()
#     fulfill_action.transaction_methods.transact()
#     assert erc721.ownerOf(nft_id) == fulfiller


# def test_erc721_buy_now_with_erc20(
#     consideration: Consideration, erc721, erc20, offerer, zone, fulfiller
# ):
#     erc721.mint(offerer, nft_id)
#     erc20.mint(fulfiller, Web3.toWei(11, "ether"))
#     use_case = consideration.create_order(
#         account_address=offerer.address,
#         offer=[BasicOfferErc721Item(token=erc721.address, identifier=nft_id)],
#         consideration=[
#             ConsiderationCurrencyItem(
#                 amount=Web3.toWei(10, "ether"),
#                 recipient=offerer.address,
#                 token=erc20.address,
#             ),
#             ConsiderationCurrencyItem(
#                 amount=Web3.toWei(1, "ether"),
#                 recipient=zone.address,
#                 token=erc20.address,
#             ),
#         ],
#     )

#     order = use_case.execute_all_actions()

#     fulfill_order_use_case = consideration.fulfill_order(
#         order=order, account_address=fulfiller.address
#     )

#     actions = fulfill_order_use_case.actions
#     approval_action, fulfill_action = actions

#     assert approval_action.dict() == {
#         "type": "approval",
#         "token": erc20.address,
#         "identifier_or_criteria": 0,
#         "item_type": ItemType.ERC20.value,
#         "transaction_methods": approval_action.transaction_methods,
#         "operator": consideration.contract.address,
#     }

#     approval_action.transaction_methods.transact()
#     fulfill_action.transaction_methods.transact()

#     assert erc721.ownerOf(nft_id) == fulfiller


# def test_erc721_buy_now_with_erc20_offer_via_proxy(
#     consideration: Consideration,
#     erc721,
#     erc20,
#     offerer,
#     zone,
#     fulfiller,
#     legacy_proxy_registry,
# ):
#     erc721.mint(offerer, nft_id)
#     erc20.mint(fulfiller, Web3.toWei(11, "ether"))
#     legacy_proxy_registry.registerProxy({"from": offerer})
#     offerer_proxy = legacy_proxy_registry.proxies(offerer.address)
#     erc721.setApprovalForAll(offerer_proxy, True)
#     use_case = consideration.create_order(
#         account_address=offerer.address,
#         offer=[BasicOfferErc721Item(token=erc721.address, identifier=nft_id)],
#         consideration=[
#             ConsiderationCurrencyItem(
#                 amount=Web3.toWei(10, "ether"),
#                 recipient=offerer.address,
#                 token=erc20.address,
#             ),
#             ConsiderationCurrencyItem(
#                 amount=Web3.toWei(1, "ether"),
#                 recipient=zone.address,
#                 token=erc20.address,
#             ),
#         ],
#     )

#     order = use_case.execute_all_actions()
#     assert order.parameters.conduit == LEGACY_PROXY_CONDUIT

#     fulfill_order_use_case = consideration.fulfill_order(
#         order=order, account_address=fulfiller.address
#     )

#     actions = fulfill_order_use_case.actions
#     approval_action, fulfill_action = actions

#     assert approval_action.dict() == {
#         "type": "approval",
#         "token": erc20.address,
#         "identifier_or_criteria": 0,
#         "item_type": ItemType.ERC20.value,
#         "transaction_methods": approval_action.transaction_methods,
#         "operator": consideration.contract.address,
#     }

#     approval_action.transaction_methods.transact()
#     fulfill_action.transaction_methods.transact()

#     assert erc721.ownerOf(nft_id) == fulfiller


# def test_erc721_accept_offer(
#     consideration: Consideration, erc721, erc20, offerer, zone, fulfiller
# ):
#     erc721.mint(fulfiller, nft_id)
#     erc20.mint(offerer, Web3.toWei(11, "ether"))
#     use_case = consideration.create_order(
#         account_address=offerer.address,
#         offer=[
#             OfferCurrencyItem(
#                 amount=Web3.toWei(10, "ether"),
#                 token=erc20.address,
#             ),
#         ],
#         consideration=[
#             BasicConsiderationErc721Item(
#                 token=erc721.address, identifier=nft_id, recipient=offerer.address
#             ),
#             ConsiderationCurrencyItem(
#                 amount=Web3.toWei(1, "ether"),
#                 recipient=zone.address,
#                 token=erc20.address,
#             ),
#         ],
#     )

#     order = use_case.execute_all_actions()

#     fulfill_order_use_case = consideration.fulfill_order(
#         order=order, account_address=fulfiller.address
#     )

#     actions = fulfill_order_use_case.actions
#     approval_action, fulfill_action = actions

#     assert approval_action.dict() == {
#         "type": "approval",
#         "token": erc721.address,
#         "identifier_or_criteria": nft_id,
#         "item_type": ItemType.ERC721.value,
#         "transaction_methods": approval_action.transaction_methods,
#         "operator": consideration.contract.address,
#     }

#     approval_action.transaction_methods.transact()
#     fulfill_action.transaction_methods.transact()

#     assert erc721.ownerOf(nft_id) == offerer


def test_erc721_accept_offer_fulfilled_via_proxy(
    consideration: Consideration,
    erc721,
    erc20,
    offerer,
    zone,
    fulfiller,
    legacy_proxy_registry,
):
    erc721.mint(fulfiller, nft_id)
    erc20.mint(offerer, Web3.toWei(11, "ether"))
    legacy_proxy_registry.registerProxy({"from": fulfiller})
    fulfiller_proxy = legacy_proxy_registry.proxies(fulfiller.address)
    erc721.setApprovalForAll(fulfiller_proxy, True, {"from": fulfiller})

    use_case = consideration.create_order(
        account_address=offerer.address,
        offer=[
            OfferCurrencyItem(
                amount=Web3.toWei(10, "ether"),
                token=erc20.address,
            ),
        ],
        consideration=[
            BasicConsiderationErc721Item(
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

    fulfill_order_use_case = consideration.fulfill_order(
        order=order, account_address=fulfiller.address
    )

    actions = fulfill_order_use_case.actions
    assert len(actions) == 1

    fulfill_action = actions[0]

    fulfill_action.transaction_methods.transact()

    assert erc721.ownerOf(nft_id) == offerer
