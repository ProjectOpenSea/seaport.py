from web3 import Web3
from consideration.consideration import Consideration
from consideration.constants import (
    MAX_INT,
)
from consideration.types import (
    BasicConsiderationErc721Item,
    BasicErc721Item,
    ConsiderationCurrencyItem,
    ConsiderationErc721Item,
    Erc721Item,
)
from consideration.utils.order import generate_random_salt

nft_id = 1


def test_erc721_buy_now(consideration: Consideration, erc721, offerer, zone, fulfiller):
    erc721.mint(offerer, nft_id)
    use_case = consideration.create_order(
        account_address=offerer.address,
        offer=[BasicErc721Item(token=erc721.address, identifier=nft_id)],
        consideration=[
            ConsiderationCurrencyItem(
                amount=Web3.toWei(10, "ether"), recipient=offerer.address
            )
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
