"""
recursion_error.py: 종료 조건 없는 재귀 (RecursionError)
"""


def factorial(n):
    # 멈추는 기저 조건이 없어 무한 재귀 -> RecursionError
    return n * factorial(n - 1)


print(factorial(5))
