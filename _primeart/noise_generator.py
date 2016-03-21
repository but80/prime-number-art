def divide_pattern(n, begin=1):
    for i in range(begin, n):
        for p in divide_pattern(n-i, i):
            yield [i] + p
    if begin <= n: yield [n]

def diffuse_pattern(n, width):
    for divided in divide_pattern(n):
        if width < len(divided): continue
        divided_cnt = []
        for d in divided:
            i = len(divided_cnt)
            if i==0 or divided_cnt[i-1][0] != d:
                divided_cnt.append([d, 1])
            else:
                divided_cnt[i-1][1] += 1
        w = width
        pats = []
        for dc in divided_cnt:
            pats.append(layout_pattern(dc[0], dc[1], w))
            w -= dc[1]
        for p in combine_pattern(pats):
            yield p

def combine_pattern(pats):
    if len(pats) == 0:
        pass
    elif len(pats) == 1:
        for p in pats[0]: yield p
    else:
        pat = pats[0]
        pats_rest = pats[1:]
        for cp in combine_pattern(pats_rest):
            for p in pat:
                q = cp[:]
                r = p[:]
                for i in range(0, len(r)):
                    if r[i]==0: r[i] = q.pop()
                yield r

def layout_pattern(val, n, width):
    if width < n:
        pass
    elif width == 0:
        yield []
    else:
        if n == 0:
            yield [0] * width
        elif width == n:
            yield [val] * width
        else:
            for p in layout_pattern(val, n-1, width-1):
                yield [val] + p
            for p in layout_pattern(val, n, width-1):
                yield [0] + p

def signed_diffuse(diffuse):
    d = []
    for i in range(0, len(diffuse)):
        if diffuse[i] != 0:
            d.append(i)
    n = 1 << len(d)
    for i in range(0, n):
        mask = i
        r = diffuse[:]
        for j in range(0, len(d)):
            if (mask & 1) != 0:
                r[d[j]] *= -1
            mask >>= 1
        yield r

def generate_noise(width, limit_rate=5):
    for diff_total in range(1, width * limit_rate+1):
        for diffuse in diffuse_pattern(diff_total, width):
            for sd in signed_diffuse(diffuse):
                yield sd
