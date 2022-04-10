from enum import Enum, auto

CONSIDERATION_CONTRACT_NAME = "Consideration"
CONSIDERATION_CONTRACT_VERSION = "rc.1"
EIP_712_ORDER_TYPE = {
    "EIP712Domain": [
        {"name": "name", "type": "string"},
        {"name": "version", "type": "string"},
        {"name": "chainId", "type": "uint256"},
        {"name": "verifyingContract", "type": "address"},
    ],
    "OrderComponents": [
        {"name": "offerer", "type": "address"},
        {"name": "zone", "type": "address"},
        {"name": "offer", "type": "OfferItem[]"},
        {"name": "consideration", "type": "ConsiderationItem[]"},
        {"name": "orderType", "type": "uint8"},
        {"name": "startTime", "type": "uint256"},
        {"name": "endTime", "type": "uint256"},
        {"name": "salt", "type": "uint256"},
        {"name": "nonce", "type": "uint256"},
    ],
    "OfferItem": [
        {"name": "itemType", "type": "uint8"},
        {"name": "token", "type": "address"},
        {"name": "identifierOrCriteria", "type": "uint256"},
        {"name": "startAmount", "type": "uint256"},
        {"name": "endAmount", "type": "uint256"},
    ],
    "ConsiderationItem": [
        {"name": "itemType", "type": "uint8"},
        {"name": "token", "type": "address"},
        {"name": "identifierOrCriteria", "type": "uint256"},
        {"name": "startAmount", "type": "uint256"},
        {"name": "endAmount", "type": "uint256"},
        {"name": "recipient", "type": "address"},
    ],
}


class OrderType(Enum):
    FULL_OPEN = 0  # No partial fills, anyone can execute
    PARTIAL_OPEN = 1  # Partial fills supported, anyone can execute
    FULL_RESTRICTED = 2  # No partial fills, only offerer or zone can execute
    PARTIAL_RESTRICTED = 3  # Partial fills supported, only offerer or zone can execute
    FULL_OPEN_VIA_PROXY = (
        4  # No partial fills, anyone can execute, routed through proxy
    )
    PARTIAL_OPEN_VIA_PROXY = (
        5  # Partial fills supported, anyone can execute, routed through proxy
    )
    FULL_RESTRICTED_VIA_PROXY = (
        6  # No partial fills, only offerer or zone can execute, routed through proxy
    )
    PARTIAL_RESTRICTED_VIA_PROXY = 7  # Partial fills supported, only offerer or zone can execute, routed through proxy


class ItemType(Enum):
    NATIVE = 0
    ERC20 = 1
    ERC721 = 2
    ERC1155 = 3
    ERC721_WITH_CRITERIA = 4
    ERC1155_WITH_CRITERIA = 5


class Side(Enum):
    OFFER = 0
    CONSIDERATION = 1


class BasicFulfillOrder(Enum):
    ETH_FOR_ERC721 = auto()
    ETH_FOR_ERC1155 = auto()
    ERC20_FOR_ERC721 = auto()
    ERC20_FOR_ERC1155 = auto()
    ERC721_FOR_ERC20 = auto()
    ERC1155_FOR_ERC20 = auto()


MAX_INT = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
ONE_HUNDRED_PERCENT_BP = 10000
