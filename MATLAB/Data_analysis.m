%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% MATLAB SCRIPT FOR DATA ANALYSIS %%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

close all
clear all
clc

% Importing dataset
dataset = readtable('Rebreathing1.csv');
dataset

% Checking if imported data match the requirements. If Var4 is not a double,
% uncomment and execute the two lines of the script below.
% dataset.Var4 = str2double(dataset.Var4);
% dataset.Var4 = dataset.Var4/10; %Restores the float
class(dataset.Var2)
class(dataset.Var4) %Must be a double
class(dataset.CO2Sangue) %Must be 'datetime'

%% Data plotting
% Merged data
figure(1)
plot(dataset.CO2Sangue, dataset.Var2);
hold on
plot(dataset.CO2Sangue, dataset.Sentec);
hold on
plot(dataset.CO2Sangue, dataset.Var4);
title('Raw device data');
ylabel('[CO2] - ppm');
legend('Device CO2', 'Sentec', 'Delta C02');

% Only Sentec data
figure(2)
plot(dataset.CO2Sangue, dataset.Sentec);
title('Raw Sentec data');
ylabel('[CO2] - mmHg');
legend('Sentec');

%% Device data filtering
% Moving average filtering with 10 samples MA(10)
% dev_filt = 1/10*ones(10,1);
% Var2_out = filter(dev_filt,1,dataset.Var2);
% Var4_out = filter(dev_filt,1,dataset.Var4);

% Moving average filtering with 50 samples MA(50)
dev_filt = 1/50*ones(50,1);
Var2_out = filter(dev_filt,1,dataset.Var2);
Var4_out = filter(dev_filt,1,dataset.Var4);

figure(3)
plot(dataset.CO2Sangue, Var2_out);
hold on
plot(dataset.CO2Sangue, Var4_out);
hold on
plot(dataset.CO2Sangue, dataset.Sentec);
title('Filtered device data and raw Sentec data');
ylabel('[CO2] - ppm');
legend('Device CO2', 'Sentec', 'Delta C02');

%% Sentec data filtering
% Moving average filtering with 4 samples MA(4)
%dataset.Sentec(isnan(dataset.Sentec)) = 0;
sentec_filt = 1/4*ones(4,1);
sentec_out = filter(sentec_filt,1,dataset.Sentec);
figure(4)
plot(dataset.CO2Sangue,sentec_out);
title('Filtered Sentec data');
legend('Sentec');

%% Baseline extraction
% Device
baseline_d = dataset.Var2(dataset.CO2Sangue == '2021-10-19 18:45:01.053')
baseline_size = size(dataset.CO2Sangue);
baseline_d = ones(baseline_size)*baseline_d;

% Sentec
baseline_s = dataset.Sentec(dataset.CO2Sangue == '2021-10-19 18:45:01.053')
baseline_s = ones(baseline_size)*baseline_s;
start_rebr = datetime('2021-10-19 18:45:01.053')
end_rebr = datetime('2021-10-19 18:47:01.165')

% Data plotting
figure(5)
plot(dataset.CO2Sangue, Var2_out);
hold on
plot(dataset.CO2Sangue, sentec_out);
hold on
plot(dataset.CO2Sangue, Var4_out);
hold on
plot(dataset.CO2Sangue,baseline_d);
xline(start_rebr,'--','LineWidth',2);
xline(end_rebr,'--','LineWidth',2);
title('Filtered device data and baseline');
ylabel('[CO2] - ppm');
legend('Device CO2', 'Sentec', 'Delta C02','Baseline','Start Rebreathing', ...
    'End Rebreathing');

figure(6)
plot(dataset.CO2Sangue,sentec_out);
hold on
plot(dataset.CO2Sangue,baseline_s);
xline(start_rebr,'--','LineWidth',2);
xline(end_rebr,'--','LineWidth',2);
title('Filtered Sentec data and baseline');
ylabel('[CO2] - mmHg');
legend('Sentec', 'Baseline', 'Start Rebreathing', ...
    'End Rebreathing');

%% Maximum C02 value
% The maxima are computed on the filtered signals from both Sentec and the 
% device
max_sentec = max(sentec_out)
find(sentec_out == max_sentec)
max_device = max(Var2_out(100:end)) %to discard temperature drift
find(Var2_out == max_device)
%max_device_time = find(Var2_out == max_device)

%% Relationship between Sentec CO2 and device CO2
figure(7)
plot(Var2_out,sentec_out)
xlabel('Device [CO2]');
ylabel('Sentec [CO2]');
title('Device [CO2] vs Sentec [CO2]')

%Analizzare meglio la correlazione perchè il plot fa schifo














