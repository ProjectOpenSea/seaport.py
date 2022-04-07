from dataclasses import dataclass
from typing import Optional

from consideration.utils.proxy import ProxyStrategy


@dataclass
class ContractOverrides:
    contract_address: Optional[str]
    legacy_proxy_registry_address: Optional[str]


@dataclass
class ConsiderationConfig:
    # Used because fulfillments may be invalid if confirmations take too long. Default buffer is 30 minutes
    ascending_amount_fulfillment_buffer: int = 1800

    # Allow users to optionally skip balance and approval checks
    balance_and_approval_checks_on_order_creation: bool = True

    # Defaults to use proxy if it would result in zero approvals needed. Otherwise, users can specify the proxy strategy
    # they want to use, relevant for creating orders or fulfilling orders
    proxy_strategy: ProxyStrategy = ProxyStrategy.IF_ZERO_APPROVALS_NEEDED

    overrides: ContractOverrides = ContractOverrides(
        contract_address="", legacy_proxy_registry_address=""
    )
