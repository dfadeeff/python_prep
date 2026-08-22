# PyTorch Track — Cheat Sheet, From-Scratch Drills, Bug Catalog

Read a section for 15 minutes, then close it and type the drill from a blank file. **Reading PyTorch feels like knowing PyTorch; it isn't.** The only thing that transfers to the interview is having typed it.

Convention used throughout: `B` batch, `T` time/sequence, `C`/`D` channels/features, `H` heads, `N`/`M` points, `K` classes.

---

## §1 Tensor mechanics — Day 1

This is where interviews are actually lost. Not the model — the shapes.

### Broadcasting, the only rule
Align shapes from the **trailing** dimension. Two dims are compatible if equal, or one of them is 1. Missing leading dims are treated as 1.

```
(B, T, C) + (C,)        -> (B, T, C)     ok
(B, T, C) + (T, 1)      -> (B, T, C)     ok
(B, N, 3) - (B, M, 3)   -> ERROR
(B, N, 1, 3) - (B, 1, M, 3) -> (B, N, M, 3)   # ← the pairwise-distance trick
```

That last line is the single most reusable idea in this section. **Unsqueezing to create a pairwise axis** is how you do distance matrices, attention scores, IoU matrices, chamfer distance, and NMS — all of it. Practice it until it's reflex.

### view / reshape / permute / contiguous
- `view` needs contiguous memory; it errors after a `permute`/`transpose`.
- `reshape` = `view` when it can, silently copies when it can't. Safe default.
- `permute`/`transpose` return **non-contiguous views** — same storage, reordered strides.
- Fix with `.contiguous()` before `.view()`. Idiom: `x.transpose(1, 2).contiguous().view(B, T, C)`.
- `x.T` is only for 2D. For batched, use `x.transpose(-2, -1)` or `x.mT`.

### cat vs stack
- `cat` joins along an **existing** dim: 2×`(B, T, C)` on `dim=1` → `(B, 2T, C)`.
- `stack` creates a **new** dim: 2×`(B, T, C)` on `dim=0` → `(2, B, T, C)`.
- Mixing these up is a top-3 interview bug. Say which one you want and why.

### Reductions and `keepdim`
`x.sum(dim=-1)` on `(B, T, C)` → `(B, T)`. With `keepdim=True` → `(B, T, 1)`, which then broadcasts back against `x`. **Any time you reduce and then divide/subtract, you want `keepdim=True`.**

```python
x_norm = (x - x.mean(-1, keepdim=True)) / (x.var(-1, keepdim=True, unbiased=False) + eps).sqrt()
```

### einsum — worth 20 minutes
```python
torch.einsum('btc,cd->btd', x, w)          # batched matmul over features
torch.einsum('bhtd,bhsd->bhts', q, k)      # attention scores, all heads at once
torch.einsum('bij,bjk->bik', A, B)         # batched matmul
torch.einsum('bnd,bmd->bnm', p, q)         # pairwise dot products
```
Repeated index = summed over. Index absent from output = summed out. Being fluent here reads as senior and sidesteps a lot of transpose gymnastics.

### Indexing you should know
- `gather(dim, index)` — pick per-row elements. Used constantly for "score of the correct class" and for RL/policy code.
- `masked_fill(mask, value)` — the attention-mask workhorse.
- Boolean masks flatten: `x[mask]` returns 1-D. Surprises people mid-interview.
- `torch.where(cond, a, b)` — the branchless conditional; use it instead of a Python `if` on tensors.

### §1 drill
1. `(B, T, C) @ (C, D) -> (B, T, D)` three ways: `@`, `einsum`, reshape-to-2D-and-back.
2. Pairwise Euclidean distance between `(B, N, 3)` and `(B, M, 3)` → `(B, N, M)`, no loops.
3. Per-position layer normalization over `C`, by hand.
4. Take `(B, T, C)` → `(B, H, T, C//H)` and back again. This is the reshape at the heart of multi-head attention; do it until it's automatic.

---

## §2 Autograd, nn.Module, the training loop — Day 2

### The loop, memorized
```python
model.train()
for xb, yb in train_loader:
    xb, yb = xb.to(device), yb.to(device)
    optimizer.zero_grad(set_to_none=True)   # grads ACCUMULATE; must clear
    logits = model(xb)
    loss = criterion(logits, yb)
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)   # optional, after backward
    optimizer.step()

model.eval()
with torch.no_grad():
    for xb, yb in val_loader:
        ...
```

