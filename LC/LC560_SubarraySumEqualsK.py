from typing import List

class Solution:
    def subarraySum(self, nums: List[int], k: int) -> int:
        # sum of nums between boundary i and boundary j  =  P[j] − P[i]
        res, curSum = 0,0
        prefixSum = {0 : 1}

        for n in nums:
            curSum += n
            diff = curSum - k #diff is the prefix value a left boundary must have

            res += prefixSum.get(diff,0) #How many boundaries to my left carry the value diff?
            prefixSum[curSum] = 1 + prefixSum.get(curSum,0)
            print("prefix", prefixSum)
        return res


if __name__ == "__main__":
    s = Solution()
    print(s.subarraySum(nums = [1,1,1], k = 2))