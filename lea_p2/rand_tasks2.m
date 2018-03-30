function T = rand_tasks2(n_x,n_y)
Sequence_A_up=randperm(n_x*n_y,n_x*n_y);
layer_up = floor(Sequence_A_up/n_x)+1;
rack_up = rem(Sequence_A_up,n_x);
T = [rack_up;layer_up]';
end