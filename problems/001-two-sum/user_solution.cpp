#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {
        // Write your code here
        unordered_map<int, int> seen;
        for (int i = 0; i < (int)nums.size(); i++) {
            if (seen.count(target - nums[i]))
                return {seen[target - nums[i]], i};
            seen[nums[i]] = i;
        }
        return {};
    }
};
