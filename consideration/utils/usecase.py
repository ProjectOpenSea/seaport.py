from typing import Optional, Union

from web3.contract import ContractFunction
from web3.types import TxParams

from consideration.types import (
    ApprovalAction,
    CreateOrderAction,
    CreateOrderActions,
    OrderExchangeActions,
    TransactionMethods,
)


def execute_all_actions(
    actions: Union[CreateOrderActions, OrderExchangeActions],
    initial_tx_params: TxParams = {},
):
    for action in actions[:-1]:
        if isinstance(action, ApprovalAction):
            action.transaction_methods.transact(initial_tx_params)

    final_action = actions[-1]

    return (
        final_action.create_order()
        if isinstance(final_action, CreateOrderAction)
        else final_action.transaction_methods.transact(initial_tx_params)
    )


def get_transaction_methods(
    contract_fn: ContractFunction, initial_tx_params: TxParams = {}
) -> TransactionMethods:
    def estimate_gas(transaction: Optional[TxParams] = {}):
        transaction = transaction or {}
        return contract_fn.estimateGas(initial_tx_params | transaction)

    def call_static(transaction: Optional[TxParams] = {}):
        transaction = transaction or {}
        return contract_fn.call(initial_tx_params | transaction)

    def transact(transaction: Optional[TxParams] = {}):
        transaction = transaction or {}

        return contract_fn.transact(initial_tx_params | transaction)

    def build_transaction(transaction: Optional[TxParams] = {}):
        transaction = transaction or {}
        return contract_fn.buildTransaction(initial_tx_params | transaction)

    return TransactionMethods(
        estimate_gas=estimate_gas,
        call_static=call_static,
        transact=transact,
        build_transaction=build_transaction,
    )
