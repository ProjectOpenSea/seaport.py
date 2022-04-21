import pytest
from web3 import Web3
from consideration.consideration import Consideration
from consideration.constants import (
    LEGACY_PROXY_CONDUIT,
    MAX_INT,
    ItemType,
    OrderType,
    ProxyStrategy,
)
from consideration.types import (
    ApprovalAction,
    BasicConsiderationErc721Item,
    BasicErc1155Item,
    BasicOfferErc721Item,
    ConsiderationConfig,
    ConsiderationCurrencyItem,
    ContractOverrides,
    CreateOrderAction,
    OfferCurrencyItem,
    Fee,
)
from consideration.utils.order import generate_random_salt
from eth_utils.currency import to_wei
from web3.constants import ADDRESS_ZERO

nft_id = 1
start_time = 0
end_time = MAX_INT
salt = generate_random_salt()


def test_create_order_success(
    consideration: Consideration, erc721, offerer, zone, fulfiller
):
    erc721.mint(offerer, nft_id)
    use_case = consideration.create_order(
        start_time=start_time,
        end_time=end_time,
        salt=salt,
        offer=[BasicOfferErc721Item(token=erc721.address, identifier=nft_id)],
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
        "transaction_methods": approval_action.transaction_methods,
        "operator": consideration.contract.address,
    }

    approval_action.transaction_methods.transact()

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
            "zoneHash": "0x0000000000000000000000000000000000000000000000000000000000000000",
            "conduit": ADDRESS_ZERO,
        },
        "signature": order.signature,
        "nonce": 0,
    }

    is_valid = consideration.contract.functions.validate([order_dict]).call(
        {"from": fulfiller.address}
    )

    assert is_valid


def test_create_order_offer_erc20_for_erc721(
    consideration: Consideration, erc20, erc721, offerer, zone, fulfiller
):
    erc20.mint(offerer, to_wei(10, "ether"))
    use_case = consideration.create_order(
        start_time=start_time,
        end_time=end_time,
        salt=salt,
        offer=[OfferCurrencyItem(amount=to_wei(10, "ether"), token=erc20.address)],
        consideration=[
            BasicConsiderationErc721Item(token=erc721.address, identifier=nft_id)
        ],
        fees=[Fee(recipient=zone.address, basis_points=250)],
    )

    actions = use_case.actions
    approval_action, create_order_action = actions

    assert isinstance(approval_action, ApprovalAction)
    assert approval_action.dict() == {
        "type": "approval",
        "token": erc20.address,
        "identifier_or_criteria": 0,
        "item_type": ItemType.ERC20.value,
        "transaction_methods": approval_action.transaction_methods,
        "operator": consideration.contract.address,
    }

    approval_action.transaction_methods.transact()

    assert erc20.allowance(offerer, consideration.contract.address) == MAX_INT

    assert isinstance(create_order_action, CreateOrderAction)

    order = create_order_action.create_order()
    order_dict = order.dict()

    assert order_dict == {
        "parameters": {
            "consideration": [
                {
                    "endAmount": 1,
                    "identifierOrCriteria": nft_id,
                    "itemType": ItemType.ERC721.value,
                    "startAmount": 1,
                    "token": erc721.address,
                    "recipient": offerer,
                },
                {
                    "endAmount": to_wei(0.25, "ether"),
                    "identifierOrCriteria": 0,
                    "itemType": ItemType.ERC20.value,
                    "recipient": zone,
                    "startAmount": to_wei(0.25, "ether"),
                    "token": erc20.address,
                },
            ],
            "endTime": end_time,
            "offer": [
                {
                    # Fees were deducted
                    "endAmount": to_wei(10, "ether"),
                    "identifierOrCriteria": 0,
                    "itemType": ItemType.ERC20.value,
                    "startAmount": to_wei(10, "ether"),
                    "token": erc20.address,
                },
            ],
            "offerer": offerer.address,
            "orderType": OrderType.FULL_OPEN.value,
            "salt": salt,
            "startTime": start_time,
            "totalOriginalConsiderationItems": 2,
            "zone": ADDRESS_ZERO,
            "zoneHash": "0x0000000000000000000000000000000000000000000000000000000000000000",
            "conduit": ADDRESS_ZERO,
        },
        "signature": order.signature,
        "nonce": 0,
    }

    is_valid = consideration.contract.functions.validate([order_dict]).call(
        {"from": fulfiller.address}
    )

    assert is_valid


