# 951. Pattern 19

Given an integer `n`, recreate the pattern shown below for the given value of `n`.

Print the pattern inside the function provided.

## Example 1

**Input:**
```text
n = 4
```

**Output:**

![Pattern 19 for n = 4](https://static.takeuforward.org/content/1789474065_eDSnBu9_.webp)

## Example 2

**Input:**
```text
n = 2
```

**Output:**

![Pattern 19 for n = 2](https://static.takeuforward.org/content/1789474073_tG6IiNZg.webp)

## Output pattern in text form

The attached screenshot in this package is also included as `attached-pattern-reference.png`.

For `n = 4`, the exact pattern is:

```text
* * * * * * * *
* * *     * * *
* *         * *
*             *
*             *
* *         * *
* * *     * * *
* * * * * * * *
```

For `n = 2`, the exact pattern is:

```text
* * * *
*     *
*     *
* * * *
```

## Constraints

- `1 <= n <= 100`

## Function Signature

Print the pattern in the provided method. The method does not return a value.

- **C++:** `void pattern19(int n)`
- **JavaScript:** `pattern19(n)`
- **Python:** `pattern19(n)`
