from typing import List


class Solution:
    def productExceptSelfNaive(self, nums: List[int]) -> List[int]:
        # fails at zero
        n = 1
        for i in nums:
            n *= i

        final_list = []
        for i in range(0, len(nums)):
            final_list.append(int(n/nums[i]))
        return final_list

    def productExceptSelf(self, nums: List[int]) -> List[int]:
        n = len(nums)
        out = [1] * n

        prefix = 1
        for i in range(n):
            out[i] = prefix
            prefix *= nums[i]
            print("out", out)
            print("prefix", prefix)


        suffix = 1
        for i in range(n-1,-1,-1):
            out[i] *= suffix
            suffix *= nums[i]
            print("suffix", suffix)
            print("out", out)
        return out





if __name__ == "__main__":
    s = Solution()
    #print(s.productExceptSelfNaive([1, 2, 3, 4]))
    print(s.productExceptSelf([1, 2, 3, 4]))

