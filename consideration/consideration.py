from typing import Optional
from web3 import Web3
from web3.providers.base import BaseProvider
from brownie.network.account import Accounts

from consideration.types import ConsiderationConfig


class Consideration:
    web3: Web3
    # Provides the raw interface to the contract for flexibility
    # _contract: ConsiderationContract;

    # private provider: providers.JsonRpcProvider;

    # Use the multicall provider for reads for batching and performance optimisations
    # NOTE: Do NOT await between sequential requests if you're intending to batch
    # instead, use Promise.all() and map to fetch data in parallel
    # https://www.npmjs.com/package/@0xsequence/multicall
    # private multicallProvider: multicallProviders.MulticallProvider;

    config: ConsiderationConfig
    legacy_proxy_registry_address: str

    def __init__(
        self,
        provider: BaseProvider,
        config: ConsiderationConfig = ConsiderationConfig(),
    ):
        self.web3 = Web3(provider=provider)
        self.config = config
        self.legacy_proxy_registry_address = (
            config.overrides.legacy_proxy_registry_address or ""
        )
