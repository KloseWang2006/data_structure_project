import time
from Graph import generate_connected_weighted_graph, visualize_graph
from Task_Manager import TaskManager


def run_simulation_demo():
    # 1. 环境初始化
    width, height = 200, 200
    num_nodes = 40
    print(f"正在构建城市配送网络...")

    graph = generate_connected_weighted_graph(num_nodes, width, height)
    warehouse_id = graph.set_central_warehouse(width, height)
    print(f"中央仓库已设在节点: {warehouse_id}")

    # 2. 初始化任务管理器
    # 设定最高积压上限为 10 个任务
    task_manager = TaskManager(graph, max_tasks_limit=10)

    # 3. 模拟参数
    current_tick = 0
    total_ticks = 30  # 演示运行的时间步数

    print(f"\n开始模拟...")

    while current_tick < total_ticks:
        # 每个 tick 尝试生成任务
        new_tasks = task_manager.step_generate(current_tick)

        # 打印日志以便观察
        if new_tasks:
            for t in new_tasks:
                print(f"[{current_tick}s] ⚡ 新任务: 目的地 {t.target_id}, 重量 {t.weight:.1f}kg")

        # 统计当前状态
        pending = task_manager.get_pending_tasks()
        if current_tick % 5 == 0:  # 每 5 秒报一次盘
            print(f">>> 时间: {current_tick}s | 任务池积压: {len(pending)} 个")

        current_tick += 1
        time.sleep(0.1)  # 快速演示

    print("\n模拟演示结束。")
    print(f"总计生成任务: {task_manager.task_counter} 个")

    # 4. 最终地图呈现（展示任务点的分布）
    visualize_graph(graph)


if __name__ == "__main__":
    run_simulation_demo()