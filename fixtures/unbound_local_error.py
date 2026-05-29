"""
unbound_local_error.py: 지역/전역 변수 혼동 (UnboundLocalError)
"""

count = 0


def increment():
    # 바깥 count 를 수정하려 하지만 지역 변수로 취급됨 -> UnboundLocalError
    count = count + 1
    return count


print(increment())
