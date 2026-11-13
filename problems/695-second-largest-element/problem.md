# 695. Second Largest Element

Given an array of integers `nums`, return the **second-largest distinct element** in the array. If the second-largest element does not exist, return `-1`.

## Example 1

**Input:**
```text
nums = [8, 8, 7, 6, 5]
```

**Output:**
```text
7
```

**Explanation:** The largest value in `nums` is 8, and the second-largest distinct value is 7.

## Example 2

**Input:**
```text
nums = [10, 10, 10, 10, 10]
```

**Output:**
```text
-1
```

**Explanation:** The only distinct value in `nums` is 10, so a second-largest distinct value does not exist. Therefore, -1 is returned.

## Function Signature

Implement the following method and return the second-largest distinct integer, or `-1` if it does not exist:

- **C++:** `int secondLargestElement(vector<int>& nums)`
- **JavaScript:** `secondLargestElement(nums)`
- **Python:** `secondLargestElement(nums)`

## Input Assumption

The supplied statement does not specify array-length or integer-value constraints. The test cases use non-empty arrays and integer values.

**Note:** “Second largest” means the second-largest *distinct* value. Repeated occurrences of the maximum do not count as a second value.
