reqs = ["requests==2.31.0", "torch", "pillow==10.2.0", "langchain==0.1.0", "pandas"]

p = 0
ms = 0
for line in reqs:
    i = 0
    index = 0
    for j in line:
        index += 1
        if j == "=":
            i = index
            break

    if i == 0 or i == len(line):
        continue
    n = line[:i]
    v = line[i+1:]
    p += 1
    ms += int(v[0])

print(f"Pinned: {p}")
print(f"Average: {(ms/p)}")
print(f"Acronym: {n[:4].upper()}")