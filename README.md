# Polling server real-time simulator

This project simulated a polling server scheduled by RM algorithm for single-server systems.

Here is the valid input format:
In `samples` directory put your values in `.txt` format like this sample:

```text
ser 5 2
per 4 1
per 6 2
aper 2 2
aper 8 1
aper 12 2
aper 19 1
24
```

- `ser` stands for `server` -> The first value is the charge period and the second one is the charge amount
- `per` stands for `periodic` -> The first value is the period and the second one is the execution time
- `aper` stands for `aperiodic` -> The first value is the arrival time and the second one is the execution time
- And the value in the latest line displays the simulation time. If there are no values LCM will be chosen by default.

Here is a sample output:
![image](https://github.com/armindelgosar/Polling-server/assets/60629485/b7301f5b-74da-4fa7-b8e1-c64e585c5c51)
