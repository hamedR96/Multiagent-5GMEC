from osbrain import run_agent
from osbrain import run_nameserver
import time 
import matplotlib.pyplot as plt
import numpy as np
import random
import csv

def set_f(self, value):
    self.f = value

def set_t(self, value):
    self.t = value

def set_d(self, value):
    self.d = value

def distribution (agent, message):
    agent.t= message[1]+message[0]/(37.5*random.randint(7, 10)/10)**1.2
    agent.d= message[0]
    #print('data is in distribution:',[agent.d, agent.t])
    if  agent.d > 1000:
        agent.send('edge',[1000,agent.t])
        agent.send('cloud',[agent.d-1000,agent.t])
    else:
        agent.send('edge',[agent.d,agent.t])

def edge_computing(agent, message):
    agent.d= message[0]
    agent.t= message[1]+(message[0]/37.5)**1.2
    #print('data is in edge:',[agent.d, agent.t])
    agent.send('edge2',[agent.d,agent.t])

def cloud_computing(agent, message):
    agent.d= message[0]
    agent.t= message[1]+(message[0]/37.5)**1.5
    #print('data is in cloud:',[agent.d, agent.t])
    agent.send('cloud2',[agent.d,agent.t])

def edge_computing2(agent, message):
    agent.d= message[0]
    agent.t= message[1]+(message[0]/37.5)**1.2
    #print('data is back from edge:',[agent.d, agent.t])
    agent.send('lte',[agent.d,agent.t])

def cloud_computing2(agent, message):
    agent.d= message[0]
    agent.t= message[1]+(message[0]/37.5)**1.5
    #print('data is back from cloud:',[agent.d, agent.t])
    agent.send('lte',[agent.d,agent.t])


def prnt(agent,message):
    agent.t= message[1]+message[0]/(37.5*random.randint(7, 10)/10)**1.2
    #print('result:',[agent.d, agent.t])
    #agent.log_info('timeout: %s' % agent.t)
    agent.f=agent.f+agent.t
    #agent.log_info('TOTAL timeout: %s' % agent.f)
       
  
if __name__ == '__main__':
    
    ns = run_nameserver()
    
    edge= run_agent('Edge')
    edge.set_method(set_t)
    edge.set_method(set_d)
    
    ue = run_agent('UE')
    ue.set_method(set_t)
    ue.set_method(set_d)
    ue.set_method(set_f)
    
    cloud = run_agent('Cloud')
    cloud.set_method(set_t)
    cloud.set_method(set_d)
    
    lte = run_agent('LTE')
    lte.set_method(set_t)
    lte.set_method(set_d)
    
    addr_edge = lte.bind('PUSH', alias='edge')
    addr_cloud = lte.bind('PUSH', alias='cloud')
    
    addr_edge2 = edge.bind('PUSH', alias='edge2')
    addr_cloud2 = cloud.bind('PUSH', alias='cloud2')
    
    addr_ue = ue.bind('PUSH', alias='ue')
    addr_lte = lte.bind('PUSH', alias='lte')
    
    edge.connect(addr_edge, alias='edge', handler=edge_computing)
    cloud.connect(addr_cloud, alias='cloud', handler=cloud_computing)
   
    lte.connect(addr_edge2, alias='edge2',handler=edge_computing2)
    lte.connect(addr_cloud2, alias='cloud2',handler=cloud_computing2)
    lte.connect(addr_ue,  alias='ue', handler= distribution )
    
    ue.connect(addr_lte, alias='lte', handler= prnt)
    
    ue.set_t(0)
    edge.set_t(0) 
    cloud.set_t(0) 
    lte.set_t(0) 
    ue.set_f(0)
    ue.set_d(0)
    edge.set_d(0) 
    cloud.set_d(0) 
    lte.set_d(0) 
   
    final= [ [ 0 for i in range(2) ] for j in range(100)]
    ue.d=0
    ue.t= 0
    ue.f=0
    for i in range (0,100):
        ue.d=ue.d+50
        ue.send('ue',[ue.d, ue.t])  
        time.sleep(0.1)
        final[i]=[ue.d, ue.f]
        ue.t= 0
        ue.f=0
    
    ns.shutdown()
    
    B = np.array(final)
    
    
    with open('fig1.csv', 'w') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',')
        csv_writer.writerow(B[:,0])
        csv_writer.writerow(B[:,1])
    
    
    plt.plot(B[:,0], B[:,1],'-o')
    plt.xlim(0, 5000)
    plt.ylim(0, 2500)
    plt.legend()
    plt.show()
    
    #print(final)