from collections import defaultdict
from typing import List


class Solution:

    def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
        freq_map = defaultdict(list)
        for s in strs:
            key = tuple(sorted(s))
            #print(key)
            freq_map[key].append(s)
        #print(freq_map)
        return list(freq_map.values())




if __name__ == "__main__":
    s = Solution()
    strs = ["eat", "tea", "tan", "ate", "nat", "bat"]

    print(s.groupAnagrams(strs))