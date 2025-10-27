def extract_bits(n: int, a: int | list, b: int | list) -> int:
    """
    Extract bits from the ath bit to the bth bit (inclusive),
    counting from the right, 0-indexed.
    
    Args:
        n : integer to extract from
        a : starting bit (0 = least significant) or multiple starting bits ordered from
            LSB [Q1|Q0]
        b : ending bit (inclusive)

    
    Returns:
        integer containing the extracted bits (shifted to start at 0)
    """
    if isinstance(a, int) and isinstance(b, int):
        if b < a:
            raise ValueError("b must be >= a")
        num_bits = b - a + 1
        mask = (1 << num_bits) - 1
        return (n >> a) & mask
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            raise ValueError("number of start bits is not equal to number of end bits")
        offset = 0
        result_bit = 0
        for i in range(len(a)):
            cur_a = a[i]
            cur_b = b[i]
            cur_value = extract_bits(n, cur_a, cur_b)
            result_bit += (cur_value << offset)
            offset += cur_b - cur_a + 1
        return result_bit
    else:
        raise ValueError("Unrecognized inputs")


def modify_bits(x, start, length, new_value):
    mask = ((1 << length) - 1) << start      # 1. mask covering those bits
    x &= ~mask                               # 2. clear that region
    x |= (new_value << start) & mask         # 3. insert new bits
    return x

def remove_bits_from_int(n: int, remove_indices) -> int:
    """Return integer with bits at given LSB indices removed."""
    remove_indices = set(remove_indices)
    result = 0
    pos = 0  # position in the new number

    for i in range(n.bit_length()):
        if i not in remove_indices:
            bit = (n >> i) & 1
            result |= bit << pos
            pos += 1
    return result

def update_value(value, offset, Q_add:"Qint"):
    cur_value = extract_bits(value, Q_add.start, Q_add.start + len(Q_add) - 1)
    cur_value = (cur_value + offset) % (2**(len(Q_add)))
    cur_value = modify_bits(value, offset, len(Q_add), cur_value)