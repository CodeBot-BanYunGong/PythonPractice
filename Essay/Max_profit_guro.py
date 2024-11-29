import gurobipy as gp
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
model = gp.Model("DoubleCreditPolicy")

# 定义决策变量
qf = model.addVars(2, vtype=gp.GRB.INTEGER, name="qf")
qn = model.addVars(2, vtype=gp.GRB.INTEGER, name="qn")
b = model.addVar(vtype=gp.GRB.CONTINUOUS, name="b")
s = model.addVar(vtype=gp.GRB.CONTINUOUS, name="s")

# 定义目标函数
model.setObjective(
    gp.quicksum((P[j] - C[j]) * qf[j] for j in range(2)) +
    gp.quicksum((P[j+2] - C[j+2]) * qn[j] for j in range(2)) -
    p * b + p * s,
    gp.GRB.MAXIMIZE
)


# 添加约束条件
# CAFC 积分约束
model.addConstr(
    gp.max_(0, - ( (gp.quicksum(FC[j] * qf[j] for j in range(2)) / gp.quicksum(qf[j] for j in range(2)) - k * TCAFC) * gp.quicksum(qf[j] for j in range(2)) ) ) <= b, "CAFC_Constraint"
)


# NEV 积分约束
model.addConstr(
    gp.quicksum(g[i] * qn[i] for i in range(2)) - beta * gp.quicksum(qf[j] for j in range(2)) == s - b, "NEV_Constraint"
)

# 产能约束
for j in range(2):
    model.addConstr(qf[j] <= Cap[j], f"Cap_Constraint_f{j+1}")
for i in range(2):
    model.addConstr(qn[i] <= Cap[i+2], f"Cap_Constraint_n{i+1}")


# 需求约束
for j in range(2):
    model.addConstr(qf[j] >= Dem_min[j], f"Demand_Min_Constraint_f{j+1}")
    model.addConstr(qf[j] <= Dem_max[j], f"Demand_Max_Constraint_f{j+1}")
for i in range(2):
    model.addConstr(qn[i] >= Dem_min[i+2], f"Demand_Min_Constraint_n{i+1}")
    model.addConstr(qn[i] <= Dem_max[i+2], f"Demand_Max_Constraint_n{i+1}")



# 求解模型
model.optimize()

# 输出结果
if model.status == gp.GRB.OPTIMAL:
    print("Optimal solution found:")
    for v in model.getVars():
        print(f"{v.varName}: {v.x}")
    print(f"Objective value: {model.objVal}")

    #  图表 1：最优产量
    products = ['Fuel Car 1', 'Fuel Car 2', 'NEV Car 1', 'NEV Car 2']
    quantities = [qf[0].x, qf[1].x, qn[0].x, qn[1].x]
    plt.figure(figsize=(8, 6))
    plt.bar(products, quantities)
    plt.xlabel("Product")
    plt.ylabel("Quantity")
    plt.title("Optimal Production Quantities")
    plt.show()


    # 图表 2: 积分交易情况 (示例 - 需要根据实际结果调整)
    labels = 'Sold NEV Credits', 'Bought NEV Credits'
    sizes = [s.x, b.x]
    plt.figure(figsize=(6, 6))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    plt.title("NEV Credit Trading")
    plt.show()


else:
    print("Optimization failed.")



#  灵敏度分析 (示例 -  积分价格 p)
p_values = np.linspace(1000, 5000, 10)  #  积分价格变化范围
profit_values = []

for p_val in p_values:
    model.setObjective(
        gp.quicksum((P[j] - C[j]) * qf[j] for j in range(2)) +
        gp.quicksum((P[j+2] - C[j+2]) * qn[j] for j in range(2)) -
        p_val * b + p_val * s,
        gp.GRB.MAXIMIZE
    )
    model.optimize()
    if model.status == gp.GRB.OPTIMAL:
       profit_values.append(model.objVal)
    else:
        profit_values.append(None)  #  处理优化失败的情况


plt.figure(figsize=(8,6))
plt.plot(p_values, profit_values)
plt.xlabel("Credit Price (p)")
plt.ylabel("Profit")
plt.title("Sensitivity Analysis: Credit Price vs. Profit")
plt.grid(True)
plt.show()


# 其他灵敏度分析 (类似地分析 β, g, Dem 等参数)
# ...

