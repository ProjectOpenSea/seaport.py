from enum import Enum, auto

from web3.constants import HASH_ZERO

CONSIDERATION_CONTRACT_NAME = "Seaport"
CONSIDERATION_CONTRACT_VERSION = "1.1"
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
        {"name": "zoneHash", "type": "bytes32"},
        {"name": "salt", "type": "uint256"},
        {"name": "conduitKey", "type": "bytes32"},
        {"name": "counter", "type": "uint256"},
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


class BasicOrderRouteType(Enum):
    ETH_TO_ERC721 = 0
    ETH_TO_ERC1155 = 1
    ERC20_TO_ERC721 = 2
    ERC20_TO_ERC1155 = 3
    ERC721_TO_ERC20 = 4
    ERC1155_TO_ERC20 = 5


class ProxyStrategy(Enum):
    IF_ZERO_APPROVALS_NEEDED = auto()
    NEVER = auto()
    ALWAYS = auto()


MAX_INT = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
ONE_HUNDRED_PERCENT_BP = 10000
NO_CONDUIT_KEY = HASH_ZERO
CROSS_CHAIN_SEAPORT_ADDRESS = "0x00000000006c3852cbef3e08e8df289169ede581"
