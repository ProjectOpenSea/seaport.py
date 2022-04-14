from eth_utils.currency import to_wei
from web3.constants import ADDRESS_ZERO
from consideration.consideration import Consideration
from consideration.constants import MAX_INT, ItemType, OrderType
from consideration.types import (
    ApprovalAction,
    BasicErc721Item,
    ConsiderationCurrencyItem,
    CreateOrderAction,
    CurrencyItem,
    Fee,
)
from consideration.utils.order import generate_random_salt

nft_id = 1
start_time = 0
end_time = MAX_INT
salt = generate_random_salt()


def test_create_order_after_setting_approvals(
    consideration: Consideration, erc721, offerer, zone, fulfiller
):
    erc721.mint(offerer, nft_id)
    use_case = consideration.create_order(
        start_time=start_time,
        end_time=end_time,
        salt=salt,
        offer=[BasicErc721Item(token=erc721.address, identifier=nft_id)],
        consideration=[ConsiderationCurrencyItem(amount=to_wei(10, "ether"))],
        fees=[Fee(recipient=zone.address, basis_points=250)],
    )

    actions = use_case.actions
    approval_action, create_order_action = actions

    assert isinstance(approval_action, ApprovalAction)
    assert approval_action.dict() == {
        "type": "approval",
        "token": erc721.address,
        "identifier_or_criteria": nft_id,
        "item_type": ItemType.ERC721.value,
        "transaction": approval_action.transaction,
        "operator": consideration.contract.address,
    }

    approval_action.transaction.transact()

    assert erc721.isApprovedForAll(offerer, consideration.contract.address)

    assert isinstance(create_order_action, CreateOrderAction)

    order = create_order_action.create_order()
    order_dict = order.dict()

    assert order_dict == {
        "parameters": {
            "consideration": [
                {
                    # Fees were deducted
                    "endAmount": to_wei(9.75, "ether"),
                    "identifierOrCriteria": 0,
                    "itemType": ItemType.NATIVE.value,
                    "recipient": offerer,
                    "startAmount": to_wei(9.75, "ether"),
                    "token": ADDRESS_ZERO,
                },
                {
                    "endAmount": to_wei(0.25, "ether"),
                    "identifierOrCriteria": 0,
                    "itemType": ItemType.NATIVE.value,
                    "recipient": zone,
                    "startAmount": to_wei(0.25, "ether"),
                    "token": ADDRESS_ZERO,
                },
            ],
            "endTime": end_time,
            "offer": [
                {
                    "endAmount": 1,
                    "identifierOrCriteria": nft_id,
                    "itemType": ItemType.ERC721.value,
                    "startAmount": 1,
                    "token": erc721.address,
                },
            ],
            "offerer": offerer.address,
            "orderType": OrderType.FULL_OPEN.value,
            "salt": salt,
            "startTime": start_time,
            "totalOriginalConsiderationItems": 2,
            "zone": ADDRESS_ZERO,
        },
        "signature": order.signature,
        "nonce": 0,
    }

    is_valid = consideration.contract.functions.validate([order_dict]).call(
        {"from": fulfiller.address}
    )

    assert is_valid


def test_create_order_offer_erc20_for_erc721(erc20, accounts):
    erc20.mint(accounts[0], 1e18)
    print(erc20.balanceOf(accounts[0]))

    assert erc20.balanceOf(accounts[0]) == 1e18