Ordering that must be automatic: **zero_grad → forward → loss → backward → (clip) → step.** If you can't type this in 30 seconds you are not ready for Day 3.

### The distinctions they probe
- `no_grad()` — context manager, no graph is built at all. For inference/eval. Saves memory.
- `.detach()` — one tensor cut out of the graph, still shares storage.
- `.item()` — Python float out of a 1-element tensor. **Accumulating `total_loss += loss` instead of `loss.item()` keeps the whole graph alive → memory blows up.** Classic question.
- `model.train()` / `model.eval()` — changes Dropout (off in eval) and BatchNorm (running stats in eval). It does **not** disable gradients; that's `no_grad()`'s job. Interviewers love asking whether `eval()` is enough. It isn't.

### nn.Module facts
- `nn.Parameter` wrapping registers a tensor as learnable and puts it in `.parameters()` and `state_dict`.
- `register_buffer('running_mean', ...)` — state that moves with `.to(device)` and saves in `state_dict` but is **not** learned.
- Submodules in a plain Python list are **invisible** — no params, not moved to device. Use `nn.ModuleList` / `nn.Sequential` / `nn.ModuleDict`. This is a favorite trick question.
- Never call `model.forward(x)`; call `model(x)` so hooks run.

### §2 drill
Blank file → synthetic data with `torch.randn`, an MLP, a train/val split, 200 steps, loss printed and visibly decreasing, `eval()` + `no_grad()` on val. Under 12 minutes. Then delete the file and do it again tomorrow morning.

---

## §3 Layers from scratch — Day 3 (highest-probability material)

### Linear
```python
class Linear(nn.Module):
    def __init__(self, in_f, out_f, bias=True):
        super().__init__()
        self.weight = nn.Parameter(torch.randn(out_f, in_f) * (in_f ** -0.5))
        self.bias = nn.Parameter(torch.zeros(out_f)) if bias else None
    def forward(self, x):                 # (..., in_f)
        out = x @ self.weight.T           # (..., out_f)
        return out if self.bias is None else out + self.bias
```
Note `weight` is `(out, in)` — matching torch's own convention — hence the transpose. Mention that you know it's stored that way.

### LayerNorm vs BatchNorm — know the difference cold
- **LayerNorm** normalizes over the **feature** dims, per sample. No batch dependence, identical in train and eval, no running stats. Standard in transformers.
- **BatchNorm** normalizes over the **batch** dim per channel. Depends on other samples, keeps running stats, **behaves differently in train vs eval**. Breaks with batch size 1.
- "Why do transformers use LayerNorm?" → independence from batch statistics and from variable sequence length, and it behaves identically at train and inference time. Have that sentence ready.

### Scaled dot-product attention + MHA — drill this hardest
```python
class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, n_heads):
        super().__init__()
        assert d_model % n_heads == 0
        self.h, self.dk = n_heads, d_model // n_heads
        self.qkv = nn.Linear(d_model, 3 * d_model)
        self.proj = nn.Linear(d_model, d_model)

    def forward(self, x, mask=None):                     # x: (B, T, D)
        B, T, D = x.shape
        q, k, v = self.qkv(x).chunk(3, dim=-1)           # each (B, T, D)
        # (B, T, D) -> (B, T, H, dk) -> (B, H, T, dk)
        q, k, v = [t.view(B, T, self.h, self.dk).transpose(1, 2) for t in (q, k, v)]

        att = (q @ k.transpose(-2, -1)) / (self.dk ** 0.5)   # (B, H, T, T)
        if mask is not None:
            att = att.masked_fill(mask == 0, float('-inf'))  # BEFORE softmax
        att = att.softmax(dim=-1)                            # over KEYS = last dim

        out = att @ v                                        # (B, H, T, dk)
        out = out.transpose(1, 2).contiguous().view(B, T, D) # back to (B, T, D)
        return self.proj(out)
```
The four things to get right, and to *narrate* while writing:
1. Scale by `sqrt(dk)` — otherwise dot products grow with dimension and softmax saturates into near-one-hot, killing gradients.
2. Mask **before** softmax, with `-inf`, not after.
3. `softmax(dim=-1)` — over keys. `dim=-2` is a silent, plausible-looking wrong answer.
4. `.contiguous()` before `.view()` after the transpose.

Causal mask: `mask = torch.tril(torch.ones(T, T)).bool()`.

