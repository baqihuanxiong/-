clc,clear

v_x = 4;  % �Ѷ��ƽ��ˮƽ�ٶ�
v_y = 1;  % �Ѷ��ƽ����ֱ�ٶ�
ct = 3;  % ��������ʱ��
n_x = 36;  % ˮƽ��λ����
n_y = 5;  % ��ֱ��λ����
width = 0.5;  % ��λ��
height = 0.55;  % ��λ��

inde_time = zeros(170,1);
para_time = zeros(170,1);
para_pro_time = zeros(170,1);
c = 1;
for num_task=11:180
    avr_count  = 10;
    inde_sum = 0;
    para_sum = 0;
    para_pro_sum = 0;
    for i=1:avr_count
        T = rand_tasks(num_task,n_x,n_y);
        T_time_inde = sum(T*[width/v_x;2*height/v_y],2)+ct;
        T_time = zeros(num_task,1);
        for j=1:num_task
            T_time(j,1) = max(T(j,1)*width/v_x,T(j,2)*height/v_y)+ct;
        end
        T_time_pro = zeros(num_task,1);
        for j=1:num_task
            T_time_pro(j,1) = max(T(j,1)*width/v_x,(T(j,2)*height/v_y)/2)+ct;
        end
        [x0,p0] = mengte(T_time,num_task);
        [x0_pro,p0_pro] = mengte(T_time_pro,num_task);
        inde_sum = inde_sum+sum(T_time_inde)*2;
        para_sum = para_sum+max(T_time'*x0,T_time'*(1-x0));
        para_pro_sum = para_pro_sum+max(T_time_pro'*x0_pro,T_time_pro'*(1-x0_pro));
    end
    inde_time(c,1) = inde_sum/avr_count;
    para_time(c,1) = para_sum/avr_count;
    para_pro_time(c,1) = para_pro_sum/avr_count;
    c = c+1;
    disp(num_task);
end

figure
ax1 = subplot(1,2,1);
ax2 = subplot(1,2,2);

x = 21:2:360;
plot(ax1,x,para_time,x,inde_time);
title(ax1,'4�Ѷ��DUOSUS��1�Ѷ��DUOSYS���³��ڣ���ҵЧ��');
xlabel(ax1,'������');
ylabel(ax1,'��ʱ��s��');

ratio = zeros(170,1);
for k=1:170
    ratio(k) = inde_time(k,1)/para_time(k,1);
end
plot(ax2,x,ratio);
title(ax2,'4�Ѷ��DUOSUS��1�Ѷ��DUOSYS���³��ڣ���ҵЧ�ʱ�ֵ');
xlabel(ax2,'������');
ylabel(ax2,'4 / 1');

%% �����������1
function T = rand_tasks(nt,n_x,n_y)
T = zeros(nt,2);
T(1,1) = randi([1,n_x]);
T(1,2) = randi([1,n_y]);
for i=2:size(T,1)
    while 1
        T(i,1) = randi([1,n_x]);
        T(i,2) = randi([1,n_y]);
        c_rep = 0;
        for j=1:i-1
            if isequal(T(i,:),T(j,:))
                c_rep = c_rep + 1;
            end
        end
        if c_rep == 0
            break;
        end
    end
end
end

%% �����������2
function T = rand_tasks2(nt,n_x,n_y)
Sequence_A_up=randperm(nt,nt);
layer_up = floor(Sequence_A_up/n_x)+1;
rack_up = rem(Sequence_A_up,n_x);
T = [rack_up;layer_up]';
end

%% ���ؿ��巨����Сֵ
function [x0,p0] = mengte(Tt,nt)
p0 = 1000;
for i=1:10^3
    x = randi([0 1],nt,1);
    f = abs(2*Tt'*x-sum(Tt));
    if p0 >= f
        x0 = x;
        p0 = f;
    end
end
end
