import pulp
import matplotlib.pyplot as plt
import numpy as np

# 模型参数 (根据上表设置)
P = [150000, 200000, 250000, 300000]
C = [120000, 160000, 200000, 240000]
FC = [6, 7]
g = [3, 5]
Cap = [10000, 8000, 6000, 4000]
Dem_min = [5000, 4000, 2000, 1000]
Dem_max = [8000, 7000, 5000, 3000]
TCAFC = 6.5
k = 1
beta = 0.15
p = 3000


# 创建模型
model = pulp.LpProblem("DoubleCreditPolicy", pulp.LpMaximize)

# 定义决策变量
qf = pulp.LpVariable.dicts("qf", range(2), lowBound=0, cat='Integer')
qn = pulp.LpVariable.dicts("qn", range(2), lowBound=0, cat='Integer')
b = pulp.LpVariable("b", lowBound=0)
s = pulp.LpVariable("s", lowBound=0)

# 定义目标函数
model += (
    pulp.lpSum((P[j] - C[j]) * qf[j] for j in range(2)) +
    pulp.lpSum((P[j+2] - C[j+2]) * qn[j] for j in range(2)) -
    p * b + p * s
)


# CAFC and NEV Constraints (Approximation for Non-Linear Terms)
# Note:  These constraints are approximations due to the non-linearity introduced by division.
#        For a more accurate solution, consider using a non-linear solver.

qf_total = pulp.lpSum(qf[j] for j in range(2))
model += qf_total >= 1  # Avoid division by zero

# Approximate CAFC constraint
CAFC_val = pulp.lpSum(FC[j] * qf[j] for j in range(2)) - k * TCAFC * qf_total
model += CAFC_val <= b * qf_total # Linearization by multiplying with qf_total
model += -CAFC_val <= b * qf_total # Linearization by multiplying with qf_total



# NEV 积分约束
model += (
    pulp.lpSum(g[i] * qn[i] for i in range(2)) - beta * pulp.lpSum(qf[j] for j in range(2)) == s - b
)




# 产能约束
for j in range(2):
    model += qf[j] <= Cap[j]
for i in range(2):
    model += qn[i] <= Cap[i+2]


# 需求约束
for j in range(2):
    model += qf[j] >= Dem_min[j]
    model += qf[j] <= Dem_max[j]
for i in range(2):
    model += qn[i] >= Dem_min[i+2]
    model += qn[i] <= Dem_max[i+2]



# 指定 CBC 求解器
solver = pulp.PULP_CBC_CMD()

# 求解模型
model.solve(solver)


# 输出结果
if model.status == pulp.LpStatusOptimal:
    print("Optimal solution found:")
    for v in model.variables():
        print(f"{v.name}: {v.varValue}")
    print(f"Objective value: {pulp.value(model.objective)}")

    # ... (绘图部分与之前代码相同，使用 v.varValue 获取变量值) ...


else:
    print(f"Optimization failed. Status: {model.status}, {pulp.LpStatus[model.status]}")



# ... (灵敏度分析部分与之前代码类似，使用 PuLP 语法)
