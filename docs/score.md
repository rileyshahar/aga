# Determining Score

This section describes the complete semantics for computing the score of a test
case. Each test case is scored as all-or-nothing.

Each problem is sorted into a specific group by virtue of the
[`group`](reference.html#aga.group) decorator. A group consists of every test
case underneath that group, and before the next group decorator. There is an
implicit group consisting of all test cases preceding the first decorator. For
example, in the following setup, there are three groups; one consists of the
negative cases, one of `0`, and one of the positive cases.

```python
@test_case(-2)
@test_case(-1)
@group()
@test_case(0)
@group()
@test_case(1)
@test_case(2)
@problem()
def square(x: int) -> int:
    return x * x
```

Each group is first assigned a total score, and then each test case in a group
is assigned a score. These processes work identically; we will think of either a
group or a test case as a scorable object. Scorable objects possess a _value_
(default 0), which is absolute, and a _weight_ (default 1), which is relative.
There is some pot of points, the _total score_ which is available as an input to
the algorithm; this is determined by the classroom frontend for the group case,
and the output of the group algorithm for the indivial test case.

For each object, the algorithm first sets its score to its value, decrementing
the total score by that value. The algorithm allows for the sum of values to
potentially be larger than the total available score; in this case, extra credit
will be available, and relative weights will have no effect. The algorithm then
divides the remaining total score according to weight.

For example, consider the following problem with total score 20.

```python
@test_case(-2, aga_weight = 2)
@test_case(-1, aga_weight = 0, aga_value = 2.0)
@test_case(0, aga_weight = 2, aga_value = 4.0)
@test_case(1, aga_value = 2.0)
@test_case(2)
@problem()
def square(x: int) -> int:
    return x * x
```

Every test case is in the implicit group, which has weight one and value zero,
and so it is assigned all 20 points. We have the following weights and values:

| Case | Weight | Value |
| ---- | ------ | ----- |
| -2   | 2      | 0.0   |
| -1   | 0      | 2.0   |
| 0    | 2      | 4.0   |
| 1    | 1      | 2.0   |
| 2    | 1      | 0.0   |

First, processing values leaves total score 12 and gives the following temporary
scores:

| Case | Score |
| ---- | ----- |
| -2   | 0.0   |
| -1   | 2.0   |
| 0    | 4.0   |
| 1    | 2.0   |
| 2    | 0.0   |

Next, we divide the remaining 12 units of score amongst the 6 units of weight,
so each unit of weight represents 2 units of score. This give the final scores.

| Case | Score |
| ---- | ----- |
| -2   | 4.0   |
| -1   | 2.0   |
| 0    | 8.0   |
| 1    | 4.0   |
| 2    | 2.0   |
