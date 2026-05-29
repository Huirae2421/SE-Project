"""
attribute_error.py: 클래스에서 자주 하는 실수 (AttributeError)
정의하지 않은 메서드를 호출한다.
"""


class Dog:
    def __init__(self, name):
        self.name = name

    def bark(self):
        print(f"{self.name}: 멍멍!")


dog = Dog("바둑이")
dog.bark()

# 정의하지 않은 메서드를 호출 -> AttributeError
dog.run()
