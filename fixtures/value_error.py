def parse_age(value):
    age = int(value)
    return age


def parse_score(value):
    score = float(value)
    return score


def get_index(items, target):
    return items.index(target)


age = parse_age("twenty")
print(age)

score = parse_score("abc")
print(score)

numbers = [1, 2, 3]
idx = get_index(numbers, 99)
print(idx)
