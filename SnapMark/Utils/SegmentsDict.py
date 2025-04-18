# Dizionario dei segmenti per ciascun numero (il punto minore in 'X' deve corrispondere a '0')
number_segments_dict = {
    '0': [(0, 0.3), (0, 3.7), (0.3, 4), (1.4, 4), (1.7, 3.7), (1.7, 0.3), (1.4, 0), (0.3, 0), (0, 0.3), (1.7, 3.7)],
    # '0': [(2, 4), (0, 0), (2, 0), (2, 4), (0, 4), (0, 0)],
    '1': [(1, 0), (1, 4)],
    '2': [(2, 0), (0.3, 0), (0, 0.3), (0, 1.7), (0.3, 2), (1.7, 2), (2, 2.3), (2, 3.7), (1.7, 4), (0, 4)],
    '3': [(0, 0), (1.7, 0), (2, 0.3), (2, 1.7), (1.7, 2), (0, 2), (1.7, 2), (2, 2.3), (2, 3.7), (1.7, 4), (0, 4)],
    '4': [(0, 4), (0, 2.3), (0.3, 2), (2, 2), (2, 4), (2, 0)],
    '5': [(0, 0), (1.7, 0), (2, 0.3), (2, 1.7), (1.7, 2), (0.3, 2), (0, 2.3), (0, 3.7), (0.3, 4), (2, 4)],
    '6': [(0, 1.7), (0.3, 2), (1.7, 2), (2, 1.7), (2, 0.3), (1.7, 0), (0.3, 0), (0, 0.3), (0, 3.7), (0.3, 4), (2, 4)],
    '7': [(0.5, 0), (2, 4), (0, 4)],
    '8': [(0.3, 0), (0, 0.3), (0, 1.7), (0.3, 2), (1.7, 2), (2, 2.3), (2, 3.7), (1.7, 4), (0.3, 4), (0, 3.7), (0, 2.3), (0.3, 2), (1.7, 2), (2, 1.7), (2, 0.3), (1.7, 0), (0.3, 0)],
    '9': [(0, 0), (1.7, 0), (2, 0.3), (2, 3.7), (1.7, 4), (0.3, 4), (0, 3.7), (0, 2.3), (0.3, 2), (1.7, 2), (2, 2.3)],
    '-': [(0, 2), (1.2, 2)],
    'space': [(0, 0), (0, 1.1)],
    'A': [(0, 0), (1, 4), (2, 0), (1.5, 2), (0.5, 2)],
    'a': [(0, 0), (1, 2), (2, 0), (1.5, 1), (0.5, 1)],
    'B': [(0, 0), (0, 4), (1.5, 4), (2, 3.5), (2, 2.5), (1.5, 2), (0, 2), (1.5, 2), (2, 1.5), (2, 0.5), (1.5, 0), (0, 0)],
    'C': [(2, 4), (0.5, 4), (0, 3.5), (0, 0.5), (0.5, 0), (2, 0)],
    'D': [(0, 0), (0, 4), (1.5, 4), (2, 3.5), (2, 0.5), (1.5, 0), (0, 0)],
    'E': [(2, 0), (0, 0), (0, 2), (2, 2), (0, 2), (0, 4), (2, 4)],
    'F': [(0, 0), (0, 2), (2, 2), (0, 2), (0, 4), (2, 4)],
    'G': [(2, 4), (0.5, 4), (0, 3.5), (0, 0.5), (0.5, 0), (2, 0), (2, 1.5), (1.5, 1.5)],
    'H': [(0, 0), (0, 4), (0, 2), (2, 2), (2, 4), (2, 0)],
    #'H': [((0, 0), (0, 2), (2, 2)), ((0, 2), (0, 4)), ((2, 0), (2, 4))],
    'I': [(0, 0), (1, 0), (0.5, 0), (0.5, 4), (0, 4), (1, 4)],
    'J': [(2, 4), (2, 0.5), (1.5, 0), (0.5, 0), (0, 0.5)],
    'K': [(0, 4), (0, 0), (0, 2), (2, 4), (0, 2), (2, 0)],
    'L': [(0, 4), (0, 0), (2, 0)],
    'M': [(0, 0), (0, 4), (1, 2), (2, 4), (2, 0)],
    'N': [(0, 0), (0, 4), (2, 0), (2, 4)],
    'O': [(0.5, 0), (0, 0.5), (0, 3.5), (0.5, 4), (1.5, 4), (2, 3.5), (2, 0.5), (1.5, 0), (0.5, 0)],
    'P': [(0, 0), (0, 4), (1.5, 4), (2, 3.5), (2, 2.5), (1.5, 2), (0, 2)],
    'Q': [(0.5, 0), (0, 0.5), (0, 3.5), (0.5, 4), (1.5, 4), (2, 3.5), (2, 0.5), (1.75, 0.25), (1.5, 0.5), (2, 0), (1.75, 0.25), (1.5, 0), (0.5, 0)],
    'R': [(0, 0), (0, 4), (1.5, 4), (2, 3.5), (2, 2.5), (1.5, 2), (0, 2), (1.5, 2), (2, 1.5), (2, 0)],
    'S': [(0, 0.5), (0.5, 0), (1.5, 0), (2, 0.5), (2, 1.5), (1.5, 2), (0.5, 2), (0, 2.5), (0, 3.5), (0.5, 4), (1.5, 4), (2, 3.5)],
    'T': [(1, 0), (1, 4), (0, 4), (2, 4)],
    'U': [(0, 4), (0, 0.5), (0.5, 0), (1.5, 0), (2, 0.5), (2, 4)],
    'V': [(0, 4), (1, 0), (2, 4)],
    'W': [(0, 4), (0.5, 0), (1, 4), (1.5, 0), (2, 4)],
    'X': [(0, 4), (2, 0), (1, 2), (0, 0), (2, 4)],
    'Y': [(0, 4), (1, 2), (1, 0), (1, 2), (2, 4)],
    'Z': [(2, 0), (0, 0), (2, 4), (0, 4)]
}
