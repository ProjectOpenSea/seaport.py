from web3 import Web3

from consideration.consideration import Consideration
from consideration.constants import ItemType
from consideration.types import (
    BasicConsiderationErc721Item,
    BasicConsiderationErc1155Item,
    BasicOfferErc721Item,
    BasicOfferErc1155Item,
    ConsiderationCurrencyItem,
    ConsiderationErc721ItemWithCriteria,
    InputCriteria,
    OfferCurrencyItem,
    OfferErc721ItemWithCriteria,
)

nft_id = 1
erc1155_amount = 3


def test_erc721_collection_based_listing(
    consideration: Consideration, erc721, offerer, zone, fulfiller
):
    erc721.mint(offerer, nft_id)

    use_case = consideration.create_order(
        account_address=offerer.address,
        offer=[
            OfferErc721ItemWithCriteria(
                token=erc721.address,
                identifiers=[],
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
        order=order,
        account_address=fulfiller.address,
        offer_criteria=[InputCriteria(identifier=nft_id, valid_identifiers=[])],
    )

    actions = fulfill_order_use_case.actions
    fulfill_action = actions[0]
    fulfill_action.transaction_methods.transact()

    assert erc721.ownerOf(nft_id) == fulfiller


def test_erc721_collection_based_offer(
    consideration: Consideration, erc721, erc20, offerer, zone, fulfiller
):
    erc721.mint(fulfiller, nft_id)
    erc20.mint(offerer, Web3.toWei(10, "ether"))

    use_case = consideration.create_order(
        account_address=offerer.address,
        offer=[
            OfferCurrencyItem(
                amount=Web3.toWei(10, "ether"),
                token=erc20.address,
            ),
        ],
        consideration=[
            ConsiderationErc721ItemWithCriteria(
                token=erc721.address,
                identifiers=[],
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
        order=order,
        account_address=fulfiller.address,
        consideration_criteria=[InputCriteria(identifier=nft_id, valid_identifiers=[])],
    )

    actions = fulfill_order_use_case.actions
    approval_action, erc20_approval_action, fulfill_action = actions
    assert approval_action.dict() == {
        "type": "approval",
        "token": erc721.address,
        "identifier_or_criteria": 1,
        "item_type": ItemType.ERC721_WITH_CRITERIA.value,
        "transaction_methods": approval_action.transaction_methods,
        "operator": consideration.contract.address,
    }
    approval_action.transaction_methods.transact()

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


def test_erc721_trait_based_listing():
    pass


def test_erc721_trait_based_offer():
    pass


def test_erc1155_collection_based_listing(
    consideration: Consideration, erc721, second_erc721, offerer, zone, fulfiller
):
    pass


def test_erc1155_collection_based_offer():
    pass


def test_erc1155_trait_based_listing():
    pass


def test_erc1155_trait_based_offer():
    pass


def test_erc721_for_erc1155_collection_based_swap(
    consideration: Consideration, erc721, second_erc721, offerer, zone, fulfiller
):
    pass


def test_erc721_for_erc1155_trait_based_swap():
    pass
