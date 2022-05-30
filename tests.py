def fun(X):
    if X/10 or X%10:
        return int(X%10) + fun(int(X/10))
    return 0

print(fun(int(input())))


