CONSIDERATION_ABI = [
    {
        "inputs": [],
        "name": "DOMAIN_SEPARATOR",
        "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {
                "components": [
                    {"internalType": "address", "name": "offerer", "type": "address"},
                    {"internalType": "address", "name": "zone", "type": "address"},
                    {
                        "components": [
                            {
                                "internalType": "enum ItemType",
                                "name": "itemType",
                                "type": "uint8",
                            },
                            {
                                "internalType": "address",
                                "name": "token",
                                "type": "address",
                            },
                            {
                                "internalType": "uint256",
                                "name": "identifierOrCriteria",
                                "type": "uint256",
                            },
                            {
                                "internalType": "uint256",
                                "name": "startAmount",
                                "type": "uint256",
                            },
                            {
                                "internalType": "uint256",
                                "name": "endAmount",
                                "type": "uint256",
                            },
                        ],
                        "internalType": "struct OfferItem[]",
                        "name": "offer",
                        "type": "tuple[]",
                    },
                    {
                        "components": [
                            {
                                "internalType": "enum ItemType",
                                "name": "itemType",
                                "type": "uint8",
                            },
                            {
                                "internalType": "address",
                                "name": "token",
                                "type": "address",
                            },
                            {
                                "internalType": "uint256",
                                "name": "identifierOrCriteria",
                                "type": "uint256",
                            },
                            {
                                "internalType": "uint256",
                                "name": "startAmount",
                                "type": "uint256",
                            },
                            {
                                "internalType": "uint256",
                                "name": "endAmount",
                                "type": "uint256",
                            },
                            {
                                "internalType": "address payable",
                                "name": "recipient",
                                "type": "address",
                            },
                        ],
                        "internalType": "struct ConsiderationItem[]",
                        "name": "consideration",
                        "type": "tuple[]",
                    },
                    {
                        "internalType": "enum OrderType",
                        "name": "orderType",
                        "type": "uint8",
                    },
                    {"internalType": "uint256", "name": "startTime", "type": "uint256"},
                    {"internalType": "uint256", "name": "endTime", "type": "uint256"},
                    {"internalType": "uint256", "name": "salt", "type": "uint256"},
                    {"internalType": "uint256", "name": "nonce", "type": "uint256"},
                ],
                "internalType": "struct OrderComponents[]",
                "name": "orders",
                "type": "tuple[]",
            }
        ],
        "name": "cancel",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {
                "components": [
                    {
                        "components": [
                            {
                                "internalType": "address",
                                "name": "offerer",
                                "type": "address",
                            },
                            {
                                "internalType": "address",
                                "name": "zone",
                                "type": "address",
                            },
                            {
                                "internalType": "enum OrderType",
                                "name": "orderType",
                                "type": "uint8",
                            },
                            {
                                "internalType": "uint256",
                                "name": "startTime",
                                "type": "uint256",
                            },
                            {
                                "internalType": "uint256",
                                "name": "endTime",
                                "type": "uint256",
                            },
                            {
                                "internalType": "uint256",
                                "name": "salt",
                                "type": "uint256",
                            },
                            {
                                "components": [
                                    {
                                        "internalType": "enum ItemType",
                                        "name": "itemType",
                                        "type": "uint8",
                                    },
                                    {
                                        "internalType": "address",
                                        "name": "token",
                                        "type": "address",
                                    },
                                    {
                                        "internalType": "uint256",
                                        "name": "identifierOrCriteria",
                                        "type": "uint256",
                                    },
                                    {
                                        "internalType": "uint256",
                                        "name": "startAmount",
                                        "type": "uint256",
                                    },
                                    {
                                        "internalType": "uint256",
                                        "name": "endAmount",
                                        "type": "uint256",
                                    },
                                ],
                                "internalType": "struct OfferItem[]",
                                "name": "offer",
                                "type": "tuple[]",
                            },
                            {
                                "components": [
                                    {
                                        "internalType": "enum ItemType",
                                        "name": "itemType",
                                        "type": "uint8",
                                    },
                                    {
                                        "internalType": "address",
                                        "name": "token",
                                        "type": "address",
                                    },
                                    {
                                        "internalType": "uint256",
                                        "name": "identifierOrCriteria",
                                        "type": "uint256",
                                    },
                                    {
                                        "internalType": "uint256",
                                        "name": "startAmount",
                                        "type": "uint256",
                                    },
                                    {
                                        "internalType": "uint256",
                                        "name": "endAmount",
                                        "type": "uint256",
                                    },
                                    {
                                        "internalType": "address payable",
                                        "name": "recipient",
                                        "type": "address",
                                    },
                                ],
                                "internalType": "struct ConsiderationItem[]",
                                "name": "consideration",
                                "type": "tuple[]",
                            },
                            {
                                "internalType": "uint256",
                                "name": "totalOriginalConsiderationItems",
                                "type": "uint256",
                            },
                        ],
                        "internalType": "struct OrderParameters",
                        "name": "parameters",
                        "type": "tuple",
                    },
                    {"internalType": "uint120", "name": "numerator", "type": "uint120"},
                    {
                        "internalType": "uint120",
                        "name": "denominator",
                        "type": "uint120",
                    },
                    {"internalType": "bytes", "name": "signature", "type": "bytes"},
                ],
                "internalType": "struct AdvancedOrder",
                "name": "advancedOrder",
                "type": "tuple",
            },
            {
                "components": [
                    {
                        "internalType": "uint256",
                        "name": "orderIndex",
                        "type": "uint256",
                    },
                    {"internalType": "enum Side", "name": "side", "type": "uint8"},
                    {"internalType": "uint256", "name": "index", "type": "uint256"},
                    {
                        "internalType": "uint256",
                        "name": "identifier",
                        "type": "uint256",
                    },
                    {
                        "internalType": "bytes32[]",
                        "name": "criteriaProof",
                        "type": "bytes32[]",
                    },
                ],
                "internalType": "struct CriteriaResolver[]",
                "name": "criteriaResolvers",
                "type": "tuple[]",
            },
            {"internalType": "bool", "name": "useFulfillerProxy", "type": "bool"},
        ],
        "name": "fulfillAdvancedOrder",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "payable",
        "type": "function",
    },
    {
        "inputs": [
            {
                "components": [
                    {
                        "internalType": "address",
                        "name": "considerationToken",
                        "type": "address",
                    },
                    {
                        "internalType": "uint256",
                        "name": "considerationIdentifier",
                        "type": "uint256",
                    },
                    {
                        "internalType": "uint256",
                        "name": "considerationAmount",
                        "type": "uint256",
                    },
                    {
                        "internalType": "address payable",
                        "name": "offerer",
                        "type": "address",
                    },
                    {"internalType": "address", "name": "zone", "type": "address"},
                    {
                        "internalType": "address",
                        "name": "offerToken",
                        "type": "address",
                    },
                    {
                        "internalType": "uint256",
                        "name": "offerIdentifier",
                        "type": "uint256",
                    },
                    {
                        "internalType": "uint256",
                        "name": "offerAmount",
                        "type": "uint256",
                    },
                    {
                        "internalType": "enum OrderType",
                        "name": "orderType",
                        "type": "uint8",
                    },
                    {"internalType": "uint256", "name": "startTime", "type": "uint256"},
                    {"internalType": "uint256", "name": "endTime", "type": "uint256"},
                    {"internalType": "uint256", "name": "salt", "type": "uint256"},
                    {
                        "internalType": "bool",
                        "name": "useFulfillerProxy",
                        "type": "bool",
                    },
                    {
                        "internalType": "uint256",
                        "name": "totalOriginalAdditionalRecipients",
                        "type": "uint256",
                    },
                    {
                        "components": [
                            {
                                "internalType": "uint256",
                                "name": "amount",
                                "type": "uint256",
                            },
                            {
                                "internalType": "address payable",
                                "name": "recipient",
                                "type": "address",
                            },
                        ],
                        "internalType": "struct AdditionalRecipient[]",
                        "name": "additionalRecipients",
                        "type": "tuple[]",
                    },
                    {"internalType": "bytes", "name": "signature", "type": "bytes"},
                ],
                "internalType": "struct BasicOrderParameters",
                "name": "parameters",
                "type": "tuple",
            }
        ],
        "name": "fulfillBasicERC1155ForERC20Order",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {
                "components": [
                    {
                        "internalType": "address",
                        "name": "considerationToken",
                        "type": "address",
                    },
                    {
                        "internalType": "uint256",
                        "name": "considerationIdentifier",
                        "type": "uint256",
                    },
                    {
                        "internalType": "uint256",
                        "name": "considerationAmount",
                        "type": "uint256",
                    },
                    {
                        "internalType": "address payable",
                        "name": "offerer",
                        "type": "address",
                    },
                    {"internalType": "address", "name": "zone", "type": "address"},
                    {
                        "internalType": "address",
                        "name": "offerToken",
                        "type": "address",
                    },
                    {
                        "internalType": "uint256",
                        "name": "offerIdentifier",
                        "type": "uint256",
                    },
                    {
                        "internalType": "uint256",
                        "name": "offerAmount",
                        "type": "uint256",
                    },
                    {
                        "internalType": "enum OrderType",
                        "name": "orderType",
                        "type": "uint8",
                    },
                    {"internalType": "uint256", "name": "startTime", "type": "uint256"},
                    {"internalType": "uint256", "name": "endTime", "type": "uint256"},
                    {"internalType": "uint256", "name": "salt", "type": "uint256"},
                    {
                        "internalType": "bool",
                        "name": "useFulfillerProxy",
                        "type": "bool",
                    },
                    {
                        "internalType": "uint256",
                        "name": "totalOriginalAdditionalRecipients",
                        "type": "uint256",
                    },
                    {
                        "components": [
                            {
                                "internalType": "uint256",
                                "name": "amount",
                                "type": "uint256",
                            },
                            {
                                "internalType": "address payable",
                                "name": "recipient",
                                "type": "address",
                            },
                        ],
                        "internalType": "struct AdditionalRecipient[]",
                        "name": "additionalRecipients",
                        "type": "tuple[]",
                    },
                    {"internalType": "bytes", "name": "signature", "type": "bytes"},
                ],
                "internalType": "struct BasicOrderParameters",
                "name": "parameters",
                "type": "tuple",
            }
        ],
        "name": "fulfillBasicERC20ForERC1155Order",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {
                "components": [
                    {
                        "internalType": "address",
                        "name": "considerationToken",
                        "type": "address",
                    },
                    {
                        "internalType": "uint256",
                        "name": "considerationIdentifier",
                        "type": "uint256",
                    },
                    {
                        "internalType": "uint256",
                        "name": "considerationAmount",
                        "type": "uint256",
                    },
                    {
                        "internalType": "address payable",
                        "name": "offerer",
                        "type": "address",
                    },
                    {"internalType": "address", "name": "zone", "type": "address"},
                    {
                        "internalType": "address",
                        "name": "offerToken",
                        "type": "address",
                    },
                    {
                        "internalType": "uint256",
                        "name": "offerIdentifier",
                        "type": "uint256",
                    },
                    {
                        "internalType": "uint256",
                        "name": "offerAmount",
                        "type": "uint256",
                    },
                    {
                        "internalType": "enum OrderType",
                        "name": "orderType",
                        "type": "uint8",
                    },
                    {"internalType": "uint256", "name": "startTime", "type": "uint256"},
                    {"internalType": "uint256", "name": "endTime", "type": "uint256"},
                    {"internalType": "uint256", "name": "salt", "type": "uint256"},
                    {
                        "internalType": "bool",
                        "name": "useFulfillerProxy",
                        "type": "bool",
                    },
                    {
                        "internalType": "uint256",
                        "name": "totalOriginalAdditionalRecipients",
                        "type": "uint256",
                    },
                    {
                        "components": [
                            {
                                "internalType": "uint256",
                                "name": "amount",
                                "type": "uint256",
                            },
                            {
                                "internalType": "address payable",
                                "name": "recipient",
                                "type": "address",
                            },
                        ],
                        "internalType": "struct AdditionalRecipient[]",
                        "name": "additionalRecipients",
                        "type": "tuple[]",
                    },
                    {"internalType": "bytes", "name": "signature", "type": "bytes"},
                ],
                "internalType": "struct BasicOrderParameters",
                "name": "parameters",
                "type": "tuple",
            }
        ],
        "name": "fulfillBasicERC20ForERC721Order",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {
                "components": [
                    {
                        "internalType": "address",
                        "name": "considerationToken",
                        "type": "address",
                    },
                    {
                        "internalType": "uint256",
                        "name": "considerationIdentifier",
                        "type": "uint256",
                    },
                    {
                        "internalType": "uint256",
                        "name": "considerationAmount",
                        "type": "uint256",
                    },
                    {
                        "internalType": "address payable",
                        "name": "offerer",
                        "type": "address",
                    },
                    {"internalType": "address", "name": "zone", "type": "address"},
                    {
                        "internalType": "address",
                        "name": "offerToken",
                        "type": "address",
                    },
                    {
                        "internalType": "uint256",
                        "name": "offerIdentifier",
                        "type": "uint256",
                    },
                    {
                        "internalType": "uint256",
                        "name": "offerAmount",
                        "type": "uint256",
                    },
                    {
                        "internalType": "enum OrderType",
                        "name": "orderType",
                        "type": "uint8",
                    },
                    {"internalType": "uint256", "name": "startTime", "type": "uint256"},
                    {"internalType": "uint256", "name": "endTime", "type": "uint256"},
                    {"internalType": "uint256", "name": "salt", "type": "uint256"},
                    {
                        "internalType": "bool",
                        "name": "useFulfillerProxy",
                        "type": "bool",
                    },
                    {
                        "internalType": "uint256",
                        "name": "totalOriginalAdditionalRecipients",
                        "type": "uint256",
                    },
                    {
                        "components": [
                            {
                                "internalType": "uint256",
                                "name": "amount",
                                "type": "uint256",
                            },
                            {
                                "internalType": "address payable",
                                "name": "recipient",
                                "type": "address",
                            },
                        ],
                        "internalType": "struct AdditionalRecipient[]",
                        "name": "additionalRecipients",
                        "type": "tuple[]",
                    },
                    {"internalType": "bytes", "name": "signature", "type": "bytes"},
                ],
                "internalType": "struct BasicOrderParameters",
                "name": "parameters",
                "type": "tuple",
            }
        ],
        "name": "fulfillBasicERC721ForERC20Order",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {
                "components": [
                    {
                        "internalType": "address",
                        "name": "considerationToken",
                        "type": "address",
                    },
                    {
                        "internalType": "uint256",
                        "name": "considerationIdentifier",
                        "type": "uint256",
                    },
                    {
                        "internalType": "uint256",
                        "name": "considerationAmount",
                        "type": "uint256",
                    },
                    {
                        "internalType": "address payable",
                        "name": "offerer",
                        "type": "address",
                    },
                    {"internalType": "address", "name": "zone", "type": "address"},
                    {
                        "internalType": "address",
                        "name": "offerToken",
                        "type": "address",
                    },
                    {
                        "internalType": "uint256",
                        "name": "offerIdentifier",
                        "type": "uint256",
                    },
                    {
                        "internalType": "uint256",
                        "name": "offerAmount",
                        "type": "uint256",
                    },
                    {
                        "internalType": "enum OrderType",
                        "name": "orderType",
                        "type": "uint8",
                    },
                    {"internalType": "uint256", "name": "startTime", "type": "uint256"},
                    {"internalType": "uint256", "name": "endTime", "type": "uint256"},
                    {"internalType": "uint256", "name": "salt", "type": "uint256"},
                    {
                        "internalType": "bool",
                        "name": "useFulfillerProxy",
                        "type": "bool",
                    },
                    {
                        "internalType": "uint256",
                        "name": "totalOriginalAdditionalRecipients",
                        "type": "uint256",
                    },
                    {
                        "components": [
                            {
                                "internalType": "uint256",
                                "name": "amount",
                                "type": "uint256",
                            },
                            {
                                "internalType": "address payable",
                                "name": "recipient",
                                "type": "address",
                            },
                        ],
                        "internalType": "struct AdditionalRecipient[]",
                        "name": "additionalRecipients",
                        "type": "tuple[]",
                    },
                    {"internalType": "bytes", "name": "signature", "type": "bytes"},
                ],
                "internalType": "struct BasicOrderParameters",
                "name": "parameters",
                "type": "tuple",
            }
        ],
        "name": "fulfillBasicEthForERC1155Order",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "payable",
        "type": "function",
    },
    {
        "inputs": [
            {
                "components": [
                    {
                        "internalType": "address",
                        "name": "considerationToken",
                        "type": "address",
                    },
                    {
                        "internalType": "uint256",
                        "name": "considerationIdentifier",
                        "type": "uint256",
                    },
                    {
                        "internalType": "uint256",
                        "name": "considerationAmount",
                        "type": "uint256",
                    },
                    {
                        "internalType": "address payable",
                        "name": "offerer",
                        "type": "address",
                    },
                    {"internalType": "address", "name": "zone", "type": "address"},
                    {
                        "internalType": "address",
                        "name": "offerToken",
                        "type": "address",
                    },
                    {
                        "internalType": "uint256",
                        "name": "offerIdentifier",
                        "type": "uint256",
                    },
                    {
                        "internalType": "uint256",
                        "name": "offerAmount",
                        "type": "uint256",
                    },
                    {
                        "internalType": "enum OrderType",
                        "name": "orderType",
                        "type": "uint8",
                    },
                    {"internalType": "uint256", "name": "startTime", "type": "uint256"},
                    {"internalType": "uint256", "name": "endTime", "type": "uint256"},
                    {"internalType": "uint256", "name": "salt", "type": "uint256"},
                    {
                        "internalType": "bool",
                        "name": "useFulfillerProxy",
                        "type": "bool",
                    },
                    {
                        "internalType": "uint256",
                        "name": "totalOriginalAdditionalRecipients",
                        "type": "uint256",
                    },
                    {
                        "components": [
                            {
                                "internalType": "uint256",
                                "name": "amount",
                                "type": "uint256",
                            },
                            {
                                "internalType": "address payable",
                                "name": "recipient",
                                "type": "address",
                            },
                        ],
                        "internalType": "struct AdditionalRecipient[]",
                        "name": "additionalRecipients",
                        "type": "tuple[]",
                    },
                    {"internalType": "bytes", "name": "signature", "type": "bytes"},
                ],
                "internalType": "struct BasicOrderParameters",
                "name": "parameters",
                "type": "tuple",
            }
        ],
        "name": "fulfillBasicEthForERC721Order",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "payable",
        "type": "function",
    },
    {
        "inputs": [
            {
                "components": [
                    {
                        "components": [
                            {
                                "internalType": "address",
                                "name": "offerer",
                                "type": "address",
                            },
                            {
                                "internalType": "address",
                                "name": "zone",
                                "type": "address",
                            },
                            {
                                "internalType": "enum OrderType",
                                "name": "orderType",
                                "type": "uint8",
                            },
                            {
                                "internalType": "uint256",
                                "name": "startTime",
                                "type": "uint256",
                            },
                            {
                                "internalType": "uint256",
                                "name": "endTime",
                                "type": "uint256",
                            },
                            {
                                "internalType": "uint256",
                                "name": "salt",
                                "type": "uint256",
                            },
                            {
                                "components": [
                                    {
                                        "internalType": "enum ItemType",
                                        "name": "itemType",
                                        "type": "uint8",
                                    },
                                    {
                                        "internalType": "address",
                                        "name": "token",
                                        "type": "address",
                                    },
                                    {
                                        "internalType": "uint256",
                                        "name": "identifierOrCriteria",
                                        "type": "uint256",
                                    },
                                    {
                                        "internalType": "uint256",
                                        "name": "startAmount",
                                        "type": "uint256",
                                    },
                                    {
                                        "internalType": "uint256",
                                        "name": "endAmount",
                                        "type": "uint256",
                                    },
                                ],
                                "internalType": "struct OfferItem[]",
                                "name": "offer",
                                "type": "tuple[]",
                            },
                            {
                                "components": [
                                    {
                                        "internalType": "enum ItemType",
                                        "name": "itemType",
                                        "type": "uint8",
                                    },
                                    {
                                        "internalType": "address",
                                        "name": "token",
                                        "type": "address",
                                    },
                                    {
                                        "internalType": "uint256",
                                        "name": "identifierOrCriteria",
                                        "type": "uint256",
                                    },
                                    {
                                        "internalType": "uint256",
                                        "name": "startAmount",
                                        "type": "uint256",
                                    },
                                    {
                                        "internalType": "uint256",
                                        "name": "endAmount",
                                        "type": "uint256",
                                    },
                                    {
                                        "internalType": "address payable",
                                        "name": "recipient",
                                        "type": "address",
                                    },
                                ],
                                "internalType": "struct ConsiderationItem[]",
                                "name": "consideration",
                                "type": "tuple[]",
                            },
                            {
                                "internalType": "uint256",
                                "name": "totalOriginalConsiderationItems",
                                "type": "uint256",
                            },
                        ],
                        "internalType": "struct OrderParameters",
                        "name": "parameters",
                        "type": "tuple",
                    },
                    {"internalType": "bytes", "name": "signature", "type": "bytes"},
                ],
                "internalType": "struct Order",
                "name": "order",
                "type": "tuple",
            },
            {"internalType": "bool", "name": "useFulfillerProxy", "type": "bool"},
        ],
        "name": "fulfillOrder",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "payable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "offerer", "type": "address"},
            {"internalType": "address", "name": "zone", "type": "address"},
        ],
        "name": "getNonce",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {
                "components": [
                    {"internalType": "address", "name": "offerer", "type": "address"},
                    {"internalType": "address", "name": "zone", "type": "address"},
                    {
                        "components": [
                            {
                                "internalType": "enum ItemType",
                                "name": "itemType",
                                "type": "uint8",
                            },
                            {
                                "internalType": "address",
                                "name": "token",
                                "type": "address",
                            },
                            {
                                "internalType": "uint256",
                                "name": "identifierOrCriteria",
                                "type": "uint256",
                            },
                            {
                                "internalType": "uint256",
                                "name": "startAmount",
                                "type": "uint256",
                            },
                            {
                                "internalType": "uint256",
                                "name": "endAmount",
                                "type": "uint256",
                            },
                        ],
                        "internalType": "struct OfferItem[]",
                        "name": "offer",
                        "type": "tuple[]",
                    },
                    {
                        "components": [
                            {
                                "internalType": "enum ItemType",
                                "name": "itemType",
                                "type": "uint8",
                            },
                            {
                                "internalType": "address",
                                "name": "token",
                                "type": "address",
                            },
                            {
                                "internalType": "uint256",
                                "name": "identifierOrCriteria",
                                "type": "uint256",
                            },
                            {
                                "internalType": "uint256",
                                "name": "startAmount",
                                "type": "uint256",
                            },
                            {
                                "internalType": "uint256",
                                "name": "endAmount",
                                "type": "uint256",
                            },
                            {
                                "internalType": "address payable",
                                "name": "recipient",
                                "type": "address",
                            },
                        ],
                        "internalType": "struct ConsiderationItem[]",
                        "name": "consideration",
                        "type": "tuple[]",
                    },
                    {
                        "internalType": "enum OrderType",
                        "name": "orderType",
                        "type": "uint8",
                    },
                    {"internalType": "uint256", "name": "startTime", "type": "uint256"},
                    {"internalType": "uint256", "name": "endTime", "type": "uint256"},
                    {"internalType": "uint256", "name": "salt", "type": "uint256"},
                    {"internalType": "uint256", "name": "nonce", "type": "uint256"},
                ],
                "internalType": "struct OrderComponents",
                "name": "order",
                "type": "tuple",
            }
        ],
        "name": "getOrderHash",
        "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "bytes32", "name": "orderHash", "type": "bytes32"}],
        "name": "getOrderStatus",
        "outputs": [
            {"internalType": "bool", "name": "isValidated", "type": "bool"},
            {"internalType": "bool", "name": "isCancelled", "type": "bool"},
            {"internalType": "uint256", "name": "totalFilled", "type": "uint256"},
            {"internalType": "uint256", "name": "totalSize", "type": "uint256"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "offerer", "type": "address"},
            {"internalType": "address", "name": "zone", "type": "address"},
        ],
        "name": "incrementNonce",
        "outputs": [{"internalType": "uint256", "name": "newNonce", "type": "uint256"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {
                "components": [
                    {
                        "components": [
                            {
                                "internalType": "address",
                                "name": "offerer",
                                "type": "address",
                            },
                            {
                                "internalType": "address",
                                "name": "zone",
                                "type": "address",
                            },
                            {
                                "internalType": "enum OrderType",
                                "name": "orderType",
                                "type": "uint8",
                            },
                            {
                                "internalType": "uint256",
                                "name": "startTime",
                                "type": "uint256",
                            },
                            {
                                "internalType": "uint256",
                                "name": "endTime",
                                "type": "uint256",
                            },
                            {
                                "internalType": "uint256",
                                "name": "salt",
                                "type": "uint256",
                            },
                            {
                                "components": [
                                    {
                                        "internalType": "enum ItemType",
                                        "name": "itemType",
                                        "type": "uint8",
                                    },
                                    {
                                        "internalType": "address",
                                        "name": "token",
                                        "type": "address",
                                    },
                                    {
                                        "internalType": "uint256",
                                        "name": "identifierOrCriteria",
                                        "type": "uint256",
                                    },
                                    {
                                        "internalType": "uint256",
                                        "name": "startAmount",
                                        "type": "uint256",
                                    },
                                    {
                                        "internalType": "uint256",
                                        "name": "endAmount",
                                        "type": "uint256",
                                    },
                                ],
                                "internalType": "struct OfferItem[]",
                                "name": "offer",
                                "type": "tuple[]",
                            },
                            {
                                "components": [
                                    {
                                        "internalType": "enum ItemType",
                                        "name": "itemType",
                                        "type": "uint8",
                                    },
                                    {
                                        "internalType": "address",
                                        "name": "token",
                                        "type": "address",
                                    },
                                    {
                                        "internalType": "uint256",
                                        "name": "identifierOrCriteria",
                                        "type": "uint256",
                                    },
                                    {
                                        "internalType": "uint256",
                                        "name": "startAmount",
                                        "type": "uint256",
                                    },
                                    {
                                        "internalType": "uint256",
                                        "name": "endAmount",
                                        "type": "uint256",
                                    },
                                    {
                                        "internalType": "address payable",
                                        "name": "recipient",
                                        "type": "address",
                                    },
                                ],
                                "internalType": "struct ConsiderationItem[]",
                                "name": "consideration",
                                "type": "tuple[]",
                            },
                            {
                                "internalType": "uint256",
                                "name": "totalOriginalConsiderationItems",
                                "type": "uint256",
                            },
                        ],
                        "internalType": "struct OrderParameters",
                        "name": "parameters",
                        "type": "tuple",
                    },
                    {"internalType": "uint120", "name": "numerator", "type": "uint120"},
                    {
                        "internalType": "uint120",
                        "name": "denominator",
                        "type": "uint120",
                    },
                    {"internalType": "bytes", "name": "signature", "type": "bytes"},
                ],
                "internalType": "struct AdvancedOrder[]",
                "name": "orders",
                "type": "tuple[]",
            },
            {
                "components": [
                    {
                        "internalType": "uint256",
                        "name": "orderIndex",
                        "type": "uint256",
                    },
                    {"internalType": "enum Side", "name": "side", "type": "uint8"},
                    {"internalType": "uint256", "name": "index", "type": "uint256"},
                    {
                        "internalType": "uint256",
                        "name": "identifier",
                        "type": "uint256",
                    },
                    {
                        "internalType": "bytes32[]",
                        "name": "criteriaProof",
                        "type": "bytes32[]",
                    },
                ],
                "internalType": "struct CriteriaResolver[]",
                "name": "criteriaResolvers",
                "type": "tuple[]",
            },
            {
                "components": [
                    {
                        "components": [
                            {
                                "internalType": "uint256",
                                "name": "orderIndex",
                                "type": "uint256",
                            },
                            {
                                "internalType": "uint256",
                                "name": "itemIndex",
                                "type": "uint256",
                            },
                        ],
                        "internalType": "struct FulfillmentComponent[]",
                        "name": "offerComponents",
                        "type": "tuple[]",
                    },
                    {
                        "components": [
                            {
                                "internalType": "uint256",
                                "name": "orderIndex",
                                "type": "uint256",
                            },
                            {
                                "internalType": "uint256",
                                "name": "itemIndex",
                                "type": "uint256",
                            },
                        ],
                        "internalType": "struct FulfillmentComponent[]",
                        "name": "considerationComponents",
                        "type": "tuple[]",
                    },
                ],
                "internalType": "struct Fulfillment[]",
                "name": "fulfillments",
                "type": "tuple[]",
            },
        ],
        "name": "matchAdvancedOrders",
        "outputs": [
            {
                "components": [
                    {
                        "components": [
                            {
                                "internalType": "enum ItemType",
                                "name": "itemType",
                                "type": "uint8",
                            },
                            {
                                "internalType": "address",
                                "name": "token",
                                "type": "address",
                            },
                            {
                                "internalType": "uint256",
                                "name": "identifier",
                                "type": "uint256",
                            },
                            {
                                "internalType": "uint256",
                                "name": "amount",
                                "type": "uint256",
                            },
                            {
                                "internalType": "address payable",
                                "name": "recipient",
                                "type": "address",
                            },
                        ],
                        "internalType": "struct ReceivedItem",
                        "name": "item",
                        "type": "tuple",
                    },
                    {"internalType": "address", "name": "offerer", "type": "address"},
                    {"internalType": "bool", "name": "useProxy", "type": "bool"},
                ],
                "internalType": "struct Execution[]",
                "name": "standardExecutions",
                "type": "tuple[]",
            },
            {
                "components": [
                    {"internalType": "address", "name": "token", "type": "address"},
                    {"internalType": "address", "name": "from", "type": "address"},
                    {"internalType": "address", "name": "to", "type": "address"},
                    {
                        "internalType": "uint256[]",
                        "name": "tokenIds",
                        "type": "uint256[]",
                    },
                    {
                        "internalType": "uint256[]",
                        "name": "amounts",
                        "type": "uint256[]",
                    },
                    {"internalType": "bool", "name": "useProxy", "type": "bool"},
                ],
                "internalType": "struct BatchExecution[]",
                "name": "batchExecutions",
                "type": "tuple[]",
            },
        ],
        "stateMutability": "payable",
        "type": "function",
    },
    {
        "inputs": [
            {
                "components": [
                    {
                        "components": [
                            {
                                "internalType": "address",
                                "name": "offerer",
                                "type": "address",
                            },
                            {
                                "internalType": "address",
                                "name": "zone",
                                "type": "address",
                            },
                            {
                                "internalType": "enum OrderType",
                                "name": "orderType",
                                "type": "uint8",
                            },
                            {
                                "internalType": "uint256",
                                "name": "startTime",
                                "type": "uint256",
                            },
                            {
                                "internalType": "uint256",
                                "name": "endTime",
                                "type": "uint256",
                            },
                            {
                                "internalType": "uint256",
                                "name": "salt",
                                "type": "uint256",
                            },
                            {
                                "components": [
                                    {
                                        "internalType": "enum ItemType",
                                        "name": "itemType",
                                        "type": "uint8",
                                    },
                                    {
                                        "internalType": "address",
                                        "name": "token",
                                        "type": "address",
                                    },
                                    {
                                        "internalType": "uint256",
                                        "name": "identifierOrCriteria",
                                        "type": "uint256",
                                    },
                                    {
                                        "internalType": "uint256",
                                        "name": "startAmount",
                                        "type": "uint256",
                                    },
                                    {
                                        "internalType": "uint256",
                                        "name": "endAmount",
                                        "type": "uint256",
                                    },
                                ],
                                "internalType": "struct OfferItem[]",
                                "name": "offer",
                                "type": "tuple[]",
                            },
                            {
                                "components": [
                                    {
                                        "internalType": "enum ItemType",
                                        "name": "itemType",
                                        "type": "uint8",
                                    },
                                    {
                                        "internalType": "address",
                                        "name": "token",
                                        "type": "address",
                                    },
                                    {
                                        "internalType": "uint256",
                                        "name": "identifierOrCriteria",
                                        "type": "uint256",
                                    },
                                    {
                                        "internalType": "uint256",
                                        "name": "startAmount",
                                        "type": "uint256",
                                    },
                                    {
                                        "internalType": "uint256",
                                        "name": "endAmount",
                                        "type": "uint256",
                                    },
                                    {
                                        "internalType": "address payable",
                                        "name": "recipient",
                                        "type": "address",
                                    },
                                ],
                                "internalType": "struct ConsiderationItem[]",
                                "name": "consideration",
                                "type": "tuple[]",
                            },
                            {
                                "internalType": "uint256",
                                "name": "totalOriginalConsiderationItems",
                                "type": "uint256",
                            },
                        ],
                        "internalType": "struct OrderParameters",
                        "name": "parameters",
                        "type": "tuple",
                    },
                    {"internalType": "bytes", "name": "signature", "type": "bytes"},
                ],
                "internalType": "struct Order[]",
                "name": "orders",
                "type": "tuple[]",
            },
            {
                "components": [
                    {
                        "components": [
                            {
                                "internalType": "uint256",
                                "name": "orderIndex",
                                "type": "uint256",
                            },
                            {
                                "internalType": "uint256",
                                "name": "itemIndex",
                                "type": "uint256",
                            },
                        ],
                        "internalType": "struct FulfillmentComponent[]",
                        "name": "offerComponents",
                        "type": "tuple[]",
                    },
                    {
                        "components": [
                            {
                                "internalType": "uint256",
                                "name": "orderIndex",
                                "type": "uint256",
                            },
                            {
                                "internalType": "uint256",
                                "name": "itemIndex",
                                "type": "uint256",
                            },
                        ],
                        "internalType": "struct FulfillmentComponent[]",
                        "name": "considerationComponents",
                        "type": "tuple[]",
                    },
                ],
                "internalType": "struct Fulfillment[]",
                "name": "fulfillments",
                "type": "tuple[]",
            },
        ],
        "name": "matchOrders",
        "outputs": [
            {
                "components": [
                    {
                        "components": [
                            {
                                "internalType": "enum ItemType",
                                "name": "itemType",
                                "type": "uint8",
                            },
                            {
                                "internalType": "address",
                                "name": "token",
                                "type": "address",
                            },
                            {
                                "internalType": "uint256",
                                "name": "identifier",
                                "type": "uint256",
                            },
                            {
                                "internalType": "uint256",
                                "name": "amount",
                                "type": "uint256",
                            },
                            {
                                "internalType": "address payable",
                                "name": "recipient",
                                "type": "address",
                            },
                        ],
                        "internalType": "struct ReceivedItem",
                        "name": "item",
                        "type": "tuple",
                    },
                    {"internalType": "address", "name": "offerer", "type": "address"},
                    {"internalType": "bool", "name": "useProxy", "type": "bool"},
                ],
                "internalType": "struct Execution[]",
                "name": "standardExecutions",
                "type": "tuple[]",
            },
            {
                "components": [
                    {"internalType": "address", "name": "token", "type": "address"},
                    {"internalType": "address", "name": "from", "type": "address"},
                    {"internalType": "address", "name": "to", "type": "address"},
                    {
                        "internalType": "uint256[]",
                        "name": "tokenIds",
                        "type": "uint256[]",
                    },
                    {
                        "internalType": "uint256[]",
                        "name": "amounts",
                        "type": "uint256[]",
                    },
                    {"internalType": "bool", "name": "useProxy", "type": "bool"},
                ],
                "internalType": "struct BatchExecution[]",
                "name": "batchExecutions",
                "type": "tuple[]",
            },
        ],
        "stateMutability": "payable",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "name",
        "outputs": [{"internalType": "string", "name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {
                "components": [
                    {
                        "components": [
                            {
                                "internalType": "address",
                                "name": "offerer",
                                "type": "address",
                            },
                            {
                                "internalType": "address",
                                "name": "zone",
                                "type": "address",
                            },
                            {
                                "internalType": "enum OrderType",
                                "name": "orderType",
                                "type": "uint8",
                            },
                            {
                                "internalType": "uint256",
                                "name": "startTime",
                                "type": "uint256",
                            },
                            {
                                "internalType": "uint256",
                                "name": "endTime",
                                "type": "uint256",
                            },
                            {
                                "internalType": "uint256",
                                "name": "salt",
                                "type": "uint256",
                            },
                            {
                                "components": [
                                    {
                                        "internalType": "enum ItemType",
                                        "name": "itemType",
                                        "type": "uint8",
                                    },
                                    {
                                        "internalType": "address",
                                        "name": "token",
                                        "type": "address",
                                    },
                                    {
                                        "internalType": "uint256",
                                        "name": "identifierOrCriteria",
                                        "type": "uint256",
                                    },
                                    {
                                        "internalType": "uint256",
                                        "name": "startAmount",
                                        "type": "uint256",
                                    },
                                    {
                                        "internalType": "uint256",
                                        "name": "endAmount",
                                        "type": "uint256",
                                    },
                                ],
                                "internalType": "struct OfferItem[]",
                                "name": "offer",
                                "type": "tuple[]",
                            },
                            {
                                "components": [
                                    {
                                        "internalType": "enum ItemType",
                                        "name": "itemType",
                                        "type": "uint8",
                                    },
                                    {
                                        "internalType": "address",
                                        "name": "token",
                                        "type": "address",
                                    },
                                    {
                                        "internalType": "uint256",
                                        "name": "identifierOrCriteria",
                                        "type": "uint256",
                                    },
                                    {
                                        "internalType": "uint256",
                                        "name": "startAmount",
                                        "type": "uint256",
                                    },
                                    {
                                        "internalType": "uint256",
                                        "name": "endAmount",
                                        "type": "uint256",
                                    },
                                    {
                                        "internalType": "address payable",
                                        "name": "recipient",
                                        "type": "address",
                                    },
                                ],
                                "internalType": "struct ConsiderationItem[]",
                                "name": "consideration",
                                "type": "tuple[]",
                            },
                            {
                                "internalType": "uint256",
                                "name": "totalOriginalConsiderationItems",
                                "type": "uint256",
                            },
                        ],
                        "internalType": "struct OrderParameters",
                        "name": "parameters",
                        "type": "tuple",
                    },
                    {"internalType": "bytes", "name": "signature", "type": "bytes"},
                ],
                "internalType": "struct Order[]",
                "name": "orders",
                "type": "tuple[]",
            }
        ],
        "name": "validate",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "version",
        "outputs": [{"internalType": "string", "name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function",
    },
]
