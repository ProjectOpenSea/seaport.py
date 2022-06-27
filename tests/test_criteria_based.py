import pytest
from web3 import Web3

from seaport.constants import ItemType
from seaport.seaport import Seaport
from seaport.types import (
    ConsiderationCurrencyItem,
    ConsiderationErc721ItemWithCriteria,
    ConsiderationErc1155ItemWithCriteria,
    InputCriteria,
    OfferCurrencyItem,
    OfferErc721ItemWithCriteria,
    OfferErc1155ItemWithCriteria,
)
from seaport.utils.merkletree import MerkleTree

nft_id = 1
nft_id2 = 2
nft_id3 = 3

erc1155_amount = 3


def test_erc721_collection_based_listing(
    seaport: Seaport, erc721, offerer, zone, fulfiller
):
    erc721.mint(offerer, nft_id)

    use_case = seaport.create_order(
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

    fulfill_order_use_case = seaport.fulfill_order(
        order=order,
        account_address=fulfiller.address,
        offer_criteria=[InputCriteria(identifier=nft_id, proof=[])],
    )

    actions = fulfill_order_use_case.actions
    fulfill_action = actions[0]
    fulfill_action.transaction_methods.transact()

    assert erc721.ownerOf(nft_id) == fulfiller


def test_erc721_collection_based_offer(
    seaport: Seaport, erc721, erc20, offerer, zone, fulfiller
):
    erc721.mint(fulfiller, nft_id)
    erc20.mint(offerer, Web3.toWei(10, "ether"))

    use_case = seaport.create_order(
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

    fulfill_order_use_case = seaport.fulfill_order(
        order=order,
        account_address=fulfiller.address,
        consideration_criteria=[InputCriteria(identifier=nft_id, proof=[])],
    )

    actions = fulfill_order_use_case.actions
    approval_action, erc20_approval_action, fulfill_action = actions
    assert approval_action.dict() == {
        "type": "approval",
        "token": erc721.address,
        "identifier_or_criteria": 1,
        "item_type": ItemType.ERC721_WITH_CRITERIA.value,
        "transaction_methods": approval_action.transaction_methods,
        "operator": seaport.contract.address,
    }
    approval_action.transaction_methods.transact()

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

    assert erc721.ownerOf(nft_id) == offerer


def test_erc721_trait_based_listing(seaport: Seaport, erc721, offerer, zone, fulfiller):
    erc721.mint(offerer, nft_id)
    erc721.mint(offerer, nft_id2)
    erc721.mint(offerer, nft_id3)

    use_case = seaport.create_order(
        account_address=offerer.address,
        offer=[
            OfferErc721ItemWithCriteria(
                token=erc721.address,
                identifiers=[nft_id, nft_id3],
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

    reverted_use_case = seaport.fulfill_order(
        order=order,
        account_address=fulfiller.address,
        offer_criteria=[
            InputCriteria(
                identifier=nft_id2, proof=MerkleTree([nft_id2]).get_proof(nft_id2)
            )
        ],
    )

    reverted_fulfill_action = reverted_use_case.actions[0]
    with pytest.raises(ValueError):
        reverted_fulfill_action.transaction_methods.transact()

    fulfill_order_use_case = seaport.fulfill_order(
        order=order,
        account_address=fulfiller.address,
        offer_criteria=[
            InputCriteria(
                identifier=nft_id3,
                proof=MerkleTree([nft_id, nft_id3]).get_proof(nft_id3),
            )
        ],
    )

    actions = fulfill_order_use_case.actions
    fulfill_action = actions[0]
    fulfill_action.transaction_methods.transact()

    assert erc721.ownerOf(nft_id3) == fulfiller


def test_erc721_trait_based_offer(
    seaport: Seaport, erc721, erc20, offerer, zone, fulfiller
):
    erc721.mint(fulfiller, nft_id)
    erc721.mint(fulfiller, nft_id2)
    erc721.mint(fulfiller, nft_id3)
    erc20.mint(offerer, Web3.toWei(10, "ether"))

    use_case = seaport.create_order(
        account_address=offerer.address,
        offer=[OfferCurrencyItem(amount=Web3.toWei(10, "ether"), token=erc20.address)],
        consideration=[
            ConsiderationErc721ItemWithCriteria(
                token=erc721.address,
                identifiers=[nft_id, nft_id3],
            ),
            ConsiderationCurrencyItem(
                amount=Web3.toWei(1, "ether"),
                recipient=zone.address,
                token=erc20.address,
            ),
        ],
    )

    order = use_case.execute_all_actions()

    reverted_use_case = seaport.fulfill_order(
        order=order,
        account_address=fulfiller.address,
        consideration_criteria=[
            InputCriteria(
                identifier=nft_id2, proof=MerkleTree([nft_id2]).get_proof(nft_id2)
            )
        ],
    )

    (
        approval_action,
        erc20_approval_action,
        reverted_fulfill_action,
    ) = reverted_use_case.actions

    assert approval_action.dict() == {
        "type": "approval",
        "token": erc721.address,
        "identifier_or_criteria": nft_id2,
        "item_type": ItemType.ERC721_WITH_CRITERIA.value,
        "transaction_methods": approval_action.transaction_methods,
        "operator": seaport.contract.address,
    }

    approval_action.transaction_methods.transact()

    assert erc20_approval_action.dict() == {
        "type": "approval",
        "token": erc20.address,
        "identifier_or_criteria": 0,
        "item_type": ItemType.ERC20.value,
        "transaction_methods": erc20_approval_action.transaction_methods,
        "operator": seaport.contract.address,
    }

    erc20_approval_action.transaction_methods.transact()

    with pytest.raises(ValueError):
        reverted_fulfill_action.transaction_methods.transact()

    fulfill_order_use_case = seaport.fulfill_order(
        order=order,
        account_address=fulfiller.address,
        consideration_criteria=[
            InputCriteria(
                identifier=nft_id, proof=MerkleTree([nft_id, nft_id3]).get_proof(nft_id)
            )
        ],
    )

    actions = fulfill_order_use_case.actions
    fulfill_action = actions[0]
    fulfill_action.transaction_methods.transact()

    assert erc721.ownerOf(nft_id) == offerer


def test_erc1155_collection_based_listing(
    seaport: Seaport, erc1155, offerer, zone, fulfiller
):
    erc1155.mint(offerer, nft_id, erc1155_amount)

    use_case = seaport.create_order(
        account_address=offerer.address,
        offer=[
            OfferErc1155ItemWithCriteria(
                token=erc1155.address, identifiers=[], amount=erc1155_amount
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

    fulfill_order_use_case = seaport.fulfill_order(
        order=order,
        account_address=fulfiller.address,
        offer_criteria=[InputCriteria(identifier=nft_id, proof=[])],
    )

    actions = fulfill_order_use_case.actions
    fulfill_action = actions[0]
    fulfill_action.transaction_methods.transact()

    assert erc1155.balanceOf(fulfiller, nft_id) == erc1155_amount


def test_erc1155_collection_based_offer(
    seaport: Seaport, erc1155, erc20, offerer, zone, fulfiller
):
    erc1155.mint(fulfiller, nft_id, erc1155_amount)
    erc20.mint(offerer, Web3.toWei(10, "ether"))

    use_case = seaport.create_order(
        account_address=offerer.address,
        offer=[
            OfferCurrencyItem(
                amount=Web3.toWei(10, "ether"),
                token=erc20.address,
            ),
        ],
        consideration=[
            ConsiderationErc1155ItemWithCriteria(
                token=erc1155.address, identifiers=[], amount=erc1155_amount
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
        order=order,
        account_address=fulfiller.address,
        consideration_criteria=[InputCriteria(identifier=nft_id, proof=[])],
    )

    actions = fulfill_order_use_case.actions
    approval_action, erc20_approval_action, fulfill_action = actions
    assert approval_action.dict() == {
        "type": "approval",
        "token": erc1155.address,
        "identifier_or_criteria": nft_id,
        "item_type": ItemType.ERC1155_WITH_CRITERIA.value,
        "transaction_methods": approval_action.transaction_methods,
        "operator": seaport.contract.address,
    }
    approval_action.transaction_methods.transact()

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

    assert erc1155.balanceOf(offerer, nft_id) == erc1155_amount


def test_erc1155_trait_based_listing(
    seaport: Seaport, erc1155, offerer, zone, fulfiller
):
    erc1155.mint(offerer, nft_id, erc1155_amount)
    erc1155.mint(offerer, nft_id2, erc1155_amount)
    erc1155.mint(offerer, nft_id3, erc1155_amount)

    use_case = seaport.create_order(
        account_address=offerer.address,
        offer=[
            OfferErc1155ItemWithCriteria(
                token=erc1155.address,
                identifiers=[nft_id, nft_id3],
                amount=erc1155_amount,
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

    reverted_use_case = seaport.fulfill_order(
        order=order,
        account_address=fulfiller.address,
        offer_criteria=[
            InputCriteria(
                identifier=nft_id2, proof=MerkleTree([nft_id2]).get_proof(nft_id2)
            )
        ],
    )

    reverted_fulfill_action = reverted_use_case.actions[0]
    with pytest.raises(ValueError):
        reverted_fulfill_action.transaction_methods.transact()

    fulfill_order_use_case = seaport.fulfill_order(
        order=order,
        account_address=fulfiller.address,
        offer_criteria=[
            InputCriteria(
                identifier=nft_id3,
                proof=MerkleTree([nft_id, nft_id3]).get_proof(nft_id3),
            )
        ],
    )

    actions = fulfill_order_use_case.actions
    fulfill_action = actions[0]
    fulfill_action.transaction_methods.transact()

    assert erc1155.balanceOf(fulfiller, nft_id3) == erc1155_amount


def test_erc1155_trait_based_offer(
    seaport: Seaport, erc1155, erc20, offerer, zone, fulfiller
):
    erc1155.mint(fulfiller, nft_id, erc1155_amount)
    erc1155.mint(fulfiller, nft_id2, erc1155_amount)
    erc1155.mint(fulfiller, nft_id3, erc1155_amount)
    erc20.mint(offerer, Web3.toWei(10, "ether"))

    use_case = seaport.create_order(
        account_address=offerer.address,
        offer=[OfferCurrencyItem(amount=Web3.toWei(10, "ether"), token=erc20.address)],
        consideration=[
            ConsiderationErc1155ItemWithCriteria(
                token=erc1155.address,
                identifiers=[nft_id, nft_id3],
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

    reverted_use_case = seaport.fulfill_order(
        order=order,
        account_address=fulfiller.address,
        consideration_criteria=[
            InputCriteria(
                identifier=nft_id2, proof=MerkleTree([nft_id2]).get_proof(nft_id2)
            )
        ],
    )

    (
        approval_action,
        erc20_approval_action,
        reverted_fulfill_action,
    ) = reverted_use_case.actions

    assert approval_action.dict() == {
        "type": "approval",
        "token": erc1155.address,
        "identifier_or_criteria": nft_id2,
        "item_type": ItemType.ERC1155_WITH_CRITERIA.value,
        "transaction_methods": approval_action.transaction_methods,
        "operator": seaport.contract.address,
    }

    approval_action.transaction_methods.transact()

    assert erc20_approval_action.dict() == {
        "type": "approval",
        "token": erc20.address,
        "identifier_or_criteria": 0,
        "item_type": ItemType.ERC20.value,
        "transaction_methods": erc20_approval_action.transaction_methods,
        "operator": seaport.contract.address,
    }

    erc20_approval_action.transaction_methods.transact()

    with pytest.raises(ValueError):
        reverted_fulfill_action.transaction_methods.transact()

    fulfill_order_use_case = seaport.fulfill_order(
        order=order,
        account_address=fulfiller.address,
        consideration_criteria=[
            InputCriteria(
                identifier=nft_id, proof=MerkleTree([nft_id, nft_id3]).get_proof(nft_id)
            )
        ],
    )

    actions = fulfill_order_use_case.actions
    fulfill_action = actions[0]
    fulfill_action.transaction_methods.transact()

    assert erc1155.balanceOf(offerer, nft_id) == erc1155_amount


def test_erc721_for_erc1155_collection_based_swap(
    seaport: Seaport, erc721, erc1155, offerer, fulfiller
):
    erc721.mint(offerer, nft_id)
    erc721.mint(offerer, nft_id2)
    erc721.mint(offerer, nft_id3)
    erc1155.mint(fulfiller, nft_id, erc1155_amount)
    erc1155.mint(fulfiller, nft_id2, erc1155_amount)
    erc1155.mint(fulfiller, nft_id3, erc1155_amount)

    use_case = seaport.create_order(
        account_address=offerer.address,
        offer=[
            OfferErc721ItemWithCriteria(
                token=erc721.address,
                identifiers=[],
            ),
        ],
        consideration=[
            ConsiderationErc1155ItemWithCriteria(
                token=erc1155.address,
                identifiers=[],
                amount=erc1155_amount,
            )
        ],
    )

    order = use_case.execute_all_actions()

    fulfill_use_case = seaport.fulfill_order(
        order=order,
        account_address=fulfiller.address,
        offer_criteria=[InputCriteria(identifier=nft_id, proof=[])],
        consideration_criteria=[InputCriteria(identifier=nft_id2, proof=[])],
    )

    approval_action, fulfill_action = fulfill_use_case.actions

    assert approval_action.dict() == {
        "type": "approval",
        "token": erc1155.address,
        "identifier_or_criteria": nft_id2,
        "item_type": ItemType.ERC1155_WITH_CRITERIA.value,
        "transaction_methods": approval_action.transaction_methods,
        "operator": seaport.contract.address,
    }

    approval_action.transaction_methods.transact()

    fulfill_action.transaction_methods.transact()

    assert erc721.ownerOf(nft_id) == fulfiller
    assert erc1155.balanceOf(offerer, nft_id2) == erc1155_amount


def test_erc721_for_erc1155_trait_based_swap(
    seaport: Seaport, erc721, erc1155, offerer, fulfiller
):
    erc721.mint(offerer, nft_id)
    erc721.mint(offerer, nft_id2)
    erc721.mint(offerer, nft_id3)
    erc1155.mint(fulfiller, nft_id, erc1155_amount)
    erc1155.mint(fulfiller, nft_id2, erc1155_amount)
    erc1155.mint(fulfiller, nft_id3, erc1155_amount)

    use_case = seaport.create_order(
        account_address=offerer.address,
        offer=[
            OfferErc721ItemWithCriteria(
                token=erc721.address,
                identifiers=[nft_id, nft_id3],
            ),
        ],
        consideration=[
            ConsiderationErc1155ItemWithCriteria(
                token=erc1155.address,
                identifiers=[nft_id2, nft_id3],
                amount=erc1155_amount,
            )
        ],
    )

    order = use_case.execute_all_actions()

    reverted_use_case = seaport.fulfill_order(
        order=order,
        account_address=fulfiller.address,
        offer_criteria=[
            InputCriteria(
                identifier=nft_id, proof=MerkleTree([nft_id, nft_id3]).get_proof(nft_id)
            )
        ],
        consideration_criteria=[
            InputCriteria(
                identifier=nft_id2, proof=MerkleTree([nft_id2]).get_proof(nft_id2)
            )
        ],
    )

    approval_action, reverted_fulfill = reverted_use_case.actions

    assert approval_action.dict() == {
        "type": "approval",
        "token": erc1155.address,
        "identifier_or_criteria": nft_id2,
        "item_type": ItemType.ERC1155_WITH_CRITERIA.value,
        "transaction_methods": approval_action.transaction_methods,
        "operator": seaport.contract.address,
    }

    approval_action.transaction_methods.transact()

    with pytest.raises(ValueError):
        reverted_fulfill.transaction_methods.transact()

    fulfill_use_case = seaport.fulfill_order(
        order=order,
        account_address=fulfiller.address,
        offer_criteria=[
            InputCriteria(
                identifier=nft_id, proof=MerkleTree([nft_id, nft_id3]).get_proof(nft_id)
            )
        ],
        consideration_criteria=[
            InputCriteria(
                identifier=nft_id2,
                proof=MerkleTree([nft_id2, nft_id3]).get_proof(nft_id2),
            )
        ],
    )

    fulfill_action = fulfill_use_case.actions[0]

    fulfill_action.transaction_methods.transact()

    assert erc721.ownerOf(nft_id) == fulfiller
    assert erc1155.balanceOf(offerer, nft_id2) == erc1155_amount
