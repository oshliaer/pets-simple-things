import random
import json
import matplotlib.pyplot as plt


class Source:
    def __init__(self, name, data):
        self.name = name
        self.data = data
        self.data_map = []

    def split_data(self, value, n=3):
        shares = [random.randint(0, 1000) for _ in range(n - 1)]
        shares.append(value - sum(shares))
        return shares

    def process_and_send(self, nodes, n=3):
        print(f"\n📡 {self.name} отправляет данные:")
        for record in self.data:
            shares = self.split_data(record, n)
            for i, node in enumerate(nodes):
                node.receive_share(self.name, record, shares[i])
                print(f"  - Запись {record} → {node.name}: доля {shares[i]}")

            self.data_map.append(
                {
                    "record": record,
                    "method": f"additive secret sharing, n={n}",
                    "shares_sent": {node.name: shares[i] for i, node in enumerate(nodes)},
                }
            )

    def export_data_map(self, filename):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.data_map, f, indent=4, ensure_ascii=False)


class Node:
    def __init__(self, name):
        self.name = name
        self.received = []  # (source, record_id, share)

    def receive_share(self, source_name, record_value, share):
        self.received.append((source_name, record_value, share))


# --- Реконструкция ---
def reconstruct(nodes, source_name, record_value):
    shares = [share for node in nodes for s, r, share in node.received if s == source_name and r == record_value]
    return sum(shares)


# --- Визуализация ---
def visualize_flow(sources, nodes):
    fig, ax = plt.subplots(figsize=(8, 6))

    src_positions = {s.name: (0, i) for i, s in enumerate(sources)}
    node_positions = {n.name: (5, i) for i, n in enumerate(nodes)}

    # Источники
    for name, (x, y) in src_positions.items():
        ax.scatter(x, y, s=800, c="skyblue", edgecolor="black", zorder=2)
        ax.text(x, y, name, ha="center", va="center", fontsize=10, weight="bold")

    # Узлы
    for name, (x, y) in node_positions.items():
        ax.scatter(x, y, s=800, c="lightgreen", edgecolor="black", zorder=2)
        ax.text(x, y, name, ha="center", va="center", fontsize=10, weight="bold")

    # Стрелки
    for src in sources:
        for record in src.data_map:
            for node, share in record["shares_sent"].items():
                x1, y1 = src_positions[src.name]
                x2, y2 = node_positions[node]
                ax.annotate(
                    "",
                    xy=(x2 - 0.3, y2),
                    xytext=(x1 + 0.3, y1),
                    arrowprops=dict(arrowstyle="->", lw=1, color="gray"),
                    zorder=1,
                )

    ax.axis("off")
    plt.title("Передача долей от Источников к Узлам", fontsize=12, weight="bold")
    plt.show()


# --- Симуляция ---
if __name__ == "__main__":
    src1 = Source("Источник1", [25, 30, 45])
    src2 = Source("Источник2", [20, 50])

    nodes = [Node("Узел1"), Node("Узел2"), Node("Узел3")]

    src1.process_and_send(nodes)
    src2.process_and_send(nodes)

    src1.export_data_map("data_map_src1.json")
    src2.export_data_map("data_map_src2.json")

    visualize_flow([src1, src2], nodes)

    print("\n🔑 Реконструкция:")
    for record in src1.data:
        rec_val = reconstruct(nodes, "Источник1", record)
        print(f"  {record} восстановлено → {rec_val}")

    for record in src2.data:
        rec_val = reconstruct(nodes, "Источник2", record)
        print(f"  {record} восстановлено → {rec_val}")

    print("\n✅ Симуляция завершена. Карты данных сохранены в JSON.")
