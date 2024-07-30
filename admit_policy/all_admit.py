#已完成
# from ..lib.dequedict import DequeDict
# from ..lib.heapdict import HeapDict
from .admit_BASE import admit_BASE


class ALL_ADMIT(admit_BASE):
    def judge(self,obj):#判斷是否admit
        return True

    