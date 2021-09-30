from typing import List

from aga import problem, test_case

@test_case(3, [1, 0, 1, 2], aga_output=[1, 2, 1])
@test_case(6, [1, 5, 0, 0, 5, 2, 5], aga_output=[2, 1, 1, 0, 0, 3])
@test_case(10, [1, 5, 0, 0, 5, 2, 5], aga_output=[2, 1, 1, 0, 0, 3, 0, 0, 0, 0])
@test_case(10, [], aga_output=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
@test_case(1, [0, 0, 0], aga_output=[3])
@test_case(3, [2, 2, 2, 1, 1, 0], aga_output=[1,2,3])
@test_case(1, [0], aga_output=[1])
@test_case(5, [0], aga_output=[1,0,0,0,0])
@test_case(20, [3, 3, 5, 1, 2, 0, 17, 17, 6, 16, 8, 1, 3], aga_output=[1,2,1,3,0,1,1,0,1,0,0,0,0,0,0,0,1,2,0,0])
@test_case(4, [1, 2, 3], aga_output=[0,1,1,1])
@test_case(2, [0, 0, 1, 0, 1, 0, 0, 1], aga_output=[5,3])
@problem()
def counts(n: int, xs: List[int]) -> List[int]:
    """Count the number of occurances of each value in x."""
    counts = [0] * n

    for x in xs:
        counts[x] += 1

    return counts
