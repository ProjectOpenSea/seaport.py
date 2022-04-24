from web3 import Web3


class MerkleTree:
    elements: list[bytes]
    element_to_index: dict[bytes, int]

    def __init__(self, identifiers: list[int]):
        sorted_identifiers = sorted(
            map(
                lambda identifier: bytes.fromhex(hex(identifier)[2:].zfill(64)),
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

    def get_root(self):
        layers = self._get_layers(self.elements)
        layer = layers[-1]

        return layer[0] if layer else bytes()

    def get_proof(self, identifier: int):
        proof = []
        element = bytes.fromhex(hex(identifier)[2:].zfill(64))

        if element not in self.element_to_index:
            return proof

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
                proof.append(pair_element)

            index_of_element = index_of_element // 2

        return list(map(lambda x: "0x" + x.hex(), proof))

    def _get_next_layer(self, elements: list[bytes]):
        return [
            self._combined_hash(element, elements[index + 1])
            for index, element in enumerate(elements)
            if index % 2 == 0
        ]

    def _get_layers(self, elements: list[bytes]):
        layers = [elements[:]]
        while len(layers[-1]) > 1:
            layers.append(self._get_next_layer(layers[-1]))

        return layers

    def _combined_hash(self, first: bytes, second: bytes):
        if not first:
            return second
        if not second:
            return first

        return Web3.solidityKeccak(abi_types=["bytes"], values=[first + second])
