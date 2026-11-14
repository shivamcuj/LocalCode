# 838. Linear Search

**Difficulty:** Basic

Given an array of integers `nums` and an integer `target`, find the smallest index (0-based indexing) where the target appears in the array. If the target is not found in the array, return `-1`.

## Example 1

**Input:**
```text
nums = [2, 3, 4, 5, 3], target = 3
```

**Output:**
```text
1
```

**Explanation:** The first occurrence of 3 in `nums` is at index 1.

## Example 2

**Input:**
```text
nums = [2, -4, 4, 0, 10], target = 6
```

**Output:**
```text
-1
```

**Explanation:** The value 6 does not occur in the array, hence the output is -1.

## Function Signature

Implement the following method and return the smallest index containing `target`, or `-1` if it is absent:

- **C++:** `int linearSearch(vector<int>& nums, int target)`
- **JavaScript:** `linearSearch(nums, target)`
- **Python:** `linearSearch(nums, target)`

## Input Assumption

The supplied statement does not specify array-length or integer-value constraints. The test cases use non-empty arrays and integer values.
