import pulp
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置字体为SimHei
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 车型数据（表5.1 F车企车型数据）
车型列表 = ["燃油车 A", "燃油车 B", "新能源车 A", "新能源车 B"]
售价 = {"燃油车 A": 120000, "燃油车 B": 320000, "新能源车 A": 280000, "新能源车 B": 200000}
成本 = {"燃油车 A": 96000, "燃油车 B": 256000, "新能源车 A": 260000, "新能源车 B": 185000}
产能上限 = {"燃油车 A": 100000, "燃油车 B": 100000, "新能源车 A": 100000, "新能源车 B": 100000}
油耗 = {"燃油车 A": 9, "燃油车 B": 11}
production_ratio_min = {"燃油车 A": 0.20, "燃油车 B": 0.20, "新能源车 A": 0.10, "新能源车 B": 0.20}
production_ratio_max = {"燃油车 A": 0.40, "燃油车 B": 0.30, "新能源车 A": 0.25, "新能源车 B": 0.25}

# 工厂最大产能
max_total_production = 300000

# 双积分政策参数（5.3.1章节内容）
k = 1.08  # CAFC合规因子
beta = 0.28  # NEV积分比例要求
p = 1525  # 积分价格 (元/积分)
目标油耗 = {"燃油车 A": 4.75, "燃油车 B": 5.85}
g = {"新能源车 A": 2.87, "新能源车 B": 2.19}  # NEV单车积分

# 创建模型（使用PuLP）
model = pulp.LpProblem("有双积分政策下的利润最大化", pulp.LpMaximize)

# 重新定义决策变量
x = pulp.LpVariable.dicts("产量", 车型列表, lowBound=0, cat='Integer')
b = pulp.LpVariable("购买积分", lowBound=0, cat='Integer')
s = pulp.LpVariable("出售积分", lowBound=0, cat='Integer')

# 计算燃油车总产量 和 CAFC 积分（公式4.2，公式4.3，公式4.4）
total_fuel_car_production = pulp.lpSum([x[i] for i in ["燃油车 A", "燃油车 B"]])
C_CAFC = k * pulp.lpSum([目标油耗[i] * x[i] for i in ["燃油车 A", "燃油车 B"]]) - pulp.lpSum([油耗[i] * x[i] for i in ["燃油车 A", "燃油车 B"]])

# 计算 NEV 积分（公式4.5）
C_NEV = pulp.lpSum([g[i] * x[i] for i in ["新能源车 A", "新能源车 B"]]) - beta*total_fuel_car_production

# 目标函数 (增加积分交易项) （公式4.1）
model += pulp.lpSum([(售价[i] - 成本[i]) * x[i] for i in 车型列表]) - p * b + p * s, "总利润"

# 定义约束条件 (增加双积分政策约束)
# 积分平衡约束（公式4.6）
model += (C_CAFC + C_NEV + b - s == 0), "积分平衡约束"

# 产能、产量占比和总产量约束（公式4.7，公式4.8，公式4.9，公式4.10）
total_production = pulp.lpSum(x)
model += total_production <= max_total_production, "工厂总产能约束"

for i in 车型列表:
    model += x[i] <= 产能上限[i], f"{i} 产能约束"
    model += x[i] >= production_ratio_min[i] * total_production, f"{i} 产量下限约束 (占比)"
    model += x[i] <= production_ratio_max[i] * total_production, f"{i} 产量上限约束 (占比)"

# 重新求解模型
model.solve(pulp.PULP_CBC_CMD(msg=False))

# 输出结果 (增加积分交易结果)
print("Status:", pulp.LpStatus[model.status])
产量_结果 = {}
for i in 车型列表:
    print(f"{i} 最优产量: {x[i].varValue}")
    产量_结果[i] = x[i].varValue

print("购买积分:", b.varValue)
print("出售积分:", s.varValue)
print("最优总利润:", pulp.value(model.objective))

