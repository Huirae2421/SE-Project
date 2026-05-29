"""
error_guide.py: 오류 유형별 해결 가이드 제공 (한국어/영어)

각 오류에 대한 원인, 해결 방법, 잘못된/올바른 코드 예시, 학습 개념을
한국어와 영어로 제공한다. 코드 예시는 언어와 무관하므로 공통으로 둔다.
"""

from dataclasses import dataclass
from typing import Optional


# ──────────────────────────────────────────────
# 데이터 클래스
# ──────────────────────────────────────────────

@dataclass
class ErrorGuide:
    error_type: str
    cause: str
    solution: str
    example_wrong: str
    example_fixed: str
    concept: str
    cause_en: str = ""
    solution_en: str = ""
    concept_en: str = ""


# ──────────────────────────────────────────────
# 오류별 가이드 정의
# ──────────────────────────────────────────────

ERROR_GUIDES = {
    "NameError": ErrorGuide(
        error_type="NameError",
        cause="정의되지 않은 변수나 함수를 사용했습니다.",
        solution="변수를 사용하기 전에 먼저 값을 할당하여 정의해야 합니다. 오타가 없는지도 확인하세요.",
        example_wrong="print(x)",
        example_fixed="x = 10\nprint(x)",
        concept="변수 정의와 스코프",
        cause_en="You used a variable or function that has not been defined.",
        solution_en="Define the variable by assigning a value before using it, and check for typos.",
        concept_en="Variable definition and scope",
    ),
    "TypeError": ErrorGuide(
        error_type="TypeError",
        cause="서로 다른 자료형끼리 연산하거나, 잘못된 자료형을 사용했습니다.",
        solution="연산하려는 값들의 자료형을 일치시키세요. 필요 시 int(), str() 등으로 형 변환을 해야 합니다.",
        example_wrong='result = "나이: " + 25',
        example_fixed='result = "나이: " + str(25)',
        concept="자료형과 형 변환",
        cause_en="You combined values of different types, or used a wrong type.",
        solution_en="Make the value types match. Convert with int(), str(), etc. when needed.",
        concept_en="Data types and type conversion",
    ),
    "IndexError": ErrorGuide(
        error_type="IndexError",
        cause="리스트나 문자열의 범위를 벗어난 인덱스에 접근했습니다.",
        solution="인덱스가 0부터 시작하며 길이-1까지만 유효함을 기억하세요. len()으로 길이를 먼저 확인하세요.",
        example_wrong="items = [1, 2, 3]\nprint(items[3])",
        example_fixed="items = [1, 2, 3]\nprint(items[2])",
        concept="인덱싱과 리스트 길이",
        cause_en="You accessed an index outside the range of a list or string.",
        solution_en="Indexes start at 0 and go up to length-1. Check the length with len() first.",
        concept_en="Indexing and list length",
    ),
    "ValueError": ErrorGuide(
        error_type="ValueError",
        cause="자료형은 맞지만 변환할 수 없는 값을 전달했습니다.",
        solution="변환하려는 값이 올바른 형식인지 확인하세요. 예를 들어 int()에는 숫자 형태의 문자열만 전달해야 합니다.",
        example_wrong='age = int("스물")',
        example_fixed='age = int("20")',
        concept="값 검증과 예외 처리",
        cause_en="The type was right, but the value could not be converted.",
        solution_en="Check the value is in a valid format. For example, int() needs a numeric string.",
        concept_en="Value validation and exceptions",
    ),
    "IndentationError": ErrorGuide(
        error_type="IndentationError",
        cause="들여쓰기가 올바르지 않습니다. 공백이 일관되지 않게 사용되었습니다.",
        solution="같은 블록 안에서는 동일한 들여쓰기(보통 공백 4칸)를 사용하세요. 탭과 공백을 섞지 마세요.",
        example_wrong="def func():\nprint('hello')",
        example_fixed="def func():\n    print('hello')",
        concept="들여쓰기 규칙과 코드 블록",
        cause_en="The indentation is incorrect or inconsistent.",
        solution_en="Use the same indentation (usually 4 spaces) within a block. Don't mix tabs and spaces.",
        concept_en="Indentation rules and code blocks",
    ),
    "SyntaxError": ErrorGuide(
        error_type="SyntaxError",
        cause="문법 규칙에 맞지 않는 코드가 있습니다. 콜론, 괄호 등이 누락되었을 수 있습니다.",
        solution="콜론(:), 괄호의 짝, 따옴표가 올바른지 확인하세요. 오류가 발생한 줄의 바로 윗줄도 확인하세요.",
        example_wrong="def func()\n    return 1",
        example_fixed="def func():\n    return 1",
        concept="기본 문법 규칙",
        cause_en="The code breaks a grammar rule. A colon, bracket, or quote may be missing.",
        solution_en="Check colons (:), matching brackets, and quotes. Also check the line just above.",
        concept_en="Basic syntax rules",
    ),
    "ZeroDivisionError": ErrorGuide(
        error_type="ZeroDivisionError",
        cause="0으로 나누기를 시도했습니다.",
        solution="나누기 전에 분모가 0이 아닌지 조건문으로 확인하세요.",
        example_wrong="result = 10 / 0",
        example_fixed="divisor = 0\nif divisor != 0:\n    result = 10 / divisor",
        concept="나눗셈과 조건 검사",
        cause_en="You tried to divide by zero.",
        solution_en="Check that the denominator is not zero with an if statement before dividing.",
        concept_en="Division and condition checking",
    ),
    "KeyError": ErrorGuide(
        error_type="KeyError",
        cause="딕셔너리에 존재하지 않는 키에 접근했습니다.",
        solution="키가 존재하는지 in 연산자로 확인하거나, get() 메서드를 사용하세요.",
        example_wrong='d = {"a": 1}\nprint(d["b"])',
        example_fixed='d = {"a": 1}\nprint(d.get("b", "기본값"))',
        concept="딕셔너리 키 접근",
        cause_en="You accessed a key that does not exist in the dictionary.",
        solution_en="Check existence with the 'in' operator, or use the get() method.",
        concept_en="Dictionary key access",
    ),
    "AttributeError": ErrorGuide(
        error_type="AttributeError",
        cause="객체(클래스 인스턴스 등)에 존재하지 않는 속성이나 메서드를 호출했습니다. 클래스를 처음 다룰 때 자주 발생합니다.",
        solution="클래스에 그 메서드를 정의했는지, 이름에 오타가 없는지 확인하세요. 자료형(리스트/정수 등)에 맞는 메서드인지도 점검하세요.",
        example_wrong='class Dog:\n    def bark(self):\n        print("bark")\n\nd = Dog()\nd.run()',
        example_fixed='class Dog:\n    def bark(self):\n        print("bark")\n\nd = Dog()\nd.bark()',
        concept="클래스의 속성과 메서드",
        cause_en="You called an attribute or method that the object (e.g. a class instance) does not have. Common when first learning classes.",
        solution_en="Check the method is defined in the class and spelled correctly, and that it fits the type.",
        concept_en="Class attributes and methods",
    ),
    "ModuleNotFoundError": ErrorGuide(
        error_type="ModuleNotFoundError",
        cause="설치되지 않았거나 이름이 틀린 모듈을 import 했습니다.",
        solution="모듈 이름 철자를 확인하세요. 외부 라이브러리라면 터미널에서 'pip install 모듈명'으로 먼저 설치해야 합니다.",
        example_wrong="import numpyy",
        example_fixed="import numpy",
        concept="모듈과 import",
        cause_en="You imported a module that is not installed or whose name is misspelled.",
        solution_en="Check the spelling. For external libraries, install first with 'pip install <name>'.",
        concept_en="Modules and import",
    ),
    "UnboundLocalError": ErrorGuide(
        error_type="UnboundLocalError",
        cause="함수 안에서 바깥(전역) 변수를 수정하려다, 파이썬이 그 변수를 지역 변수로 취급해서 발생합니다.",
        solution="함수 안에서 바깥 변수를 바꾸려면 global 선언을 하거나, 값을 인자로 받아 계산한 뒤 반환하세요.",
        example_wrong="count = 0\ndef add():\n    count = count + 1\n    return count",
        example_fixed="def add(count):\n    return count + 1",
        concept="변수 스코프(지역/전역)",
        cause_en="You tried to modify an outer (global) variable inside a function, so Python treated it as local.",
        solution_en="Use a 'global' declaration, or pass the value as an argument and return the result.",
        concept_en="Variable scope (local/global)",
    ),
    "RecursionError": ErrorGuide(
        error_type="RecursionError",
        cause="재귀 함수에 멈추는 조건이 없어 자기 자신을 무한히 호출했습니다.",
        solution="재귀를 멈추는 기저 조건(base case)을 반드시 넣어 더 이상 호출하지 않도록 하세요.",
        example_wrong="def factorial(n):\n    return n * factorial(n - 1)",
        example_fixed="def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)",
        concept="재귀와 종료 조건",
        cause_en="A recursive function had no stopping condition and called itself forever.",
        solution_en="Always add a base case so the function stops calling itself.",
        concept_en="Recursion and base case",
    ),
}


