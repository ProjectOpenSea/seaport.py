from typing import Union
from consideration.types import (
    ApprovalAction,
    CreateOrderAction,
    CreateOrderActions,
    OrderExchangeActions,
    TransactionMethods,
)
from web3.contract import ContractFunction


def execute_all_actions(actions: Union[CreateOrderActions, OrderExchangeActions]):
    for action in range(len(actions) - 1):
        if isinstance(action, ApprovalAction):
            action.transaction.transact()

    final_action = actions[-1]

    return (
        final_action.create_order()
        if isinstance(final_action, CreateOrderAction)
        else final_action.transaction.transact()
    )


def get_transaction_methods(contract_fn: ContractFunction) -> TransactionMethods:
    return TransactionMethods(
        estimate_gas=contract_fn.estimateGas,
        call_static=contract_fn.call,
        transact=contract_fn.transact,
        build_transaction=contract_fn.buildTransaction,
    )
