# coding:utf-8
import numpy as np

NUM_RACK = 8  # 货架排数
NUM_LAYER = 8  # 货架层数
NUM_PACK = 20  # 每排货架最大托盘数
NUM_RGV = 1  # 每排货架穿梭车数量
NUM_FORK = 8  # 叉车数量
NUM_TASK = 200  # 任务数

LENGTH = 1  # 货架单位托盘长度(m)
WIDTH = 2  # 货架宽度(m)
HEIGHT = 0.5  # 货架层高(m)
S_RGV = 0.6  # 穿梭车速度(m/s)
S_FORK = 2  # 叉车速度(m/s)
S_FORK_LIFT = 0.3  # 叉车升降速度(m/s)
M = 1e7
E = 0.2  # 距离精度
DELT_T = 0.05  # 时间精度

busy_FORK = np.zeros(NUM_FORK, dtype=float)  # 叉车忙率
busy_RGV = np.zeros((NUM_LAYER, NUM_RACK), dtype=float)  # 穿梭车忙率


def randomTask(layer, rack, pack, count):
    rt = np.zeros((layer, rack), dtype=int)
    while count > 0:
        r_layer = np.random.randint(0, layer)
        r_rack = np.random.randint(0, rack)
        r_packs = np.random.randint(0, pack)
        if rt[r_layer, r_rack] <= pack - r_packs:
            rt[r_layer, r_rack] += r_packs
            count -= r_packs
    return rt


def getNonZero(m_tasks):
    ii = np.nonzero(m_tasks)
    return np.array([ii[0], ii[1]], dtype=int).T


def assign(task_position, tasks, tasks_raw, fork_state):
    rgv_time_predict = (NUM_PACK - tasks_raw[tuple(task_position)] + tasks[tuple(task_position)]) * LENGTH / S_RGV
    delt_rf = np.zeros(NUM_FORK, dtype=float)
    for i in range(NUM_FORK):
        if fork_state[i, -1] == -1:
            temp_rgv_hp = task_position[0] * HEIGHT + 2 * fork_state[i, 2] - fork_state[i, 0] if fork_state[i, 4] == 1 else task_position[0] * HEIGHT + fork_state[i, 0]
            temp_rgv_wp = task_position[1] * WIDTH + 2 * fork_state[i, 3] - fork_state[i, 1] if fork_state[i, 4] == 1 else task_position[1] * WIDTH + fork_state[i, 1]
            fork_time_predict = temp_rgv_hp / S_FORK_LIFT + temp_rgv_wp / S_FORK
            delt_rf[i] = abs(fork_time_predict - rgv_time_predict)
        else:
            delt_rf[i] = -1
    if sum(delt_rf) > -1 * NUM_FORK:
        delt_rf[delt_rf == -1] = M
        return np.unravel_index(delt_rf.argmin(), delt_rf.shape)[0]
    else:
        return -1


def updateFORK(fork_state):
    global busy_FORK
    for i, fork in enumerate(fork_state):
        if fork[2] != -1:
            if fork[4] == 1:
                if abs(fork[0] - fork[2]) > E:
                    fork_state[i, 0] += DELT_T * S_FORK_LIFT
                    busy_FORK[i] += DELT_T
                elif abs(fork[1] - fork[3]) > E:
                    fork_state[i, 1] += DELT_T * S_FORK
                    busy_FORK[i] += DELT_T
                else:
                    fork_state[i, 5] = 1
            elif fork[4] == 0:
                if fork[0] > E:
                    fork_state[i, 0] -= DELT_T * S_FORK_LIFT
                    busy_FORK[i] += DELT_T
                elif fork[1] > E:
                    fork_state[i, 1] -= DELT_T * S_FORK
                    busy_FORK[i] += DELT_T
                else:
                    fork_state[i, 4] = 1
                    fork_state[i, 2:4] = fork_state[i, -2:]
                    fork_state[i, -2:] = -1
    return fork_state