Verify it: change a *later* token's value and confirm earlier outputs don't move. That check itself is a strong signal to an interviewer.

### Conv arithmetic (say it, don't derive it)
`out = floor((in + 2*pad - dilation*(kernel-1) - 1) / stride) + 1`
"Same" padding at stride 1: `pad = (kernel - 1) // 2` for odd kernels.
Conv2d weight shape: `(out_channels, in_channels/groups, kH, kW)`.

### §3 drill
MHA from a blank file, causal mask, under 20 minutes, verified. Then LayerNorm from scratch and diff against `nn.LayerNorm`.

---

## §4 Data pipeline & numerical stability — Day 4

```python
class MyDataset(torch.utils.data.Dataset):
    def __init__(self, items): self.items = items
    def __len__(self):         return len(self.items)
    def __getitem__(self, i):  return self.items[i]     # returns ONE sample

def collate_fn(batch):                                   # list of samples -> batched tensors
    seqs = [b['x'] for b in batch]
    lens = torch.tensor([len(s) for s in seqs])
    padded = torch.nn.utils.rnn.pad_sequence(seqs, batch_first=True)   # (B, Tmax, ...)
    mask = torch.arange(padded.size(1))[None, :] < lens[:, None]       # (B, Tmax) True = real
    return padded, mask
```
That `arange[None, :] < lens[:, None]` line is the standard length→mask idiom. Memorize it.

**Masked mean-pool** — the place people silently get it wrong:
```python
summed = (x * mask.unsqueeze(-1)).sum(dim=1)     # (B, C)
pooled = summed / mask.sum(dim=1, keepdim=True).clamp(min=1)   # divide by REAL length
```
Dividing by `T` instead of the real length is a bug that trains fine and quietly degrades — worth naming out loud as the reason for the `clamp`.

### Losses — logits, not probabilities
- `nn.CrossEntropyLoss` takes **raw logits** `(B, K)` and **integer class indices** `(B,)`. It applies log-softmax internally. **Applying softmax yourself first is wrong**, and it's the single most common PyTorch interview bug.
- For sequences: reshape to `(B*T, K)` and `(B*T,)`, and use `ignore_index=PAD` for padded positions.
- `nn.BCEWithLogitsLoss` over `Sigmoid` + `BCELoss` — fuses log-sigmoid for numerical stability. Always prefer it.
- Numerically stable softmax subtracts the max: `x = x - x.max(dim, keepdim=True).values` before `exp`. Be ready to write stable softmax and stable log-sum-exp by hand.
- `reduction='mean'` vs `'sum'` matters when you mask — mean over a padded batch divides by the wrong count.

### DataLoader knobs to mention
`batch_size`, `shuffle=True` for train / `False` for val, `num_workers`, `pin_memory=True` with CUDA, `drop_last`, `collate_fn`.

---

## §5 Bug catalog — "this training loop is broken, fix it"

A very likely question at a robotics company that cares about people who can debug real systems. Learn these **by symptom**, so you can diagnose out loud instead of reading line by line.

| # | Bug | Symptom |
|---|---|---|
| 1 | Missing `optimizer.zero_grad()` | Loss jumps around / diverges; grads accumulate across steps |
| 2 | `zero_grad()` after `backward()` | Nothing learns at all — grads wiped before `step()` |
| 3 | Softmax applied before `CrossEntropyLoss` | Trains, but slowly and to a worse optimum |
| 4 | No `model.eval()` at validation | Val loss noisy and worse than train; dropout/BN still in train mode |
| 5 | No `torch.no_grad()` at validation | Memory grows, eval is slow; nothing else visibly wrong |
| 6 | `total_loss += loss` instead of `.item()` | Memory grows every step until OOM |
| 7 | Optimizer built before model moved to device, or over the wrong params | Nothing learns; params never update |
| 8 | Submodules in a plain list, not `nn.ModuleList` | Those layers never train, never move to GPU |
| 9 | `shuffle=True` on the validation loader | Metrics inconsistent run to run |
| 10 | LR far too high / too low | Loss → NaN, or a flat line |
| 11 | `scheduler.step()` in the wrong place (per batch vs per epoch) | LR decays ~N× too fast |
| 12 | Labels not aligned with inputs after a shuffle/sort | Loss plateaus at chance level |

**Say the symptom→cause mapping out loud when you find one.** "Loss is exactly flat and memory is stable — that points at the optimizer not seeing these parameters, so let me check how it was constructed" is worth far more than silently inserting the fix.

