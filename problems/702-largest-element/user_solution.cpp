class Solution {
public:
    int largestElement(vector<int>& nums) {
        int l=nums[0];
        int n = nums.size();
        if(n==1){
            return l;
        }else{
            for(int i=1;i<n;i++){
                if(nums[i]>l){
                    l=nums[i];
                }
            }
            return l;
        }
    }    
};