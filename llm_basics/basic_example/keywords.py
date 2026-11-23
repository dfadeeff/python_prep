# Drill 1
def greet(name, greeting="Hello"):
    return f'{greeting}, {name}'


def show(a, **rest):
    print(a, rest)

def build(base,**extra):
    params = {"base":base}
    params.update(extra)
    return params

if __name__ == "__main__":
    d = {"name": "Dmitry", "greeting": "Hi"}
    print(greet(**d))
    print(show(1, x=2, y=3))
    print(build("model-x", temperature=0.5, top_k=3))
