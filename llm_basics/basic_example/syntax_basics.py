# DEFINITION: collect
def f(a, *args, **kwargs):
    print(a, args, kwargs)


if __name__ == "__main__":
    f(1, 2, 3, x=4, y=5, z=6)
    f(1, 2, 3, 4, 5, x=6, y=7)
    # CALL: spread
    nums = [2, 3]
    opts = {"x": 4, "y": 5}
    f(1, *nums, **opts)
