from typing import Optional, Type

from brownie import ZERO_ADDRESS
from brownie.network.account import Accounts
from eth_account.messages import encode_structured_data
from web3 import Web3
from web3.contract import Contract
from web3.providers.base import BaseProvider
from web3.types import RPCEndpoint

from consideration.abi.Consideration import CONSIDERATION_ABI
from consideration.constants import (CONSIDERATION_CONTRACT_NAME,
                                     CONSIDERATION_CONTRACT_VERSION,
                                     EIP_712_ORDER_TYPE)
from consideration.types import (ConsiderationConfig, Order, OrderParameters,
                                 TransactionRequest)
from consideration.utils.pydantic import dict_int_to_str, parse_model_list


class Consideration:
    contract: Contract
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
        self.contract = self.web3.eth.contract(
            address=config.overrides.contract_address
            or Web3.toChecksumAddress(ZERO_ADDRESS),
            abi=CONSIDERATION_ABI,
        )

    def get_nonce(self, offerer: str, zone: str) -> int:
        return self.contract.functions.getNonce(offerer, zone).call()

    def sign_order(
        self,
        order_parameters: OrderParameters,
        nonce: int,
        account_address: str,
    ):
        domain_data = {
            "name": CONSIDERATION_CONTRACT_NAME,
            "version": CONSIDERATION_CONTRACT_VERSION,
            "chainId": self.web3.eth.chain_id,
            "verifyingContract": self.contract.address,
        }

        # We need to convert ints to str when signing due to limitations of certain RPC providers
        order_components = {
            **dict_int_to_str(order_parameters.dict()),
            "nonce": nonce,
            "offer": list(
                map(lambda x: dict_int_to_str(x.dict()), order_parameters.offer)
            ),
            "consideration": list(
                map(lambda x: dict_int_to_str(x.dict()), order_parameters.consideration)
            ),
        }

        payload = {
            "domain": domain_data,
            "message": order_components,
            "types": EIP_712_ORDER_TYPE,
            "primaryType": "OrderComponents",
        }

        # Default to using signTypedData_v4. If that's not possible, fallback to signTypedData
        try:
            response = self.web3.provider.make_request(
                RPCEndpoint("eth_signTypedData_v4"),
                [
                    account_address or self.web3.eth.accounts[0],
                    payload,
                ],
            )
        except:
            response = self.web3.provider.make_request(
                RPCEndpoint("eth_signTypedData"),
                [
                    account_address or self.web3.eth.accounts[0],
                    payload,
                ],
            )

        if "result" not in response and "error" in response:
            raise ValueError(
                f"There was a problem generating the signature for the order: {response['error']}"
            )

        return response["result"]

    def approve_orders(self, orders: list[Order]):
        validate = self.contract.functions.validate(parse_model_list(orders))

        return TransactionRequest(
            transact=validate.transact,
            build_transaction=validate.buildTransaction,
        )