def test_create_order_offer_erc20_and_erc1155(
    consideration: Consideration,
    erc721,
    offerer,
    zone,
    fulfiller,
    erc1155,
):
    erc721.mint(offerer, nft_id)
    erc1155.mint(offerer, nft_id, 1)

    use_case = consideration.create_order(
        start_time=start_time,
        end_time=end_time,
        salt=salt,
        offer=[
            BasicOfferErc721Item(token=erc721.address, identifier=nft_id),
            BasicErc1155Item(token=erc1155.address, identifier=nft_id, amount=1),
        ],
        consideration=[ConsiderationCurrencyItem(amount=to_wei(10, "ether"))],
        fees=[Fee(recipient=zone.address, basis_points=250)],
    )

    actions = use_case.actions
    approval_action, second_approval_action, create_order_action = actions

    assert isinstance(approval_action, ApprovalAction)

    assert approval_action.dict() == {
        "type": "approval",
        "token": erc721.address,
        "identifier_or_criteria": nft_id,
        "item_type": ItemType.ERC721.value,
        "transaction_methods": approval_action.transaction_methods,
        "operator": consideration.contract.address,
    }

    approval_action.transaction_methods.transact()

    assert erc721.isApprovedForAll(offerer, consideration.contract.address)

    assert isinstance(second_approval_action, ApprovalAction)

    assert second_approval_action.dict() == {
        "type": "approval",
        "token": erc1155.address,
        "identifier_or_criteria": nft_id,
        "item_type": ItemType.ERC1155.value,
        "transaction_methods": second_approval_action.transaction_methods,
        "operator": consideration.contract.address,
    }

    second_approval_action.transaction_methods.transact()

    assert erc1155.isApprovedForAll(offerer, consideration.contract.address)

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
                {
                    "endAmount": 1,
                    "identifierOrCriteria": nft_id,
                    "itemType": ItemType.ERC1155.value,
                    "startAmount": 1,
                    "token": erc1155.address,
                },
            ],
            "offerer": offerer.address,
            "orderType": OrderType.FULL_OPEN.value,
            "salt": salt,
            "startTime": start_time,
            "totalOriginalConsiderationItems": 2,
            "zone": ADDRESS_ZERO,
            "zoneHash": "0x0000000000000000000000000000000000000000000000000000000000000000",
            "conduit": ADDRESS_ZERO,
        },
        "signature": order.signature,
        "nonce": 0,
    }

    is_valid = consideration.contract.functions.validate([order_dict]).call(
        {"from": fulfiller.address}
    )

    assert is_valid


def test_raises_if_currencies_are_different(
    consideration: Consideration,
    erc721,
    erc20,
    offerer,
    zone,
):
    erc721.mint(offerer, nft_id)
    erc20.mint(offerer, 1)

    with pytest.raises(
        ValueError, match="All currency tokens in the order must be the same token"
    ):
        consideration.create_order(
            start_time=start_time,
            end_time=end_time,
            salt=salt,
            offer=[BasicOfferErc721Item(token=erc721.address, identifier=nft_id)],
            consideration=[
                ConsiderationCurrencyItem(amount=to_wei(10, "ether")),
                ConsiderationCurrencyItem(amount=1, token=erc20.address),
            ],
            fees=[Fee(recipient=zone.address, basis_points=250)],
        )


def test_raises_if_offerer_insufficient_balance(
    consideration: Consideration, erc721, offerer, zone
):
    erc721.mint(zone, nft_id)

    with pytest.raises(
        ValueError,
        match="The offerer does not have the amount needed to create or fulfill",
    ):
        consideration.create_order(
            start_time=start_time,
            end_time=end_time,
            salt=salt,
            offer=[BasicOfferErc721Item(token=erc721.address, identifier=nft_id)],
            consideration=[
                ConsiderationCurrencyItem(amount=to_wei(10, "ether")),
            ],
            fees=[Fee(recipient=zone.address, basis_points=250)],
            account_address=offerer.address,
        )


def test_skip_balance_and_approval_validation_if_config_skips(
    consideration_contract,
    legacy_proxy_registry,
    erc721,
    offerer,
    zone,
    fulfiller,
):
    consideration = Consideration(
        provider=Web3.HTTPProvider("http://127.0.0.1:8545"),
        config=ConsiderationConfig(
            overrides=ContractOverrides(
                contract_address=consideration_contract.address,
                legacy_proxy_registry_address=legacy_proxy_registry.address,
            ),
            balance_and_approval_checks_on_order_creation=False,
        ),
    )

    erc721.mint(fulfiller, nft_id)

    use_case = consideration.create_order(
        start_time=start_time,
        end_time=end_time,
        salt=salt,
        offer=[BasicOfferErc721Item(token=erc721.address, identifier=nft_id)],
        consideration=[ConsiderationCurrencyItem(amount=to_wei(10, "ether"))],
        fees=[Fee(recipient=zone.address, basis_points=250)],
    )

    actions = use_case.actions
    create_order_action = actions[0]

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
            "zoneHash": "0x0000000000000000000000000000000000000000000000000000000000000000",
            "conduit": ADDRESS_ZERO,
        },
        "signature": order.signature,
        "nonce": 0,
    }

    is_valid = consideration.contract.functions.validate([order_dict]).call(
        {"from": fulfiller.address}
    )

    assert is_valid


