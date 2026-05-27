def get_first(items):
    return items[0]


def get_last(items):
    return items[len(items)]


def get_element(items, index):
    return items[index]


scores = [90, 85, 78]

print(get_first(scores))
print(get_last(scores))
print(get_element(scores, 10))
