# Evaluation Spec — Pod Classifier

Complete this spec **before** writing any code for Milestone 3.

Use Plan or Ask mode to think through each blank field. When you're done,
your answers here become the blueprint for `compute_accuracy()` and
`compute_per_class_accuracy()` in `evaluate.py`.

---

## Background: What is evaluation?

After building a classifier, we need to know how well it works. Evaluation answers:
- **Overall:** What fraction of episodes did we classify correctly?
- **Per-class:** Are we better at some labels than others?

Both functions take the same inputs: a list of predicted labels and a list of
ground-truth labels, in the same order.

---

## compute_accuracy(predictions, ground_truth)

### What it does
Returns the fraction of predictions that exactly match the ground truth.

### Inputs

| Parameter | Type | Description |
|---|---|---|
| `predictions` | `list[str]` | Labels predicted by `classify_episode()`, one per episode. |
| `ground_truth` | `list[str]` | The correct labels, in the same order as `predictions`. |

### Output

| Return value | Type | Description |
|---|---|---|
| accuracy | `float` | A value between 0.0 and 1.0. |

---

### Spec fields — fill these in before writing code

**Formula:**

```
Accuracy is the number of predictions that exactly match the ground-truth label divided by the total number of predictions.
```

---

**Step-by-step logic:**

```
1. If the predictions list is empty, return 0.0.
2. Pair each prediction with the ground-truth label at the same index.
3. Count how many pairs match exactly.
4. Divide the number of correct matches by the total number of predictions.
5. Return that value as a float.
```

---

**Edge case — what if both lists are empty?**

```
Return 0.0 because there are no predictions to evaluate, and dividing by zero would crash the function.
```

---

**Worked example:**

```
predictions  = ["interview", "solo", "panel", "interview"]
ground_truth = ["interview", "solo", "solo",  "narrative"]

Correct matches:
1. interview == interview → correct
2. solo == solo → correct
3. panel != solo → incorrect
4. interview != narrative → incorrect

2 correct out of 4 total.

compute_accuracy() returns 2 / 4 = 0.5
```

---

## compute_per_class_accuracy(predictions, ground_truth)

### What it does
Returns accuracy broken down by each label. For each label in `VALID_LABELS`,
reports how many episodes with that ground-truth label were classified correctly.

### Inputs

| Parameter | Type | Description |
|---|---|---|
| `predictions` | `list[str]` | Labels predicted by `classify_episode()`. |
| `ground_truth` | `list[str]` | Correct labels, in the same order. |

### Output

A `dict` keyed by label. Each value is a dict with three keys:

```python
{
    "interview": {"correct": int, "total": int, "accuracy": float},
    "solo":      {"correct": int, "total": int, "accuracy": float},
    "panel":     {"correct": int, "total": int, "accuracy": float},
    "narrative": {"correct": int, "total": int, "accuracy": float},
}
```

---

### Spec fields — fill these in before writing code

**What does "correct" mean for a given class?**

```
For a given class, an episode is correct if its ground-truth label is that class and the predicted label exactly matches that same class.

For example, an interview episode counts as correct for the interview class only when ground_truth is "interview" and prediction is also "interview".
```

---

**What does "total" mean for a given class?**

```
Total means the number of test episodes whose ground-truth label is that class. It is not the number of predictions for that class.
```

---

**Step-by-step logic:**

```
1. Initialize a result dictionary for every label in VALID_LABELS with correct = 0, total = 0, and accuracy = 0.0.
2. Loop over predictions and ground_truth together using zip().
3. For each pair, use the ground-truth label to decide which class bucket to update.
4. Increment total for that ground-truth class.
5. If prediction equals ground truth, increment correct for that class.
6. After the loop, calculate accuracy for each class as correct / total.
7. If a class has total == 0, leave accuracy as 0.0.
8. Return the result dictionary.
```

---

**Edge case — what if a class has no examples in ground_truth (total == 0)?**

```
If a class has total == 0, set accuracy to 0.0. This avoids division by zero and clearly indicates that there were no examples for that class in the evaluation set.
```

---

**Worked example:**

```
predictions  = ["interview", "interview", "solo", "panel", "panel"]
ground_truth = ["interview", "solo",      "solo", "panel", "narrative"]

label       correct  total  accuracy
----------  -------  -----  --------
interview   1        1      1.0
solo        1        2      0.5
panel       1        1      1.0
narrative   0        1      0.0
```

---

## Reflection questions (discuss at the checkpoint)

1. Your overall accuracy might be decent even if one class has very low accuracy.
   Why is per-class accuracy a more informative metric than overall accuracy alone?

2. If `panel` episodes consistently get misclassified as `interview`, what does
   that tell you about your training labels or your prompt?

3. You labeled 20 training episodes and evaluated on 20 test episodes (5 per class).
   How might the evaluation results change if you had labeled 100 training episodes?
   What if you had 200 test episodes?
