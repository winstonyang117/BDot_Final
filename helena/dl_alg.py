'''
author: ming
ming.song.cn@outlook.com
copyright@2020
'''
import os
import sys
import numpy as np
from torch import nn
import copy
from random import sample
from math import isnan
import datetime
import pickle


class LstmAttentionNet(nn.Module):
    def __init__(self):
        super(LstmAttentionNet, self).__init__()
        hidden_size = 60
        attention_size = hidden_size
        self.lstm = nn.LSTM(input_size=100, hidden_size=hidden_size, batch_first=True, num_layers=3)
        self.w_omega = nn.Parameter(torch.randn(hidden_size,attention_size))
        self.b_omega = nn.Parameter(torch.randn(attention_size))
        self.u_omega = nn.Parameter(torch.randn(attention_size,1))
        self.decoding_layer = nn.Linear(hidden_size, 2)


    def forward(self, x):
        out, (h, c) = self.lstm(x)
        v = torch.matmul(out,self.w_omega)+self.b_omega
        vu = torch.matmul(v, self.u_omega)
        weight= nn.functional.softmax(vu,dim=1)
        out_weighted = torch.sum(out*weight,1)
        y_pred = self.decoding_layer(out_weighted)

        return y_pred#, weight



class DL_Model():
    """docstring for DL_Model."""

    def __init__(self, SMOOTH=60):
        super(DL_Model, self).__init__()
        ####
        # self.device = torch.device('cuda' if cuda.is_available() else 'cpu')
        self.device = torch.device('cpu')

        # self.c_Net = CNN_LSTM_Net()
        # self.c_Net = LSTM()
        self.c_Net = LstmAttentionNet()
        self.c_Net = self.c_Net.to(device = self.device)

        print(f"Using device:{self.device}")


    def load_model(self, model_path):
        if os.path.exists(os.path.join(model_path,"scaler_param.pk")):
            with open(os.path.join(model_path,"scaler_param.pk"),"rb+") as f:
                [self.scaler_x,self.scaler_y, self.window_len] = pickle.load(f)
        else:
            print(f'scaler_param.pk not exist!')
            quit()

        if os.path.exists(os.path.join(model_path,"torch_model.ckpt")):
            self.c_Net.load_state_dict(torch.load(os.path.join(model_path,"torch_model.ckpt"),map_location=torch.device(self.device)))
        else:
            print(f'torch_model.ckpt not exist!')
            quit()

        print('Model parameters loaded!')

        # if os.path.exists(os.path.join(model_path,"error.pk")):
        #     with open(os.path.join(model_path,"error.pk"),"rb+") as f:
        #         self.error = pickle.load(f)
        # else:
        #     print(f'error.pk not exist!')
        #     quit()

    def predict(self, pred_x):
        # import pdb; pdb.set_trace()

        self.pred_x = self.scaler_x.transform([pred_x[:3000]])
        self.pred_x = self.pred_x[:, :(self.window_len // 100) * 100].reshape(len(self.pred_x),-1,100)

        self.tensor_pred_x = torch.tensor(self.pred_x,dtype=torch.float32,device=self.device)
        # self.train_y_pred = self.scaler_y.inverse_transform(self.c_Net(self.tensor_pred_x[:,np.newaxis,:]).cpu().detach().numpy())
        self.train_y_pred = self.scaler_y.inverse_transform(self.c_Net(self.tensor_pred_x).cpu().detach().numpy())

        return np.round(self.train_y_pred)[0]

    # def evaluate(self, VERBOSE=False, INFLUX=False):
    #     pass