def test_use_proxy_if_zero_approvals(
    consideration: Consideration,
    erc20,
    erc721,
    offerer,
    zone,
    fulfiller,
    legacy_proxy_registry,
):
    erc721.mint(offerer, nft_id)

    # Register the proxy on the user
    legacy_proxy_registry.registerProxy({"from": offerer})
    offerer_proxy = legacy_proxy_registry.proxies(offerer)

    # Nft should now be approved for proxy
    erc721.setApprovalForAll(offerer_proxy, True)

    use_case = consideration.create_order(
        start_time=start_time,
        end_time=end_time,
        salt=salt,
        offer=[BasicOfferErc721Item(token=erc721.address, identifier=nft_id)],
        consideration=[ConsiderationCurrencyItem(amount=to_wei(10, "ether"))],
        fees=[Fee(recipient=zone.address, basis_points=250)],
    )

    actions = use_case.actions
    create_order_action = actions[0]

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
            "conduit": LEGACY_PROXY_CONDUIT,
            "zoneHash": "0x0000000000000000000000000000000000000000000000000000000000000000",
        },
        "signature": order.signature,
        "nonce": 0,
    }

    is_valid = consideration.contract.functions.validate([order_dict]).call(
        {"from": fulfiller.address}
    )

    assert is_valid


def test_should_not_use_proxy_if_proxy_strategy_is_never(
    consideration_contract,
    erc721,
    offerer,
    zone,
    fulfiller,
    legacy_proxy_registry,
):
    consideration = Consideration(
        provider=Web3.HTTPProvider("http://127.0.0.1:8545"),
        config=ConsiderationConfig(
            overrides=ContractOverrides(
                contract_address=consideration_contract.address,
                legacy_proxy_registry_address=legacy_proxy_registry.address,
            ),
            proxy_strategy=ProxyStrategy.NEVER,
        ),
    )

    erc721.mint(offerer, nft_id)

    # Register the proxy on the user
    legacy_proxy_registry.registerProxy({"from": offerer})
    offerer_proxy = legacy_proxy_registry.proxies(offerer)

    # Nft should now be approved for proxy
    erc721.setApprovalForAll(offerer_proxy, True)

    use_case = consideration.create_order(
        start_time=start_time,
        end_time=end_time,
        salt=salt,
        offer=[BasicOfferErc721Item(token=erc721.address, identifier=nft_id)],
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
        "transaction_methods": approval_action.transaction_methods,
        "operator": consideration.contract.address,
    }

    approval_action.transaction_methods.transact()

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
            "zoneHash": "0x0000000000000000000000000000000000000000000000000000000000000000",
            "conduit": ADDRESS_ZERO,
        },
        "signature": order.signature,
        "nonce": 0,
    }

    is_valid = consideration.contract.functions.validate([order_dict]).call(
        {"from": fulfiller.address}
    )

    assert is_valid


def test_should_always_use_proxy_if_proxy_strategy_is_always(
    consideration_contract,
    erc721,
    offerer,
    zone,
    fulfiller,
    legacy_proxy_registry,
):
    consideration = Consideration(
        provider=Web3.HTTPProvider("http://127.0.0.1:8545"),
        config=ConsiderationConfig(
            overrides=ContractOverrides(
                contract_address=consideration_contract.address,
                legacy_proxy_registry_address=legacy_proxy_registry.address,
            ),
            proxy_strategy=ProxyStrategy.ALWAYS,
        ),
    )

    erc721.mint(offerer, nft_id)

    # Register the proxy on the user
    legacy_proxy_registry.registerProxy({"from": offerer})
    offerer_proxy = legacy_proxy_registry.proxies(offerer)

    # Nft should now be approved for user
    erc721.setApprovalForAll(consideration_contract.address, True, {"from": offerer})

    use_case = consideration.create_order(
        start_time=start_time,
        end_time=end_time,
        salt=salt,
        offer=[BasicOfferErc721Item(token=erc721.address, identifier=nft_id)],
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
        "transaction_methods": approval_action.transaction_methods,
        "operator": offerer_proxy,
    }

    approval_action.transaction_methods.transact()

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
            "zoneHash": "0x0000000000000000000000000000000000000000000000000000000000000000",
            "conduit": LEGACY_PROXY_CONDUIT,
        },
        "signature": order.signature,
        "nonce": 0,
    }

    is_valid = consideration.contract.functions.validate([order_dict]).call(
        {"from": fulfiller.address}
    )

    assert is_valid
