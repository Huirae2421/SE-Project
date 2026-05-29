"""
key_error.py: 딕셔너리에 없는 키 접근 (KeyError)
"""

scores = {"kim": 90, "lee": 85}

print(scores["kim"])

# 존재하지 않는 키 -> KeyError
print(scores["park"])
