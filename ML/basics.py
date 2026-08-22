import torch as nn

x = nn.arange(24).reshape(4,2,3) #batch, rows, col


if __name__ == "__main__":
    print(x)