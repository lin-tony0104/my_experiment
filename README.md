# ASC_IP
## 執行

  ```
  python run.py
  ```

## 實驗結果
- LRU / all_admit:
  - cache_size:2748779070
  - 命中率:46.77%
  
- LECAR / all_admit:
  - cache_size:2748779070
  - 命中率:46.83%
- LRU / region_LRU_value:
  - cache_size:2748779070
  - 命中率:62.84%
  
- LECAR / region_LRU_value:
  - cache_size:2748779070
  - 命中率:62.72%

- LRU / Imitate_ASC_IP:
  - cache_size:2748779070
  - 命中率:70.37%
  
- LECAR / Imitate_ASC_IP:
  - cache_size:2748779070
  - 命中率:70.23%


## 程式結構
- admit_policy 資料夾:
  - 裡面專門放admit策略，供cache_system使用
  - 除了admit_BASE.py是共用父類別，其餘皆是policy
- evict_policy 資料夾:
  - 裡面專門放evict策略，供cache_system使用
  - 除了evict_BASE.py是共用父類別，其餘皆是policy
- lib:
  - 放deque,heap的lib可以用來實作LRU,LFU
- cache_system.py:
  - 快取系統框架，使用指定的呼叫admit_policy,evict_policy達成驅逐及准入，形成完整的快取系統。
- run.py:
  - 程式操作介面和policy的管理。


## 方法:
- admit_policy:
  - all_adnit: 全部准入
  - region_LRU_value:
    - 維護一個LRU計算追蹤不同size_region造成的hit數，計算region_value、cache_value。並且只准入region_value大於cache_value的obj。
    - 屬於折衷辦法(原本是想要維護當前准入策略下 各size_region造成的hit數，但寫出來的程式速度太慢了)
  - Imitate_ASC_IP: 准入版本ASC_IP准入策略
  
- evict_policy:
  - LRU
  - LeCaR

## 問題
- trace因為太大還沒上傳 wiki2018.tr(50 G)
