from web3 import Web3


class MerkleTree:
    elements: list[bytes]
    element_to_index: dict[bytes, int]

    def __init__(self, identifiers: list[int]):
        self.identifiers = identifiers
        sorted_identifiers = sorted(
            map(
                lambda identifier: self._hash_identifier(identifier),
                identifiers,
            )
        )

        elements = [
            identifier
            for index, identifier in enumerate(sorted_identifiers)
            if index == 0 or sorted_identifiers[index - 1] != identifier
        ]

        self.element_to_index = {
            element: index for index, element in enumerate(elements)
        }

        self.elements = elements

    def _hash_identifier(self, identifier: int) -> bytes:
        return Web3.solidityKeccak(
            abi_types=["bytes"], values=[bytes.fromhex(hex(identifier)[2:].zfill(64))]
        )

    def get_identifiers(self) -> list[int]:
        return self.identifiers

    def get_root(self) -> bytes:
        layers = self._get_layers(self.elements)
        layer = layers[-1]

        return layer[0] if layer else bytes()

    def get_root_as_int(self) -> int:
        return int.from_bytes(self.get_root(), "big")

    def get_proof(self, identifier: int) -> list[str]:
        proofs = []
        element = self._hash_identifier(identifier)

        if element not in self.element_to_index:
            return proofs

        layers = self._get_layers(self.elements)

        index_of_element = self.element_to_index[element]

        for layer in layers:
            pair_index = (
                index_of_element + 1
                if index_of_element % 2 == 0
                else index_of_element - 1
            )
            pair_element = layer[pair_index] if pair_index < len(layer) else None

            if pair_element:
                proofs.append(pair_element)

            index_of_element = index_of_element // 2

        str_proofs = []
        for proof in proofs:
            proof = proof.hex()
            if not str(proof).startswith("0x"):
                proof = "0x" + str(proof)
            str_proofs.append(proof)
        return str_proofs

    def _get_next_layer(self, elements: list[bytes]) -> list[bytes]:
        layer = []
        for index, element in enumerate(elements):
            if index % 2 == 0:
                if index + 1 < len(elements):
                    layer.append(self._combined_hash(element, elements[index + 1]))
                else:
                    layer.append(element)
        return layer

    def _get_layers(self, elements: list[bytes]) -> list[list[bytes]]:
        layers = [elements[:]]
        while len(layers[-1]) > 1:
            layers.append(self._get_next_layer(layers[-1]))

        return layers

    def _combined_hash(self, first: bytes, second: bytes) -> bytes:
        if not first:
            return second
        if not second:
            return first

        sorted_values = sorted([first, second])

        return Web3.solidityKeccak(
            abi_types=["bytes"], values=[sorted_values[0] + sorted_values[1]]
        )
