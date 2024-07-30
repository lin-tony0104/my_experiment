class MLP(torch.nn.Module):
    def __init__(self,input_size):
        super(MLP,self).__init__()
        #網路初始化
        self.input_size=input_size
        self.fc1=torch.nn.Linear(self.input_size,128)
        self.fc2=torch.nn.Linear(128,256)
        self.fc3=torch.nn.Linear(256,1)

        #其他設置
        self.lossfunc=torch.nn.BCELoss()
        self.optimizer=torch.optim.Adam(params=self.parameters(),lr=0.005)


        self.batch_size=20
        self.buffer_X=[]#data
        self.buffer_Y=[]#tag
        
        #因為batch滿了才會更新神經網路  所以用prob_table儲存結果 用以省去取值的計算
        #prob_table會跟神經網路同時更新
        self.prob_table=[0 for _ in range(self.input_size)]
    def forward(self,din):
        #din轉換資料

        din=self.transform_data(din)
        din=din.view(-1,self.input_size)
        

        dout=F.relu(self.fc1(din))
        dout=F.relu(self.fc2(dout))
        dout=F.sigmoid(self.fc3(dout))
        return dout
    

    def add_data(self,new_X,new_Y):#X:size Y:tag     x:osize   y: 0/1tag
        self.buffer_X.append(new_X)
        self.buffer_Y.append(int(new_Y))
        
        #如果batch滿了就train
        if len(self.buffer_X)>=self.batch_size:
            self.train()
            self.update_prob()


    def train(self):
        #運用buffer中資料訓練
        data=self.buffer_X
        target=torch.Tensor(self.buffer_Y)
        
        self.optimizer.zero_grad()
        output=self(data)#
        loss=self.lossfunc(output,target.view(-1,1))
        loss.backward()
        self.optimizer.step()
        
        #清空buffer
        self.buffer_X=[]#data
        self.buffer_Y=[]#tag

    def update_prob(self):
        # 使用 torch.no_grad() 獲取預測值
        with torch.no_grad():
            for i in range(self.input_size):
                self.prob_table[i]=self([np.exp(i)])
        # print("updated prob_table:",self.prob_table)


    def get_prob(self, data):
        x=int(np.floor(np.log(int(data))))
        return self.prob_table[x]


    def transform_data(self,data):
        result=[]
        for i in data:
            temp_i=int(np.floor(np.log(int(i))))
            temp_result=[0 for _ in range(self.input_size)]
            temp_result[temp_i]=1
            result.append(temp_result)
        return torch.Tensor(result)
#---------------------以上是MLP功能---------------------


