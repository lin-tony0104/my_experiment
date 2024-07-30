#已完成
from lib.dequedict import DequeDict
from lib.heapdict import HeapDict
from .evict_BASE import evict_BASE
import numpy as np

"""
主要功能: 決定出要evict的obj
其他程式碼: 計算驅逐對象的
""" 
class LeCaR(evict_BASE):

    class LeCaR_Entry:
        def __init__(self,obj, freq=1, time=0):
            self.o_block = obj.o_block
            self.freq = freq
            self.time = time
            self.evicted_time = None
            self.o_size=obj.o_size
            #
            self.main_cache_entry=obj

        def __lt__(self, other):
            if self.freq == other.freq:
                return self.o_block < other.o_block
            return self.freq < other.freq

    def __init__(self,cache_size):
        
        self.time=0
        self.cache_size=cache_size
        self.lru=DequeDict()
        self.lfu=HeapDict()

        self.lru_hist=DequeDict()
        self.lfu_hist=DequeDict()

        self.initial_weight = 0.5

        self.learning_rate = 0.45

        self.discount_rate = 0.005**(1 / self.cache_size)
        self.W = np.array([self.initial_weight, 1 - self.initial_weight],
                          dtype=np.float32) #[W_LRU,W_LFU]
        #========DEBUG========
        self.DEBUG_LFU_evict=0
        self.DEBUG_LRU_evict=0



    def request(self,obj):        
        if obj.hit:
            self.time+=1 #hit時
            x=self.lru[obj.o_block]
            x.time=self.time    #regret使用
            x.freq+=1

            self.lru[obj.o_block]=x
            self.lfu[obj.o_block]=x
            


    def addToCache(self,obj):
        x=self.LeCaR_Entry(obj,freq=self.freq,time=self.time)   #注意:freq的用法很怪  freq值是在admit()裡更新的， 因為在主程式cache_system.py裡 呼叫完admit() 接下來一定會呼叫addToCache()。
        self.lru[obj.o_block]=x
        self.lfu[obj.o_block]=x


        
    def evict(self):
        lru=self.lru.first()
        lfu=self.lfu.min()

        evicted=lru
        policy= 0 if np.random.rand() < self.W[0] else 1

        if policy == 0:
            self.DEBUG_LRU_evict+=1
            evicted = lru
            evicted.evicted_time = self.time#用來算reqgret的
            self.addToHistory(evicted, policy)#先判斷有沒有滿 才放入histroy

            #delete from cache
            del self.lru[evicted.o_block]
            del self.lfu[evicted.o_block]
        else:
            self.DEBUG_LFU_evict+=1
            evicted = lfu
            evicted.evicted_time = self.time#
            self.addToHistory(evicted, policy)#先判斷有沒有滿 才放入histroy

            #delete from cache
            del self.lru[evicted.o_block]
            del self.lfu[evicted.o_block]

        # self.DEBUG()
        return evicted.main_cache_entry

    def admit(self,obj):
        oblock=obj.o_block
        osize=obj.o_size

        self.time+=1 #miss但准入時
        self.freq=1
        policy="None"
        reward=0
        if oblock in self.lru_hist:
            policy="LRU"
            entry = self.lru_hist[oblock]
            self.freq = entry.freq + 1
            del self.lru_hist[oblock]
            reward=-(self.discount_rate**(self.time - entry.evicted_time))#為什麼加負號
            
        elif oblock in self.lfu_hist:
            policy="LFU"
            entry = self.lfu_hist[oblock]
            self.freq = entry.freq + 1
            del self.lfu_hist[oblock]
            reward=-(self.discount_rate**(self.time - entry.evicted_time))#為什麼加負號
        self.adjustWeights(policy,reward)
        



    '''================以上為必要函數================'''
    


    def adjustWeights(self,policy,reward): #W=[w_lru,w_lfu]
        if policy=="LRU":
            self.W[1]=self.W[1]*np.exp(self.learning_rate*reward)    
        elif policy=="LFU":
            self.W[0]=self.W[0]*np.exp(self.learning_rate*reward)
        
        self.W[0] = self.W[0] / (self.W[0]+self.W[1])
        self.W[1] = 1-self.W[0]

        if self.W[0] >= 0.99:
            self.W = np.array([0.99, 0.01], dtype=np.float32)
        elif self.W[1] >= 0.99:
            self.W = np.array([0.01, 0.99], dtype=np.float32)
        


    def addToHistory(self, x, policy):#給定lru,lfu

        policy_history = None
        if policy == 0:
            policy_history = self.lru_hist
        else:
            policy_history = self.lfu_hist

        while(x.o_size>(self.cache_size-policy_history.cached_count)):
            evicted = policy_history.first()
            del policy_history[evicted.o_block]
        policy_history[x.o_block] = x

    def DEBUG(self):
        print("LRU_evict:",self.DEBUG_LRU_evict,"  LFU_evict:",self.DEBUG_LFU_evict)