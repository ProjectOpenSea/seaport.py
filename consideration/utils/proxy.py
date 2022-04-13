from audioop import add
from enum import Enum, auto

from web3 import Web3

from consideration.abi.ProxyRegistryInterface import PROXY_REGISTRY_INTERFACE_ABI


class ProxyStrategy(Enum):
    IF_ZERO_APPROVALS_NEEDED = auto()
    NEVER = auto()
    ALWAYS = auto()


def get_proxy(
    address: str,
    legacy_proxy_registry_address: str,
    web3: Web3,
):
    proxy_registry = web3.eth.contract(
        address=Web3.toChecksumAddress(legacy_proxy_registry_address),
        abi=PROXY_REGISTRY_INTERFACE_ABI,
    )

    return proxy_registry.functions.proxies(address).call()
