def greet(name):
    message = "Hello, " + name
    return message


def add(a, b):
    result = a + b
    return result


def is_even(n):
    if n % 2 == 0:
        return True
    return False


def print_numbers(limit):
    for i in range(limit):
        print(i)


name = "CLAP"
greeting = greet(name)
print(greeting)

total = add(3, 5)
print(total)

print(is_even(4))
print_numbers(5)
