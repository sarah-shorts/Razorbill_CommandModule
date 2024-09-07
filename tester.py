v_max_ch1 = 100
v_max_ch2 = -15
voltage_steps = 5
type = "Tens."

total_range = abs(v_max_ch2) + abs(v_max_ch1)
voltage_increment = round(total_range / voltage_steps, 1)
print(voltage_increment)

v_steps = []
i_voltage = 0
j_voltage = 0
j = 0
remainder = 0
if type == "Tens.":
    for i in range(0, voltage_steps):
        i_voltage = round(voltage_increment*(i),1)
        if i_voltage <= v_max_ch1:
            v_steps.append([i_voltage, 0])
        if i_voltage > v_max_ch1:
            if j == 0:
                remainder = round(abs(i_voltage - v_max_ch1),1)
                v_steps.append([v_max_ch1, -remainder])
            if j != 0:
                j_voltage = -(remainder+voltage_increment*j)
                v_steps.append([v_max_ch1, round(j_voltage)])
            j = j + 1
    for volt in v_steps:
        if volt[0] > v_max_ch1 or volt[0] < 0:
            print("shits fucked on v1")
        if volt[1] > 0 or volt[1] < v_max_ch2:
            print("shits fucked on v2")

    print(v_steps)
    print(len(v_steps))

if type == "Comp.":
    for i in range(0, voltage_steps - 1):
        i_voltage = round(voltage_increment * (i), 1)
        if i_voltage <= v_max_ch2:
            v_steps.append([0, i_voltage])
        if i_voltage > v_max_ch2:
            if j == 0:
                remainder = round(abs(i_voltage - v_max_ch2), 1)
                v_steps.append([-remainder, v_max_ch2])
                j = j + 1
            if j != 0:
                j = j + 1
                j_voltage = -(remainder + voltage_increment * j)
                v_steps.append([round(j_voltage), v_max_ch2])

    for volt in v_steps:
        if volt[0] < v_max_ch1 or volt[0] > 0:
            print("shits fucked on v1")
        if volt[1] < 0 or volt[1] > v_max_ch2:
            print("shits fucked on v2")

    print(v_steps)
    print(len(v_steps))

print(v_steps[0][0])