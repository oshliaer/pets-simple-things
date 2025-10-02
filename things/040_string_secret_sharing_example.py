import random


def split_string(s, n=3):
    shares = [[] for _ in range(n)]
    for ch in s.encode("utf-8"):  # байты строки
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


# --- пример ---
s = "Иванов Иван"
print("Оригинал:", s)

shares = split_string(s, n=3)
print("Доли:", shares)

restored = reconstruct_string(shares)
print("Восстановлено:", restored)
