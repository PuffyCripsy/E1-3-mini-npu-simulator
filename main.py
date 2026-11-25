
import json
import math
import re
import time
from pathlib import Path

EPSILON = 1e-9


# 1. 사용자 입력 함수
def input_matrix(name, size=3):
    print(f"\n{name} ({size}줄 입력, 공백 구분)")
    matrix = []

    for i in range(size):
        while True:
            try:
                row = list(map(float, input(f"{i + 1}행: ").split()))

                if len(row) != size or not all(math.isfinite(x) for x in row):
                    print(f"입력 오류: 각 줄에 유한한 숫자 {size}개를 입력하세요.")
                    continue

                matrix.append(row)
                break

            except ValueError:
                print("입력 오류: 숫자만 입력하세요.")

    return matrix


# 2. MAC 연산 함수
def mac(pattern, filter_matrix):
    score = 0.0

    for i in range(len(pattern)):
        for j in range(len(pattern[i])):
            score += pattern[i][j] * filter_matrix[i][j]

    return score


# 3. 점수 비교 및 판정
def decide(score_a, score_b, label_a="A", label_b="B"):
    if abs(score_a - score_b) < EPSILON:
        return "UNDECIDED"

    return label_a if score_a > score_b else label_b


# 4. MAC 연산 시간 측정
def measure_mac_time(pattern, filter_matrix, repeats=10):
    total = 0.0

    for _ in range(repeats):
        start = time.perf_counter()
        mac(pattern, filter_matrix)
        total += time.perf_counter() - start

    return total / repeats * 1000


# 5. 보너스 과제: Cross/X 패턴 자동 생성
def generate_pattern(size, label):
    if size < 3 or size % 2 == 0:
        raise ValueError("패턴 크기는 3 이상의 홀수여야 합니다.")

    if label not in ("Cross", "X"):
        raise ValueError("패턴 종류는 Cross 또는 X여야 합니다.")

    center = size // 2
    result = []

    for i in range(size):
        row = []

        for j in range(size):
            if label == "Cross":
                on = (i == center or j == center)
            else:
                on = (i == j or i + j == size - 1)

            row.append(1.0 if on else 0.0)

        result.append(row)

    return result


# 6. 행렬 크기 및 숫자 검증
def valid_matrix(matrix, size):
    return (
        isinstance(matrix, list)
        and len(matrix) == size
        and all(
            isinstance(row, list)
            and len(row) == size
            and all(
                type(value) in (int, float) and math.isfinite(value)
                for value in row
            )
            for row in matrix
        )
    )


# 7. 라벨 정규화
def normalize_label(value):
    if not isinstance(value, str):
        raise ValueError("라벨이 문자열이 아닙니다.")

    label = value.strip().lower()

    if label in ("+", "cross"):
        return "Cross"

    if label == "x":
        return "X"

    raise ValueError(f"알 수 없는 라벨: {value}")

# 필터 키 정규화
def normalize_filter_keys(item):
    if not isinstance(item, dict):
        return None

    normalized = {}

    for key, matrix in item.items():
        standard_key = normalize_label(key)
        normalized[standard_key] = matrix

    return normalized

# 8. 크기별 성능 분석
def performance_table(sizes):
    print("\n[성능 분석: 각 패턴 10회 측정]")
    print(f"{'크기':<9} {'평균 시간(ms)':>15} {'연산 횟수(N²)':>16}")

    for size in sizes:
        cross = generate_pattern(size, "Cross")
        x_pattern = generate_pattern(size, "X")

        avg_cross = measure_mac_time(cross, cross)
        avg_x = measure_mac_time(x_pattern, x_pattern)

        average = (avg_cross + avg_x) / 2

        print(f"{size}×{size:<6} {average:>15.6f} {size * size:>16}")


