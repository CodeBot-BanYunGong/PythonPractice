import pulp
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 车型数据
车型列表 = ["燃油车 A", "燃油车 B", "新能源车 A", "新能源车 B"]
售价 = {"燃油车 A": 120000, "燃油车 B": 320000, "新能源车 A": 280000, "新能源车 B": 200000}
成本 = {"燃油车 A": 96000, "燃油车 B": 256000, "新能源车 A": 224000, "新能源车 B": 160000}
产能上限 = {"燃油车 A": 40000, "燃油车 B": 20000, "新能源车 A": 15000, "新能源车 B": 25000}
需求下限 = {"燃油车 A": 20000, "燃油车 B": 8000, "新能源车 A": 5000, "新能源车 B": 10000}
需求上限 = {"燃油车 A": 35000, "燃油车 B": 18000, "新能源车 A": 12000, "新能源车 B": 22000}

# 创建模型
model = pulp.LpProblem("无双积分政策下的利润最大化", pulp.LpMaximize)

# 定义决策变量
x = pulp.LpVariable.dicts("产量", 车型列表, lowBound=0, cat='Integer')

# 定义目标函数
model += pulp.lpSum([(售价[i] - 成本[i]) * x[i] for i in 车型列表]), "总利润"

# 定义约束条件
for i in 车型列表:
    model += x[i] <= 产能上限[i], f"{i} 产能约束"
    model += x[i] >= 需求下限[i], f"{i} 需求下限约束"
    model += x[i] <= 需求上限[i], f"{i} 需求上限约束"

# 求解模型
model.solve(pulp.PULP_CBC_CMD(msg=False))

# 输出结果
print("Status:", pulp.LpStatus[model.status])
产量_结果 = {}
for i in 车型列表:
    print(f"{i} 最优产量: {x[i].varValue}")
    产量_结果[i] = x[i].varValue
print("最优总利润:", pulp.value(model.objective))

# 创建图表
# 利润饼图
利润 = [(售价[i] - 成本[i]) * 产量_结果[i] for i in 车型列表]
plt.figure(figsize=(8, 6))
patches, texts, autotexts = plt.pie(利润, labels=车型列表, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 10})
plt.title("各车型利润占比", fontsize=14)
plt.tight_layout()
plt.savefig("利润饼图.png")
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
