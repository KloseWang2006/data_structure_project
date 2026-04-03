import random
import math
import matplotlib.pyplot as plt
from collections import deque


# 计算两个节点之间的欧几里得距离
# 这个距离同时作为边的权值
def get_distance(node1, node2):
    return math.sqrt((node1.x - node2.x) ** 2 + (node1.y - node2.y) ** 2)


# 节点类：表示图中的一个点
class Node:
    def __init__(self, node_id, x, y, node_type="road"):
        self.id = node_id              # 节点编号
        self.x = x                     # 节点横坐标
        self.y = y                     # 节点纵坐标
        self.type = node_type          # 节点类型：road / warehouse / charging_station / task_point

    def __repr__(self):
        # 方便调试时打印节点信息
        return f"Node(id={self.id}, x={self.x:.2f}, y={self.y:.2f}, type={self.type})"


# 图类：表示整个无向带权图
class Graph:
    def __init__(self):
        self.nodes = {}   # 存储所有节点，格式：{节点id: Node对象}
        self.adj = {}     # 邻接表，格式：{节点id: {邻居id: 边权}}

    # 添加节点
    def add_node(self, node):
        self.nodes[node.id] = node
        self.adj[node.id] = {}

    # 添加无向边
    def add_edge(self, id1, id2, weight=None):
        # 禁止自环（自己连自己）
        if id1 == id2:
            return

        # 如果两个节点不存在，就报错
        if id1 not in self.nodes or id2 not in self.nodes:
            raise ValueError("节点不存在，无法连边")

        n1 = self.nodes[id1]
        n2 = self.nodes[id2]

        # 如果没有传入权值，就默认使用两点间欧几里得距离
        if weight is None:
            weight = get_distance(n1, n2)

        # 无向图：双向存储
        # 使用字典可以自动避免重复边
        self.adj[id1][id2] = weight
        self.adj[id2][id1] = weight

    # 判断两点之间是否已经有边
    def has_edge(self, id1, id2):
        return id2 in self.adj[id1]

    # 统计图中的边数
    def edge_count(self):
        count = sum(len(neighbors) for neighbors in self.adj.values())
        return count // 2  # 因为无向图每条边存了两次，所以要除以2

    # 判断图是否全联通
    def is_connected(self):
        # 如果图里没有节点，默认认为是联通的
        if not self.nodes:
            return True

        # 从任意一个节点开始做广度优先搜索 BFS
        start = next(iter(self.nodes))
        visited = set()
        queue = deque([start])

        while queue:
            u = queue.popleft()
            if u in visited:
                continue
            visited.add(u)

            for v in self.adj[u]:
                if v not in visited:
                    queue.append(v)

        # 如果访问到的节点数等于总节点数，说明全联通
        return len(visited) == len(self.nodes)

    # 打印图的基本信息
    def print_graph_info(self):
        print("图信息：")
        print(f"节点数: {len(self.nodes)}")
        print(f"边数: {self.edge_count()}")
        print(f"是否全联通: {self.is_connected()}")


# 生成指定数量的随机节点
def generate_nodes(num_nodes=30, width=100, height=100):
    graph = Graph()

    for i in range(num_nodes):
        # 在给定平面范围内随机生成坐标
        x = random.uniform(0, width)
        y = random.uniform(0, height)

        # 当前阶段先把所有节点都设为普通道路点
        node = Node(i, x, y, node_type="road")
        graph.add_node(node)

    return graph


# 第一阶段：先保证整张图全联通
def connect_graph_guaranteed(graph):
    """
    思想：
    先任选一个点加入已连接集合 connected
    然后不断从“已连接集合”和“未连接集合”之间
    找到距离最近的一对点进行连边
    直到所有节点都被连接进来

    这样可以保证整张图一定是全联通的
    """
    node_ids = list(graph.nodes.keys())
    if len(node_ids) <= 1:
        return

    connected = {node_ids[0]}         # 已连接节点集合
    unconnected = set(node_ids[1:])   # 未连接节点集合

    while unconnected:
        best_u = None
        best_v = None
        best_dist = float("inf")

        # 在“已连接集合”和“未连接集合”之间找最近的一对点
        for u in connected:
            for v in unconnected:
                dist = get_distance(graph.nodes[u], graph.nodes[v])
                if dist < best_dist:
                    best_dist = dist
                    best_u = u
                    best_v = v

        # 把最近的一对点连起来
        graph.add_edge(best_u, best_v, best_dist)

        # 新点加入已连接集合
        connected.add(best_v)
        unconnected.remove(best_v)


# 第二阶段：补充额外的近邻边，让图看起来更自然
def add_extra_nearest_edges(graph, extra_k=2):
    """
    对每个节点，找到若干个最近但尚未连接的节点，再补充连边
    这样图不会太稀疏，更像真实道路网络
    """
    for i in graph.nodes:
        distances = []

        for j in graph.nodes:
            # 不和自己连边
            if i == j:
                continue

            # 如果已经有边，就不重复添加
            if graph.has_edge(i, j):
                continue

            dist = get_distance(graph.nodes[i], graph.nodes[j])
            distances.append((j, dist))

        # 按距离从小到大排序
        distances.sort(key=lambda x: x[1])

        # 连接最近的 extra_k 个点
        for j, dist in distances[:extra_k]:
            graph.add_edge(i, j, dist)


# 生成一个“全联通 + 带权 + 无向”的随机图
def generate_connected_weighted_graph(num_nodes=30, width=100, height=100, extra_k=2):
    # 先生成随机节点
    graph = generate_nodes(num_nodes, width, height)

    # 第一步：保证图全联通
    connect_graph_guaranteed(graph)

    # 第二步：再额外补充一些边
    add_extra_nearest_edges(graph, extra_k=extra_k)

    return graph


# 可视化图
def visualize_graph(graph, show_weights=False):
    plt.figure(figsize=(10, 8))

    # 先画边，避免节点被边覆盖
    drawn_edges = set()

    for u in graph.adj:
        for v, w in graph.adj[u].items():
            # 无向图中一条边会存两次，所以画过一次就跳过
            if (v, u) in drawn_edges:
                continue

            x1, y1 = graph.nodes[u].x, graph.nodes[u].y
            x2, y2 = graph.nodes[v].x, graph.nodes[v].y

            # 画边
            plt.plot([x1, x2], [y1, y2], linewidth=1)

            # 如果需要显示边权，就在边中点写上权值
            if show_weights:
                mx = (x1 + x2) / 2
                my = (y1 + y2) / 2
                plt.text(mx, my, f"{w:.1f}", fontsize=8)

            drawn_edges.add((u, v))

    # 再画节点
    for node_id, node in graph.nodes.items():
        color = "skyblue"  # 默认普通道路节点颜色

        # 根据不同节点类型设置不同颜色
        if node.type == "warehouse":
            color = "red"
        elif node.type == "charging_station":
            color = "green"
        elif node.type == "task_point":
            color = "orange"

        plt.scatter(node.x, node.y, s=100, c=color, edgecolors="black", zorder=3)
        plt.text(node.x + 1, node.y + 1, str(node_id), fontsize=9)

    plt.title("Connected Weighted Undirected Graph")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.axis("equal")
    plt.show()


# 主程序入口
if __name__ == "__main__":
    # 这一句会固定随机数种子
    # 所以每次运行程序，生成的图都一样
    random.seed()

    graph = generate_connected_weighted_graph(
        num_nodes=20,   # 节点数量
        width=100,      # 地图宽度
        height=100,     # 地图高度
        extra_k=2       # 每个节点额外补充连接的近邻数
    )

    graph.print_graph_info()
    visualize_graph(graph, show_weights=False)