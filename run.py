'''
run.py完成下列項目:
1. CMD介面+功能
2. 選擇演算法
'''


from cache_system import cache
import matplotlib.pyplot as plt

#evict_policy
from evict_policy.lru import LRU
from evict_policy.lfu import LFU
from evict_policy.lecar import LeCaR
#admit_policy
from admit_policy.all_admit import ALL_ADMIT
from admit_policy.Imitate_ASC_IP import Imitate_ASC_IP
from admit_policy.region_statistical import RS
from admit_policy.remove_p_ASC_IP import remove_p_ASC_IP
from admit_policy.region_LRU_value import RLV


class my_list:
    def __init__(self,name,options):
        self.name=name
        self.options=options
    
    def choice(self):
        info=self.name+":"
        for i in range(len(self.options)):
            info+= (" "+str(i)+"."+self.options[i])

        c=int(input(info))
        return self.options[c][1]





def get_unit(e,a,t):
    cache_size=int(input("cache_size:"))    
    if cache_size==0: cache_size=2748779070
    print("cache_size: ",cache_size)
    name_list=["evict_policy","admit_policy","trace_file"]
    unit_list=[e,a,t]

    result=[]
    selected_info=[]
    for  name , unit in zip(name_list,unit_list):
        info="\nselect the "+name+":\n"
        
        for i in range(len(unit)):
            info+=str(i)+"."+ unit[i][0]+"   "
        info+="\nenter: "
        i=int(input(info))
        selected=unit[i][1]
        selected_info.append(unit[i][0])
        result.append(selected)

    evict_policy=result[0]
    admit_policy=result[1]
    trace_file=result[2]

    return cache_size , evict_policy , admit_policy , trace_file ,selected_info

if __name__ == '__main__':
    print('==============================================================')
    hits = 0
    requests = 0

    #如果有心的策略,trace 要更新下面三個
    evict_list=[("LRU",LRU),("LFU",LFU),("LeCaR",LeCaR)]
    admit_list=[("all_admit",ALL_ADMIT),("Imitate_ASC_IP",Imitate_ASC_IP),("region_statistical",RS),("remove_p_ASC_IP",remove_p_ASC_IP),("region_LRU_value",RLV)]
    trace_list=[("wiki2018.tr","D:/all_Trace/ASC-IP/wiki2018.tr")]

    cache_size , evict_policy , admit_policy , trace_file , selected_info = get_unit(evict_list,admit_list,trace_list)
    #例外狀況
    if cache_size <= 0:
        print("Cache_size should be greater than 0")
        exit(1)
    
    #init
    evict=evict_policy(cache_size)
    admit=admit_policy(cache_size)

    #組裝 admit,evict
    alg = cache(admit,evict,cache_size)
    alg.DEBUG_CACHE_INFO=selected_info[0] +" / "+ selected_info[1] +" / "+ str(cache_size)
    
    #-----------------------------------------


    show_HitRate=[]
    request_num=150000000
    with open(trace_file, 'r') as f:
        for line in f:
            temp=line.split()

            lba = int(temp[1])
            size = int(temp[2])
            if size>cache_size:#如果不寫會造成矛盾， 請求到的object一定會放入cache，但同時又放不下。
                print("object size greater then cache size. ID:",lba)
                exit(1)

            if lba < 0:
                continue
            requests += 1

            hit = alg.requests(lba,size)

            if hit:
                hits += 1
            
            misses = requests - hits

            show_HitRate.append(round(100 * hits / requests, 2))
            # print("hit_rate:",round(100 * hits / requests, 2),"  ",requests,"/",request_num)
            if requests>=request_num:
                break

        plt.plot(list(range(request_num)),show_HitRate)        
        plt.show()
       # print(alg.debug)

