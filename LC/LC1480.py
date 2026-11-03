class Solution:
    def runningSum(self, nums: list[int]) -> list[int]:
        answer = []
        temp = 0
        for i in range(0,len((nums))):
            temp += nums[i]
            answer.append(temp)
        return answer

if __name__ == "__main__":
    sol = Solution()
    nums = [1, 2, 3, 4]
    print(sol.runningSum(nums))
