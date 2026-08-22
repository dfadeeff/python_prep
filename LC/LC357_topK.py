from typing import List
import heapq


class Solution:

    def topKFrequentHashMap(self, nums: List[int], k: int) -> List[int]:
        countDict = {}
        for i in nums:
            countDict[i] = 1 + countDict.get(i, 0)

        sortedList = sorted(countDict.items(),key=lambda x: x[1], reverse=True)

        final_list = []
        for (key,value) in sortedList[:k]:
            final_list.append(key)
        return final_list

    def topKFrequentHeap(self, nums: List[int], k: int) -> List[int]:
        countDict = {}
        for i in nums:
            countDict[i] = countDict.get(i,0) + 1

        heap = []
        for key, value in countDict.items():
            heapq.heappush(heap, (value, key))
            if len(heap) > k:
                heapq.heappop(heap)


        return [value for key,value in heap]



if __name__ == "__main__":
    s = Solution()
    # print(s.topKFrequentHashMap(nums=[7,7], k=1))
    # print(s.topKFrequentHashMap(nums=[1, 1, 1, 2, 2, 3], k=2))
    print(s.topKFrequentHeap(nums=[7, 7], k=1))
    print(s.topKFrequentHeap(nums=[1, 1, 1, 2, 2, 3], k=2))
