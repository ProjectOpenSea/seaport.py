from web3 import Web3
from consideration.consideration import Consideration
from consideration.constants import LEGACY_PROXY_CONDUIT
from consideration.types import (
    BasicOfferErc721Item,
    ConsiderationCurrencyItem,
)
from web3.constants import ADDRESS_ZERO


nft_id = 1


def test_erc721_buy_now(consideration: Consideration, erc721, offerer, zone, fulfiller):
    erc721.mint(offerer, nft_id)
    use_case = consideration.create_order(
        account_address=offerer.address,
        offer=[BasicOfferErc721Item(token=erc721.address, identifier=nft_id)],
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


def test_erc721_buy_now_offer_via_proxy(
    consideration: Consideration,
    erc721,
    offerer,
    zone,
    fulfiller,
    legacy_proxy_registry,
):
    erc721.mint(offerer, nft_id)

    legacy_proxy_registry.registerProxy({"from": offerer})

    offerer_proxy = legacy_proxy_registry.proxies(offerer.address)

    erc721.setApprovalForAll(offerer_proxy, True)

    use_case = consideration.create_order(
        account_address=offerer.address,
        offer=[BasicOfferErc721Item(token=erc721.address, identifier=nft_id)],
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
    assert order.parameters.conduit == LEGACY_PROXY_CONDUIT

    fulfill_order_use_case = consideration.fulfill_order(
        order=order, account_address=fulfiller.address
    )

    actions = fulfill_order_use_case.actions
    fulfill_action = actions[0]
    fulfill_action.transaction_methods.transact()

    assert erc721.ownerOf(nft_id) == fulfiller