# 创建图表
# 利润饼图
利润 = [(售价[i] - 成本[i]) * 产量_结果[i] for i in 车型列表]
plt.figure(figsize=(8, 6))
patches, texts, autotexts = plt.pie(利润, labels=车型列表, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 12})
plt.title("各车型利润占比", fontsize=14)
plt.tight_layout()
plt.savefig("利润饼图_含积分交易.png")
plt.show()

# 所有利润/损失数据，包含积分交易损失（用负值表示）
利润_燃油车_A = (售价["燃油车 A"] - 成本["燃油车 A"]) * 产量_结果["燃油车 A"]
利润_燃油车_B = (售价["燃油车 B"] - 成本["燃油车 B"]) * 产量_结果["燃油车 B"]
利润_新能源车_A = (售价["新能源车 A"] - 成本["新能源车 A"]) * 产量_结果["新能源车 A"]
利润_新能源车_B = (售价["新能源车 B"] - 成本["新能源车 B"]) * 产量_结果["新能源车 B"]
利润_积分交易_1 = (p * s.varValue - p * b.varValue)
所有利润 = [利润_燃油车_A, 利润_燃油车_B, 利润_新能源车_A, 利润_新能源车_B, 利润_积分交易_1]
所有标签 = ["燃油车 A", "燃油车 B", "新能源车 A", "新能源车 B", "积分交易"]
# 颜色列表，区分利润和损失
colors = ['skyblue'] * 4 + ['red']  # 前四个是车型利润 (蓝色)，最后一个是积分交易损失 (红色)
# 绘制柱状图
plt.figure(figsize=(8, 6))
plt.barh(所有标签, 所有利润, color=colors)
plt.ylabel("车型/积分交易", fontsize=12)
plt.xlabel("利润/损失 (元)", fontsize=12)
plt.title("各车型利润及积分交易损失", fontsize=14)
plt.xticks(rotation=0, ha="right")
plt.tight_layout()
plt.savefig("利润柱状图_含积分损失_颜色区分.png")
plt.show()

# 产量柱状图
colors = [patch.get_facecolor() for patch in patches]
plt.figure(figsize=(8, 6))
plt.bar(产量_结果.keys(), 产量_结果.values(), color=colors)
plt.xlabel("车型", fontsize=12)
plt.ylabel("产量 (辆)", fontsize=12)
plt.title("各车型产量", fontsize=14)
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("产量柱状图.png")
plt.show()

# ---  验证 CAFC 积分 ---
燃油车_产量 = {i: x[i].varValue for i in ["燃油车 A", "燃油车 B"]}
实际_油耗 = sum(油耗[i] * 燃油车_产量[i] for i in 燃油车_产量)
目标_油耗_加权 = sum(目标油耗[i] * 燃油车_产量[i] for i in 燃油车_产量)
C_CAFC = k * 目标_油耗_加权 - 实际_油耗

print(f"\n--- CAFC 积分验证 ---")
print(f"燃油车产量: {燃油车_产量}")
print(f"实际油耗总量: {实际_油耗}")
print(f"目标油耗加权总量: {目标_油耗_加权}")
print(f"CAFC 积分 (计算值): {C_CAFC}")
print(f"购买的 CAFC 积分 (b): {b.varValue}")  # 如果使用了 b 变量

# --- 验证 NEV 积分 ---
新能源车_产量 = {i: x[i].varValue for i in ["新能源车 A", "新能源车 B"]}
C_NEV = sum(g[i] * 新能源车_产量[i] for i in 新能源车_产量)
燃油车_总产量 = sum(燃油车_产量.values())
nev_积分_需求 = beta * 燃油车_总产量
nev_积分_盈余 = C_NEV - nev_积分_需求

print(f"\n--- NEV 积分验证 ---")
print(f"新能源车产量: {新能源车_产量}")
print(f"NEV 积分 (计算值): {C_NEV}")
print(f"NEV 积分需求: {nev_积分_需求}")
print(f"NEV 积分盈余/缺口: {nev_积分_盈余}")
print(f"出售的 NEV 积分 (s): {s.varValue}")  # 如果使用了 s 变量
print(f"购买的 NEV 积分 (b): {b.varValue}")  # 如果使用了 b 变量