Also have ready: **"loss is NaN — what do you check?"** → LR too high; `log(0)` or division by zero; `exp` overflow from an unstable softmax; bad input data (NaNs in the batch); `sqrt` of a negative or of exactly zero in a norm (needs `+eps`); exploding grads → clip. Say `torch.autograd.set_detect_anomaly(True)` as the debugging tool.

---

## §6 Robotics-flavored tensor problems — Day 5

Intrinsic is robotics. These are pure broadcasting problems dressed in domain clothes, and they're the most likely shape for a "PyTorch problem that isn't a model."

**Batched pairwise / chamfer distance** — `(B, N, 3)` and `(B, M, 3)`:
```python
d2 = ((p.unsqueeze(2) - q.unsqueeze(1)) ** 2).sum(-1)   # (B, N, M)
chamfer = d2.min(dim=2).values.mean(-1) + d2.min(dim=1).values.mean(-1)
```
Better numerically for large N: `|p|² + |q|² - 2 p·qᵀ` via `einsum`, then `clamp(min=0)` before `sqrt` (float error can produce tiny negatives — mention this).

**Apply batched SE(3) transforms** — `T: (B, 4, 4)` to `points: (B, N, 3)`:
```python
R, t = T[:, :3, :3], T[:, :3, 3]              # (B,3,3), (B,3)
out = points @ R.transpose(-2, -1) + t.unsqueeze(1)     # (B, N, 3)
```
Know why it's `R.transpose(-2,-1)` on the right rather than `R @ points`: points are row vectors here. Be ready to say it.

**2D IoU, batched** — boxes `(N, 4)` and `(M, 4)` in xyxy → `(N, M)`:
```python
lt = torch.max(a[:, None, :2], b[None, :, :2])          # (N, M, 2)
rb = torch.min(a[:, None, 2:], b[None, :, 2:])
wh = (rb - lt).clamp(min=0)                             # clamp = no negative overlap
inter = wh[..., 0] * wh[..., 1]
area_a = (a[:, 2] - a[:, 0]) * (a[:, 3] - a[:, 1])
area_b = (b[:, 2] - b[:, 0]) * (b[:, 3] - b[:, 1])
iou = inter / (area_a[:, None] + area_b[None, :] - inter + 1e-7)
```
Then NMS on top of it: sort by score, greedily keep, drop anything with IoU > threshold against a kept box.

**Quaternion → rotation matrix**, batched, and normalize the quaternion first. Worth 15 minutes if you have them.

---

## §7 Concept questions they may slip in

Short answers, ready to deploy:

- **Why scale attention by √dk?** Dot products of `dk`-dim vectors have variance ∝ `dk`; without scaling, softmax saturates and gradients vanish.
- **LayerNorm vs BatchNorm?** Feature-axis per sample vs batch-axis per channel; LN has no batch dependence and behaves identically train/eval.
- **What does `optimizer.zero_grad()` do and why is it needed?** Gradients accumulate into `.grad` by design (useful for grad accumulation across micro-batches); without clearing, each step uses the sum of all prior batches.
- **Adam vs SGD?** Adam adapts per-parameter step sizes from first/second moment estimates — faster to converge, less LR tuning; SGD+momentum often generalizes better on vision. Mention AdamW decouples weight decay.
- **Dropout at inference?** Off. Activations are already scaled during training (inverted dropout), so nothing is rescaled at eval.
- **Gradient accumulation?** `backward()` on each micro-batch, `step()` every N — simulates a larger batch under a memory cap. Remember to divide the loss by N.
- **Mixed precision?** `torch.autocast` + `GradScaler`; fp16/bf16 forward for speed and memory, fp32 master weights, loss scaling to keep small fp16 grads from flushing to zero.
- **`view` vs `reshape`?** `view` requires compatible strides and never copies; `reshape` falls back to a copy.

---

## Interview-time habit

Annotate every intermediate tensor with its shape as you type:

```python
q = q.view(B, T, H, dk).transpose(1, 2)   # (B, H, T, dk)
att = q @ k.transpose(-2, -1)             # (B, H, T, T)
```

It feels slow. It is not slow — it is the single highest-leverage habit in a PyTorch interview. It prevents the bug class you're most likely to hit, it gives the interviewer a running trace of your reasoning, and when you do hit an error you can find it by reading your own comments instead of guessing.
