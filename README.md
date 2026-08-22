# python_prep

Practice repository for interview preparation and self-study in Python. Three independent tracks: algorithm problems, PyTorch fundamentals, and asyncio concurrency.

Everything here is worked by hand — the point is the reps, not a library.

```
.
├── LC/            algorithms & data structures (LeetCode)
├── ML/            PyTorch fundamentals
└── Concurrency/   asyncio, following Fowler's book
```

---

## LC — algorithms

Solved LeetCode problems, one file per problem, each runnable on its own with test cases in a `__main__` block.

| Problem | File | Pattern |
|---|---|---|
| 49 · Group Anagrams | `LC/LC49_groupAnagram.py` | hashing, canonical key |
| 238 · Product of Array Except Self | `LC/LC238_productarrays.py` | prefix/suffix aggregation |
| 347 · Top K Frequent Elements | `LC/LC357_topK.py` | counting + sort, size-`k` min-heap |
| 560 · Subarray Sum Equals K | `LC/LC560_SubarraySumEqualsK.py` | prefix sums + hashmap |

Where a problem has more than one worthwhile approach, both are kept as separate methods on the same `Solution` class — a naive or O(n log n) version alongside the optimal one — so the trade-off stays visible.

```bash
python LC/LC560_SubarraySumEqualsK.py
```

## ML — PyTorch

Tensor mechanics and model-building fundamentals.

- `ML/PYTORCH.md` — reference notes: broadcasting, `view`/`reshape`/`permute`, `einsum`, autograd and the training loop, layers written from scratch, data pipelines and masking, a catalogue of common training-loop bugs by symptom.
- `ML/basics.py` — scratch file for tensor experiments.

## Concurrency — asyncio

Worked exercises from **[*Python Concurrency with asyncio*](https://www.manning.com/books/python-concurrency-with-asyncio)** by Matthew Fowler (Manning).

`Concurrency/ch2/` — coroutines and tasks: `async def` and what a coroutine object actually is, `asyncio.run` and the event loop, `await` and sequential execution, `asyncio.create_task` for concurrency, and running other work while awaiting.

Files build on each other — `ex6.py` defines the shared `delay` helper that later exercises import.

**Run these from inside the chapter directory**, since the imports are flat:

```bash
cd Concurrency/ch2
python ex9.py
```

---

## Setup

Python 3.12 recommended (PyTorch wheels are not always available for the newest release).

```bash
python3.12 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install torch numpy pytest
```

Only the `ML/` track needs third-party packages. `LC/` and `Concurrency/` run on the standard library alone.