# 9. 모드 1: 3×3 사용자 입력
def mode_input():
    filter_a = input_matrix("필터 A")
    filter_b = input_matrix("필터 B")

    print("\n필터 저장 완료")

    pattern = input_matrix("패턴")

    score_a = mac(pattern, filter_a)
    score_b = mac(pattern, filter_b)

    result = decide(score_a, score_b)

    print("\n[MAC 연산 결과]")
    print(f"A 점수: {score_a}")
    print(f"B 점수: {score_b}")

    if result == "UNDECIDED":
        print("판정: 판정 불가")
    else:
        print("판정:", result)

    avg = measure_mac_time(pattern, filter_a)

    print(f"평균 연산 시간(10회): {avg:.6f} ms")
    print("연산 횟수(N²): 9")


# 10. 모드 2: data.json 분석
def mode_json():
    filepath = Path(__file__).with_name("data.json")

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)

        filters = data["filters"]
        patterns = data["patterns"]

        if not isinstance(filters, dict) or not isinstance(patterns, dict):
            raise ValueError("filters/patterns는 객체여야 합니다.")

    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
        print(f"JSON 로드 오류: {error}")
        return

    print("\n[필터 로드]")

    for size in (5, 13, 25):
        item = filters.get(f"size_{size}")

        try:
            normalized_item = normalize_filter_keys(item)
        except ValueError:
            normalized_item = None

        good = (
            isinstance(normalized_item, dict)
            and valid_matrix(normalized_item.get("Cross"), size)
            and valid_matrix(normalized_item.get("X"), size)
        )

        print(
            f"size_{size}: "
            f"{'확인 완료' if good else '오류(케이스별 FAIL 처리)'}"
        )

    passed = 0
    failures = []

    print("\n[패턴 분석]")

    for case_id, case in patterns.items():
        try:
            matched = re.fullmatch(r"size_(\d+)_(\d+)", case_id)

            if matched is None:
                raise ValueError("케이스 키 형식 오류")

            size = int(matched.group(1))
            selected = filters.get(f"size_{size}")

            if not isinstance(selected, dict):
                raise ValueError(f"size_{size} 필터 누락")

            cross_filter = selected.get("cross")
            x_filter = selected.get("x")

            if not valid_matrix(cross_filter, size) or not valid_matrix(x_filter, size):
                raise ValueError("필터 크기/숫자 형식 오류")

            if not isinstance(case, dict) or not valid_matrix(case.get("input"), size):
                raise ValueError("패턴 크기/숫자 형식 오류")

            expected = normalize_label(case.get("expected"))

            score_cross = mac(case["input"], cross_filter)
            score_x = mac(case["input"], x_filter)

            result = decide(score_cross, score_x, "Cross", "X")

            if result == expected:
                passed += 1
                status = "PASS"
            else:
                status = "FAIL"

                if result == "UNDECIDED":
                    reason = "동점 처리(UNDECIDED)"
                else:
                    reason = "예상 라벨과 판정 불일치"

                failures.append((case_id, reason))

            print(
                f"{case_id}: Cross={score_cross:.12g}, "
                f"X={score_x:.12g} | 판정={result} | "
                f"expected={expected} | {status}"
            )

        except (ValueError, TypeError, KeyError) as error:
            failures.append((case_id, str(error)))
            print(f"{case_id}: FAIL ({error})")

    performance_table((3, 5, 13, 25))

    print("\n[결과 요약]")
    print(
        f"총 테스트: {len(patterns)}개 / "
        f"통과: {passed}개 / 실패: {len(failures)}개"
    )

    if failures:
        print("실패 케이스:")

        for case_id, reason in failures:
            print(f"- {case_id}: {reason}")


# 11. 메인 프로그램
def main():
    print("=== Mini NPU Simulator ===")
    print("1. 사용자 입력 (3×3)")
    print("2. data.json 분석")

    choice = input("선택: ").strip()

    if choice == "1":
        mode_input()
    elif choice == "2":
        mode_json()
    else:
        print("잘못된 선택입니다.")


if __name__ == "__main__":
    main()
