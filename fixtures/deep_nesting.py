def analyze_data(data):
    if data:
        for item in data:
            if isinstance(item, dict):
                for key, value in item.items():
                    if isinstance(value, list):
                        for element in value:
                            if element > 0:
                                if element % 2 == 0:
                                    print(f"짝수: {element}")
                                else:
                                    print(f"홀수: {element}")
                            else:
                                print(f"음수: {element}")
                    else:
                        print(f"값: {value}")
            else:
                print(f"항목: {item}")
    else:
        print("데이터 없음")


def process_matrix(matrix):
    result = []
    for i in range(len(matrix)):
        row = []
        for j in range(len(matrix[i])):
            if matrix[i][j] > 0:
                for k in range(matrix[i][j]):
                    if k % 2 == 0:
                        row.append(k * 2)
                    else:
                        row.append(k)
            else:
                row.append(0)
        result.append(row)
    return result


def find_nested(items, target, depth=0):
    for item in items:
        if isinstance(item, list):
            for sub in item:
                if isinstance(sub, list):
                    for element in sub:
                        if element == target:
                            return depth
        elif item == target:
            return depth
    return -1


sample_data = [
    {"scores": [10, -2, 4, 7], "name": "test"},
    {"values": [1, 3, 5], "label": "sample"},
    "simple_item"
]

analyze_data(sample_data)

matrix = [[1, 2, 3], [0, 4, 1], [2, 0, 5]]
processed = process_matrix(matrix)
print(processed)

nested = [[1, [2, 3]], [4, 5]]
print(find_nested(nested, 3))
