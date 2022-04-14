def gcd(a: int, b: int) -> int:
    if a == 0:
        return b

    return gcd(b % a, a)


def find_gcd(elements: list[int]):
    result = elements[0]
    for i in range(1, len(elements)):
        result = gcd(elements[i], result)

        if result == 1:
            return result

    return result
