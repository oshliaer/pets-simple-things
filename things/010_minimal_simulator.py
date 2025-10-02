import random
import json


class Source:
    def __init__(self, name, data):
        self.name = name
        self.data = data  # список персональных данных
        self.data_map = []

    def split_data(self, value, n=3):
        """Разделить число на n случайных долей (аддитивное secret sharing)."""
        shares = [random.randint(0, 1000) for _ in range(n - 1)]
        last_share = value - sum(shares)
        shares.append(last_share)
        return shares

    def process_and_send(self, nodes, n=3):
        for record in self.data:
            shares = self.split_data(record, n)
            for i, node in enumerate(nodes):
                node.receive_share(self.name, shares[i])

            # фиксируем карту данных
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
        self.received = []

    def receive_share(self, source_name, share):
        self.received.append((source_name, share))


# --- Симуляция ---
if __name__ == "__main__":
    # Источники с "персональными данными"
    src1 = Source("Источник1", [25, 30, 45])
    src2 = Source("Источник2", [20, 50])

    # Узлы для вычислений
    nodes = [Node("Узел1"), Node("Узел2"), Node("Узел3")]

    # Разделяем и отправляем данные
    src1.process_and_send(nodes)
    src2.process_and_send(nodes)

    # Экспорт карты данных
    src1.export_data_map("data_map_src1.json")
    src2.export_data_map("data_map_src2.json")

    print("✅ Симуляция завершена. Карта данных сохранена в JSON.")