# ──────────────────────────────────────────────
# 언어별 안내 문구
# ──────────────────────────────────────────────

NOT_READY = {
    "ko": "이 오류에 대한 가이드가 아직 준비되지 않았습니다.",
    "en": "A guide for this error is not available yet.",
}

UNKNOWN_CONCEPT = {"ko": "알 수 없음", "en": "Unknown"}


# ──────────────────────────────────────────────
# ErrorGuideProvider
# ──────────────────────────────────────────────

class ErrorGuideProvider:

    def get_guide(self, error_type: str) -> Optional[ErrorGuide]:
        return ERROR_GUIDES.get(error_type)

    def has_guide(self, error_type: str) -> bool:
        return error_type in ERROR_GUIDES

    # ──────────────────────────────────────────────
    # 언어별 필드 선택
    # ──────────────────────────────────────────────

    def _pick(self, ko_value: str, en_value: str, lang: str) -> str:
        if lang == "en" and en_value:
            return en_value
        return ko_value

    def get_cause(self, error_type: str, lang: str = "ko") -> str:
        guide = self.get_guide(error_type)
        if guide is None:
            return NOT_READY.get(lang, NOT_READY["ko"])
        return self._pick(guide.cause, guide.cause_en, lang)

    def get_solution_text(self, error_type: str, lang: str = "ko") -> str:
        guide = self.get_guide(error_type)
        if guide is None:
            return NOT_READY.get(lang, NOT_READY["ko"])
        return self._pick(guide.solution, guide.solution_en, lang)

    def get_concept(self, error_type: str, lang: str = "ko") -> str:
        guide = self.get_guide(error_type)
        if guide is None:
            return UNKNOWN_CONCEPT.get(lang, UNKNOWN_CONCEPT["ko"])
        return self._pick(guide.concept, guide.concept_en, lang)

    def get_full_guide_text(self, error_type: str, lang: str = "ko") -> str:
        guide = self.get_guide(error_type)
        if guide is None:
            return NOT_READY.get(lang, NOT_READY["ko"])

        if lang == "en":
            labels = ("Cause", "Solution", "Wrong example", "Correct example", "Concept")
        else:
            labels = ("원인", "해결 방법", "잘못된 예", "올바른 예", "학습 개념")

        lines = [
            f"[{guide.error_type}]",
            f"{labels[0]}: {self.get_cause(error_type, lang)}",
            f"{labels[1]}: {self.get_solution_text(error_type, lang)}",
            "",
            f"{labels[2]}:",
            guide.example_wrong,
            "",
            f"{labels[3]}:",
            guide.example_fixed,
            "",
            f"{labels[4]}: {self.get_concept(error_type, lang)}",
        ]
        return "\n".join(lines)

    def list_supported_errors(self) -> list:
        return list(ERROR_GUIDES.keys())