def updateRGV(rgv_state):
    global busy_RGV
    for pos in [(il, ir) for il in range(NUM_LAYER) for ir in range(NUM_RACK)]:
        state = rgv_state[tuple(pos)]
        if state[2] == 1 and state[3] == 0:
            if state[1] - state[0] > E:
                rgv_state[tuple(pos)][0] += DELT_T * S_RGV
                busy_RGV[tuple(pos)] += DELT_T
            else:
                rgv_state[tuple(pos)][2] = 0
        elif state[2] == 0:
            if state[0] > E:
                rgv_state[tuple(pos)][0] -= DELT_T * S_RGV
                busy_RGV[tuple(pos)] += DELT_T
            else:
                rgv_state[tuple(pos)][1] -= LENGTH
                rgv_state[tuple(pos)][2] = 1
                rgv_state[tuple(pos)][3] = 1
    return rgv_state


"""初始化"""
t = 0
tasks = randomTask(NUM_LAYER, NUM_RACK, NUM_PACK, NUM_TASK)  # 生成随机任务(层,排,个)
tasks_raw = tasks.copy()
RGV_state = np.zeros((NUM_LAYER, NUM_RACK, 4), dtype=float)  # 穿梭车位置及当前任务位置(层,排,[位(m),位(m),进1回0,到达])
RGV_state[:, :, 1] = NUM_PACK * LENGTH  # 穿梭车初始任务位置
RGV_state[:, :, 2] = 1  # 初始方向为朝里方向
RGV_state[:, :, 3] = 1
FORK_state = np.zeros((NUM_FORK, 8), dtype=float)  # 叉车位置及当前任务位置及下一任务位置(层(m),排(m),层(m),排(m),进1回0,到达,层(m),排(m))
FORK_state[:, 2:] = -1  # 无任务为-1
FORK_state[:, 4] = 1  # 初始方向为进入方向
FORK_state[:, 5] = 0
# 分配初始任务
for pos in getNonZero(tasks):
    whichfork = assign(pos, tasks, tasks_raw, FORK_state)
    if whichfork != -1:
        FORK_state[whichfork, -2:] = [pos[0] * HEIGHT, pos[1] * WIDTH]
        FORK_state[whichfork, 2:4] = [pos[0] * HEIGHT, pos[1] * WIDTH]
        tasks[tuple(pos)] -= 1
FORK_state[:, -2:] = -1

"""开始仿真"""
while True:
    t += DELT_T
    FORK_state = updateFORK(FORK_state)
    RGV_state = updateRGV(RGV_state)
    # 作一轮指派
    for pos in getNonZero(tasks):
        if RGV_state[tuple(pos)][3] == 1:
            whichfork = assign(pos, tasks, tasks_raw, FORK_state)
            if whichfork != -1:
                FORK_state[whichfork, -2:] = [pos[0] * HEIGHT, pos[1] * WIDTH]
                if FORK_state[whichfork, 2] == -1 and FORK_state[whichfork, 3] == -1:
                    FORK_state[whichfork, 2:4] = [pos[0] * HEIGHT, pos[1] * WIDTH]
                    FORK_state[whichfork, -2:] = -1
                tasks[tuple(pos)] -= 1
    # 处理交接
    for i, fork in enumerate(FORK_state):
        if fork[5] == 1:  # 叉车准备就绪
            task_pos = fork[2:4]
            task_pos = (int(task_pos[0] / HEIGHT), int(task_pos[1] / WIDTH))
            if RGV_state[task_pos][3] == 1:  # 穿梭车准备就绪
                FORK_state[i, 4] = 0  # 叉车返回
                FORK_state[i, 5] = 0  # 叉车撤销就绪状态
                FORK_state[i, 2:4] = FORK_state[i, -2:]  # 叉车更新当前任务
                FORK_state[i, -2:] = -1  # 叉车可被指派
                RGV_state[task_pos][3] = 0  # 穿梭车撤销就绪状态

    total_percent = 1 - np.sum(tasks)/np.sum(tasks_raw)  # 总完成度

    if t % 1 < 0.1:
        print('clock:', int(t), end='')
        print(" finish:", total_percent)

    if total_percent == 1:
        print('完成{}托盘，总用时{}s'.format(NUM_TASK, int(t)))
        print('叉车平均忙率：{}\n穿梭车平均忙率{}'.format(np.mean(busy_FORK / t), np.mean(busy_RGV / t)))
        break
