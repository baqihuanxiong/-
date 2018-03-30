# -*- coding: utf-8 -*-

import random
import numpy as np
import matplotlib.pyplot as plt
from GA import GA


class DUOSYS(object):

    def __init__(self, type, num_task, in_out, life_count=100, v_x=4, v_y=1,
                 ct=3, n_x=36, n_y=10, width=0.5, height=0.55):
        self.type = type
        self.v_x = v_x
        self.v_y = v_y
        self.ct = ct
        self.n_x = n_x
        self.n_y = n_y if self.type == 'one' else int(n_y / 2)
        self.width = width
        self.height = height
        self.num_task = num_task if self.type == 'one' else int(num_task / 2)
        self.tasks = self.generate_tasks(self.num_task, in_out)
        self.empty_time1 = 0
        self.empty_time2 = 0
        self.time_consum1 = 0
        self.time_consum2 = 0
        self.life_count = life_count
        self.ga = GA(aCrossRate=0.05,
                     aMutationRage=0.05,
                     aLifeCount=self.life_count,
                     aGeneLenght=len(self.tasks),
                     aMatchFun=self.matchFun())

    def generate_tasks(self, num_task, in_out):
        tasks = []
        if num_task > self.n_x * self. n_y:
            raise Exception("任务数大于储位数", self.n_x * self.n_y)
        for i in range(num_task):
            while True:
                t_next = [random.randint(1, self.n_x),
                          random.randint(1, self.n_y),
                          random.randint(0, 1) if in_out else 0]
                if t_next not in tasks:
                    tasks.append(t_next)
                    break
        return tasks

    def test_tasks(self, file_path):
        with open(file_path, 'r') as fh:
            self.tasks = []
            for line in fh.readlines():
                l = line.split(',')
                self.tasks.append([int(i) for i in l])

    def time_one(self, order):
        time_consum = 0
        self.empty_time1 = 0
        self.empty_time2 = 0
        pos = [0, 0]
        temp_spdx = self.width / self.v_x
        temp_spdy = self.height / self.v_y
        for c, i in enumerate(order):
            if self.tasks[i][2] == 1:
                time_consum += max(pos[0] * temp_spdx, pos[1] * temp_spdy) + \
                    max(self.tasks[i][0] * temp_spdx, self.tasks[i][1] * temp_spdy) + self.ct
                if c < int(len(order) / 2) or self.type == 'one':
                    self.empty_time1 += max(pos[0] * temp_spdx, pos[1] * temp_spdy)
                else:
                    self.empty_time2 += max(pos[0] * temp_spdx, pos[1] * temp_spdy)
                pos = self.tasks[i][:2]
            else:
                time_consum += max(abs(pos[0] - self.tasks[i][0]) * temp_spdx, \
                                   abs(pos[1] - self.tasks[i][1]) * temp_spdy) + \
                    max(self.tasks[i][0] * temp_spdx, self.tasks[i][1] * temp_spdy) + self.ct
                if c < int(len(order) / 2) or self.type == 'one':
                    self.empty_time1 += max(abs(pos[0] - self.tasks[i][0]) * temp_spdx, \
                                            abs(pos[1] - self.tasks[i][1]) * temp_spdy)
                else:
                    self.empty_time2 += max(abs(pos[0] - self.tasks[i][0]) * temp_spdx, \
                                            abs(pos[1] - self.tasks[i][1]) * temp_spdy)
                pos = [0, 0]
        return time_consum

    def time_all(self, order):
        time_consumption = 0
        if self.type == 'one':
            time_consumption = self.time_one(order)
        else:
            self.time_consum1 = self.time_one(order[:int(len(order)/2)])
            self.time_consum2 = self.time_one(order[int(len(order)/2):])
            time_consumption = max(self.time_consum1, self.time_consum2)
        return time_consumption


    def matchFun(self):
        return lambda life: 1.0 / self.time_all(life.gene)

    def run_ga(self, n=0):
        gen_t = []
        gen_e1 = []
        gen_e2 = []
        gens = n
        while n > 0:
            self.ga.next()
            time_consumption = self.time_all(self.ga.best.gene)
            gen_t.append(time_consumption)
            gen_e1.append(self.empty_time1 / self.time_consum1 * 100)
            gen_e2.append(self.empty_time2 / self.time_consum2 * 100)
            print(("%d : %f , %f") % (self.ga.generation, time_consumption, self.empty_time1 / time_consumption))
            n -= 1
        print("best:", self.ga.best.gene)
        raw_order = np.array(self.tasks)
        print(raw_order[self.ga.best.gene])
        f,(ax1, ax2) = plt.subplots(1, 2)
        ax1.plot([i for i in range(gens)], gen_t)
        ax1.set_title('Single Stack Time Consumption vs Generation')
        ax1.set_xlabel('Generation')
        ax1.set_ylabel('Time Consumption (s)')
        ax2.plot([i for i in range(gens)], gen_e1)
        ax2.plot([i for i in range(gens)], gen_e2)
        ax2.set_title('Single Stack Empty Ratio vs Generation')
        ax2.set_xlabel('Generation')
        ax2.set_ylabel('Empty Ratio (%)')
        plt.show()


if __name__ == '__main__':
    duosys = DUOSYS(type='four', num_task=100, in_out=True)
    # with open(r'C:\Users\沈立文\OneDrive\Documents\物流自动化技术\lea_p2\test_tasks.txt', 'w') as fh:
    #     for task in duosys.tasks:
    #         fh.write(str(task[0]) + ',' + str(task[1]) + ',' + str(task[2]) + '\n')
    # data = r'C:\Users\沈立文\OneDrive\Documents\物流自动化技术\lea_p2\test_tasks.txt'
    # duosys.test_tasks(data)
    duosys.run_ga(10000)
