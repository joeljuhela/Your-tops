def recaman(length):
    """
    Creates a Recamán's sequence
    :param length: The length of the wanted sequence
    :return: array containing the sequence

    For more information about this sequence: https://en.wikipedia.org/wiki/Recam%C3%A1n%27s_sequence
    """
    a = [0]
    for n in range(1, length):
        candidate = a[-1] - n
        if candidate > 0 and candidate not in a:
            a.append(candidate)
        else:
            a.append(a[-1] + n)

    return a
