#取得hit_rate的MLP改成用統計的 region size 1000
#前100w筆
from .admit_BASE import admit_BASE
from lib.dequedict import DequeDict

#改寫DequeDict
class my_cache(DequeDict):
    '''
    保存cache內容
    使用region維護cache_value
    '''
    def __init__(self,cache_size,region,region_size=1000):
        super().__init__()
        self.region=region#方便取用region_counter的 region_value
        self.region_size=region_size


        self.value=0#cache_value
        self.obj_num=0#cache中 obj數
        self.region_vlaue=[0 for _ in range((cache_size//region_size)+1)] #region總價值
        self.region_obj_num=[0 for _ in range((cache_size//region_size)+1)] #region總obj數
    #
    def pushFirst(self, key, value):
        super().pushFirst(key, value)
        r=value.o_size//self.region_size
        self.obj_num+=1
        self.region_obj_num[r]+=1 
        self.update_cache_value(value.o_size)           

    def _remove(self, key):
        value=super()._remove(key)
        r=value.o_size//self.region_size
        self.obj_num-=1
        self.region_obj_num[r]-=1
        self.update_cache_value(value.o_size)
        

    def _push(self, key, value):
        super()._push(key, value)
        r=value.o_size//self.region_size
        self.obj_num+=1
        self.region_obj_num[r]+=1
        self.update_cache_value(value.o_size)


    def update_cache_value(self,o_size):#region_obj_num改變時、region_val改變時 會用到
        r=o_size//self.region_size
        self.value-=self.region_vlaue[r]
        self.region_vlaue[r]=self.region.region_val[r]*self.region_obj_num[r]
        self.value+=self.region_vlaue[r]

    def get_avg_cache_value(self):
        if self.obj_num==0:
            return 0
        return self.value/self.obj_num

        
        

    

class RLV(admit_BASE):
    class entry():
        def __init__(self,obj):
            self.o_size=obj.o_size
            self.o_block=obj.o_block
            self.hit=False
            

    class region_counter():#用linked_list紀錄
        '''
        以link_list方式紀錄n筆紀錄、統計出region_value
        更新時會觸發更新cache_value
        '''
        class Node():
            def __init__(self,data):
                self.data=data
                self.next=None
            
        def __init__(self,cache_size,region_size,keep_num=1000000):
            self.update_cache_value=None
            self.region_size=region_size
            self.region_hit=[0 for _ in range((cache_size//region_size)+1)] #各region造成hit的次數
            self.region_val=[0 for _ in range((cache_size//region_size)+1)] #各region的價值

            #link_list_init
            self.head=self.Node(None)
            self.tail=self.head
            for _ in range(keep_num-1):
                temp=self.Node(None)
                self.tail.next=temp
                self.tail=temp

        def append(self,data):
            #region_update
            self._add_update(data)

            #linked_list
            evicted=self.head.data
            self.head=self.head.next
            self.tail.next=self.Node(data)
            self.tail=self.tail.next

            #將尾端踢除 region_update
            self._remove_update(evicted)
            
            return evicted
        
        def _add_update(self,obj):#剛入region的更新
            r=obj.o_size//self.region_size
            # self.region_num[r]+=1

            self.region_hit[r]+=1
            self.region_val[r]=self.region_hit[r]/((r+1)*self.region_size)

            self.update_cache_value(obj.o_size)

        def _remove_update(self,obj):#從obj踢除的更新
            if obj:
                r=obj.o_size//self.region_size
                # self.region_num[r]-=1

                self.region_hit[r]-=1
                self.region_val[r]=self.region_hit[r]/((r+1)*self.region_size)

                self.update_cache_value(obj.o_size)
        
        
        def get_region_val(self,o_size):
            r=o_size//self.region_size
            return self.region_val[r]

    # class my_history:  
    #     '''
    #     在接收到request時，判斷該o_block在LRU准入下是否會hit
    #     '''
        
    #     def __init__(self,region,cache_size):#RS_entry
    #         self.region=region
    #         self.cache_size=cache_size
    #         self.counter={}# {o_block : o_size}
            
    #     def req_in(self,obj):
    #         remove_list=[]#儲存counter值大於cache_size者，方便之後移除
    #         if obj.o_block in self.counter:
    #             self.region.append(obj)  #將obj送給region做統計
    #             self.counter[obj.o_block]=obj.o_size #回到原點
    #         else:
    #             self.counter[obj.o_block]=0 #後面會一起加上o_size
    #             for o_block in self.counter:
    #                 self.counter[o_block]+=obj.o_size
    #                 if self.counter[o_block]>self.cache_size:
    #                     remove_list.append(o_block)

    #         #將超過cache_size的conter移除(未命中 不用納入region)
    #         for o_block in remove_list:
    #             del self.counter[o_block]

   




    def __init__(self,cache_size):
        region_size=1000
        keep_num=1000000
        
        self.cache_size=cache_size
        #由region維護link_list和region資訊  因為兩者高度相關
        self.region=self.region_counter(cache_size,region_size,keep_num)

        #由cache維護cache_value資訊
        self.cache=my_cache(cache_size,self.region,region_size)
        self.region.update_cache_value=self.cache.update_cache_value

        
        self.LRU=DequeDict()
    
        # self.history=self.my_history(self.region,cache_size)

    def _myLRU(self,obj):#維護all_admit_LRU ，共region統計用

        if obj.o_block in self.LRU: #hit
            self.region.append(obj)#檢查傳入cache_entry有沒有問題
        else:   #miss
            while(obj.o_size>self.cache_size-self.LRU.cached_count):
                victim=self.LRU.popFirst()
        self.LRU[obj.o_block]=obj #放入/更新位置
        

    def request(self, obj):
        self._myLRU(obj)

        # self.history.req_in(obj)


    def evict(self, victim):
        del self.cache[victim.o_block]


        

    def hit(self, obj):
        self.cache[obj.o_block].hit=True
        
    def addToCache(self, obj):
        self.cache[obj.o_block]=self.entry(obj)


    def GET_DEBUG_MESSAGE(self):
        message="cache_value:"+str(self.cache.get_avg_cache_value())
        return message    

    def judge(self,obj):
        #有剩餘空間直接准入
        if obj.o_size<(self.cache_size-self.cache.cached_count):
            return True
        else:
            if self.region.get_region_val(obj.o_size)>self.cache.get_avg_cache_value():
                return True
            else:
                return False
    
        

        
        # cache_value=self.cache.value #cache_size要在evict發生時更新(較省時)
        # region_value[region_i]#region_value也要在evict發生時更新

        


        
        
        
