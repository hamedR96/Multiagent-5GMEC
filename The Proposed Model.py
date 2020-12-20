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

def du_distribution_data (agent, message):
    agent.t= message[1]+(message[0]/(800*random.randint(9, 10)/10))**1.1
    agent.d= message[0]
    #print('data is in distribution:',[agent.d, agent.t])
    if  agent.d > 1000:
        agent.send('du2fog',[1000,agent.t])
        agent.send('du2cu',[agent.d-1000,agent.t])
    else:
        agent.send('du2fog',[agent.d,agent.t])

def cu_distribution_data (agent, message):
    agent.t= message[1]
    agent.d= message[0]
    #print('data is in distribution:',[agent.d, agent.t])
    if  agent.d > 2000:
        agent.send('cu2mec',[2000,agent.t])
        agent.send('cu2cloud',[agent.d-2000,agent.t])
    else:
        agent.send('cu2mec',[agent.d,agent.t])        
             

def fog_computing(agent, message):
    agent.d= message[0]
    agent.t= message[1]
    #print('data is in edge:',[agent.d, agent.t])
    agent.send('fog2du',[agent.d,agent.t])
    
    
def mec_computing(agent, message):
    agent.d= message[0]
    agent.t= message[1]
    #print('data is in edge:',[agent.d, agent.t])
    agent.send('mec2cu',[agent.d,agent.t])

def cloud_computing(agent, message):
    agent.d= message[0]
    agent.t= message[1]+(message[0]/800)**1.3
    #print('data is in cloud:',[agent.d, agent.t])
    agent.send('cloud2cu',[agent.d,agent.t])


def cloud_collecting(agent, message):
    agent.d= message[0]
    agent.t= message[1]+(message[0]/800)**1.3
    #print('data is back from edge:',[agent.d, agent.t])
    agent.send('cu2du',[agent.d,agent.t])

def mec_collecting(agent, message):
    agent.d= message[0]
    agent.t= message[1]
    #print('data is back from cloud:',[agent.d, agent.t])
    agent.send('cu2du',[agent.d,agent.t])
    
    
def du_collecting(agent, message):
    agent.d= message[0]
    agent.t= message[1]
    #print('data is back from cloud:',[agent.d, agent.t])
    agent.send('du2ue',[agent.d,agent.t])
    
    
def result(agent,message):
    agent.t= message[1]+(message[0]/(800*random.randint(9, 10)/10))**1.1
    #print('result:',[agent.d, agent.t])
    #agent.log_info('timeout: %s' % agent.t)
    agent.f=agent.f+agent.t
    #agent.log_info('TOTAL timeout: %s' % agent.f)
       
  
if __name__ == '__main__':
    
    ns = run_nameserver()
    
    ue = run_agent('UE')
    ue.set_method(set_t)
    ue.set_method(set_d)
    ue.set_method(set_f)
    
    du = run_agent('5GDU')
    du.set_method(set_t)
    du.set_method(set_d)
    
    
    fog= run_agent('Fog')
    fog.set_method(set_t)
    fog.set_method(set_d)
    
    cu = run_agent('5GCU')
    cu.set_method(set_t)
    cu.set_method(set_d)
    
    mec = run_agent('MEC')
    mec.set_method(set_t)
    mec.set_method(set_d)
    
    cloud = run_agent('Cloud')
    cloud.set_method(set_t)
    cloud.set_method(set_d)
    
    addr_ue2du = ue.bind('PUSH', alias='ue2du')
    addr_du2fog = du.bind('PUSH', alias='du2fog')
    addr_du2cu = du.bind('PUSH', alias='du2cu')
    addr_cu2mec = cu.bind('PUSH', alias='cu2mec')
    addr_cu2cloud = cu.bind('PUSH', alias='cu2cloud')
    addr_cloud2cu = cloud.bind('PUSH', alias='cloud2cu')
    addr_mec2cu = mec.bind('PUSH', alias='mec2cu')
    addr_cu2du = cu.bind('PUSH', alias='cu2du')
    addr_fog2du = fog.bind('PUSH', alias='fog2du')
    addr_du2ue = du.bind('PUSH', alias='du2ue')

    
    du.connect(addr_ue2du, alias='ue2du', handler=du_distribution_data)
    fog.connect(addr_du2fog, alias='du2fog', handler=fog_computing)
    cu.connect(addr_du2cu, alias='du2cu',handler=cu_distribution_data)
    mec.connect(addr_cu2mec, alias='cu2mec',handler= mec_computing)
    cloud.connect(addr_cu2cloud,  alias='cu2cloud', handler= cloud_computing )
    cu.connect(addr_cloud2cu, alias='cloud2cu', handler= cloud_collecting)
    cu.connect(addr_mec2cu, alias='mec2cu', handler=mec_collecting)
    du.connect(addr_cu2du, alias='cu2du', handler=du_collecting)
    du.connect(addr_fog2du, alias='fog2du',handler=du_collecting)
    ue.connect(addr_du2ue, alias='du2ue',handler=result)
    
    
    ue.set_t(0)
    ue.set_f(0)
    ue.set_d(0)
    
    du.set_t(0)
    du.set_d(0)
    
    fog.set_t(0)
    fog.set_d(0)
    
    cu.set_t(0)
    cu.set_d(0)
    
    mec.set_t(0)
    mec.set_d(0) 
    
    cloud.set_t(0)
    cloud.set_d(0) 
    
   
    final= [ [ 0 for i in range(2) ] for j in range(100)]
    ue.d=0
    ue.t= 0
    ue.f=0
    for i in range (0,100):
        ue.d=ue.d+50
        ue.send('ue2du',[ue.d, ue.t])  
        time.sleep(0.1)
        final[i]=[ue.d, ue.f]
        ue.t= 0
        ue.f=0
    
    ns.shutdown()
   
    B = np.array(final)
    
    with open('fig3.csv', 'w') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',')
        csv_writer.writerow(B[:,0])
        csv_writer.writerow(B[:,1])
    
    plt.plot(B[:,0], B[:,1],'-o')
    plt.xlim(0, 5000)
    plt.ylim(0, 60)
    plt.legend()
    plt.show()

    #print(final)