import random
import json


# ---------- Утилиты для строк ----------
def split_string(s, n=3):
    shares = [[] for _ in range(n)]
    for ch in s.encode("utf-8"):
        parts = [random.randint(0, 255) for _ in range(n - 1)]
        last = (ch - sum(parts)) % 256
        for i in range(n - 1):
            shares[i].append(parts[i])
        shares[-1].append(last)
    return shares


def reconstruct_string(shares):
    bytes_reconstructed = []
    for i in range(len(shares[0])):
        val = sum(share[i] for share in shares) % 256
        bytes_reconstructed.append(val)
    return bytes(bytes_reconstructed).decode("utf-8", errors="ignore")


# ---------- Классы ----------
class Node:
    def __init__(self, name):
        self.name = name
        self.received = []  # список (источник, поле, id, доля)

    def receive_share(self, source, record_id, field, share):
        self.received.append((source, record_id, field, share))


class Source:
    def __init__(self, name, data):
        self.name = name
        self.data = data  # список словарей
        self.data_map = []

    def process_and_send(self, nodes):
        print(f"\n📡 {self.name} отправляет данные:")
        for record in self.data:
            local_id = record["id"]
            entry_map = {"local_id": local_id, "fields": {}}

            for field, value in record.items():
                if field == "id":
                    continue
                shares = split_string(str(value), n=len(nodes))
                entry_map["fields"][field] = {nodes[i].name: shares[i] for i in range(len(nodes))}

                for i, node in enumerate(nodes):
                    node.receive_share(self.name, local_id, field, shares[i])
                    print(f"  - {field} ({value}) → {node.name}: {shares[i]}")

            self.data_map.append(entry_map)

    def export_data_map(self, filename):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.data_map, f, indent=4, ensure_ascii=False)


# ---------- Карта данных ----------
class DataMap:
    def __init__(self):
        self.entries = []  # связывает локальные ID разных источников

    def add_entry(self, global_id, ids):
        # ids = {"Источник1": "id1", "Источник2": "id2", ...}
        self.entries.append({"global_id": global_id, "local_ids": ids})

    def export(self, filename):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.entries, f, indent=4, ensure_ascii=False)


# ---------- Симуляция ----------
if __name__ == "__main__":
    # Тестовые данные
    src1 = Source(
        "Источник1",
        [
            {
                "id": "L1-001",
                "ФИО": "Иванов Иван",
                "ДатаРождения": "1980-01-01",
                "СНИЛС": "123-456-789 00",
                "X": "Данные X1",
            },
        ],
    )
    src2 = Source(
        "Источник2",
        [
            {
                "id": "L2-777",
                "ФИО": "Иванов Иван",
                "ДатаРождения": "1980-01-01",
                "Паспорт": "4500 123456",
                "Y": "Данные Y1",
            },
        ],
    )
    src3 = Source(
        "Источник3",
        [
            {
                "id": "L3-999",
                "ФИО": "Иванов Иван",
                "ДатаРождения": "1980-01-01",
                "Паспорт": "4500 123456",
                "СНИЛС": "123-456-789 00",
                "Z": "Данные Z1",
            },
        ],
    )

    nodes = [Node("Узел1"), Node("Узел2"), Node("Узел3")]

    src1.process_and_send(nodes)
    src2.process_and_send(nodes)
    src3.process_and_send(nodes)

    # Карта данных
    card = DataMap()
    card.add_entry("GLOB-001", {"Источник1": "L1-001", "Источник2": "L2-777", "Источник3": "L3-999"})

    # Экспортируем
    src1.export_data_map("data_map_src1.json")
    src2.export_data_map("data_map_src2.json")
    src3.export_data_map("data_map_src3.json")
    card.export("card.json")

    # Реконструкция (пример)
    print("\n🔑 Реконструкция:")
    # восстановим ФИО из трёх узлов (источник1, запись L1-001, поле ФИО)
    fio_shares = [
        share
        for node in nodes
        for (s, rid, field, share) in node.received
        if s == "Источник1" and rid == "L1-001" and field == "ФИО"
    ]
    fio = reconstruct_string(fio_shares)
    print(f"ФИО восстановлено: {fio}")
