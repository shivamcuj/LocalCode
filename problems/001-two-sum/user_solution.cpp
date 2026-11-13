#include <bits/stdc++.h>
using namespace std;
class Solution { public: vector<int> twoSum(vector<int>& nums,int target){ unordered_map<int,int> seen; for(int i=0;i<(int)nums.size();i++){int x=nums[i]; if(seen.count(target-x)) return {seen[target-x],i}; seen[x]=i;} return {}; } };