#已完成
from lib.heapdict import HeapDict
from .evict_BASE import evict_BASE
class LFU(evict_BASE):
    class LFU_Entry:
        def __init__(self,o_block,o_size,obj,freq=1):
            self.o_block=o_block
            self.o_size=o_size
            self.freq=freq

            self.main_cache_entry=obj#為了回傳cache_entry，所以保存

        def __lt__(self,other):
            if self.freq==other.freq:
                return self.o_block<other.o_block
            return self.freq<other.freq
        

    def __init__(self,cache_size):
        self.cache_size=cache_size
        self.cache=HeapDict()
        self.req_count=0
        
    

#============================    
    def request(self,obj):
        '''接收「request資訊」 , req_obj型態是cache_Entry'''
        if obj.hit:
            self.cache[obj.o_block].freq+=1

    def addToCache(self,obj):
        #剛清完空間，把obj放入cache
        """接收「新增到cache的obj」 , obj型態是cache_Entry"""
        obj=self.LFU_Entry(obj.o_block,obj.o_size,obj)
        self.cache[obj.o_block]=obj
         
    def evict(self):
        return self.cache.popMin().main_cache_entry #

