# Classifier Spec — Pod Classifier

Complete this spec **before** writing any code for Milestone 2.

Use Plan or Ask mode to think through each blank field. When you're done,
your answers here become the blueprint for `build_few_shot_prompt()` and
`classify_episode()` in `classifier.py`.

---

## build_few_shot_prompt(labeled_examples, description)

### What it does
Constructs a prompt string for the LLM that includes the task instructions,
all labeled training examples, and the new episode description to classify.

### Inputs

| Parameter | Type | Description |
|---|---|---|
| `labeled_examples` | `list[dict]` | Each dict has `"title"`, `"description"`, `"label"` (and others). These are the examples you labeled in Milestone 1. |
| `description` | `str` | The episode description to classify. |

### Output

| Return value | Type | Description |
|---|---|---|
| prompt | `str` | A complete prompt string ready to send to the LLM. |

---

### Spec fields — fill these in before writing code

**Task instruction (what should the LLM know about the task?):**

```
You are classifying podcast episodes by their format. Classify the episode
into exactly one of these four labels:

- interview: a conversation between a host and one or more guests
- solo: a single host speaking from memory, experience, or opinion — no guests,
  no assembled external sources
- panel: multiple guests with roughly equal speaking time, often debating or
  discussing a topic together
- narrative: a story assembled from external sources — interviews, archival
  audio, reporting — with a clear narrative arc

Return only the label and your reasoning. Do not explain the taxonomy.
```

---

**How should labeled examples be formatted in the prompt?**

```
Each example should include the episode title, a brief excerpt or the full
description, and the correct label. Separate examples with a blank line or
a delimiter like "---". Include all fields that help the model see why the
label was applied — title and description are both useful; other fields
(like episode ID) are not needed.
```

---

**Example block sketch (write one concrete example):**

```
Title: {title}
Description: {description}
Label: {label}
```

---

**How should the new episode (to be classified) be presented?**

```
Present it in the same format as the labeled examples, but omit the Label
line and replace it with an instruction to classify. For example:

Title: {title}
Description: {description}
Label: ?

Then add a line like: "Classify the episode above. Return your answer in
the format below:" followed by the output format you chose.
```

---

**What output format should you request from the LLM?**

```
Request a simple structured text format:

Label: <one of interview, solo, panel, narrative>
Reasoning: <one or two sentences explaining the structural format>

This is easier to parse than a freeform paragraph because the parser can look
for a line beginning with "Label:". It is also less fragile than JSON because
LLMs sometimes return invalid JSON or wrap JSON in markdown. A label-only
response would be easiest to parse, but including reasoning helps with debugging
and error analysis.
```

---

**Edge cases to handle in the prompt:**

```
If labeled_examples is empty, the prompt should still explain the four valid
labels and ask the model to classify using the taxonomy, but performance will
likely be weaker because there are no demonstrations.

If the description is very short, the prompt should still ask for the best
structural label based only on the available evidence.

The prompt should repeatedly emphasize that the model must choose exactly one
of the four valid labels and should classify by episode structure, not topic,
tone, or how story-like the description sounds.
```

---

## classify_episode(description, labeled_examples)

### What it does
Classifies a single podcast episode description using the few-shot LLM classifier.
Returns a dict with a label and reasoning.

### Inputs

| Parameter | Type | Description |
|---|---|---|
| `description` | `str` | The episode description to classify. |
| `labeled_examples` | `list[dict]` | Labeled training examples from `load_labeled_examples()`. |

### Output

| Return value | Type | Description |
|---|---|---|
| result | `dict` | Must have keys `"label"` and `"reasoning"`. `"label"` must be one of `VALID_LABELS` or `"unknown"`. |

---

### Spec fields — fill these in before writing code

**Step 1 — Build the prompt:**

```
Call build_few_shot_prompt(labeled_examples, description) and store the
returned string in a variable (e.g., prompt). Pass through both arguments
exactly as received — no modification needed before calling.
```

---

**Step 2 — Send to the LLM:**

```
Call _client.chat.completions.create() with:
  - model: the model name from config (LLM_MODEL)
  - messages: a list with one dict — {"role": "user", "content": prompt}
    (system-design.md shows an optional system message too — either shape works)
  - max_tokens: a reasonable limit (e.g., 200–300) to keep responses concise

Extract the response text from:
  response.choices[0].message.content
```

---

**Step 3 — Parse the response:**

```
Extract the raw text from response.choices[0].message.content.

Split the response into lines. Look for a line that starts with "Label:" after
stripping whitespace and normalizing case. Take the text after the colon,
strip whitespace, remove common markdown/punctuation characters, and lowercase
it.

For reasoning, look for a line that starts with "Reasoning:" and take the text
after the colon. If no reasoning line is found, use the full raw response as
the reasoning so debugging is still possible.
```

---

**Step 4 — Validate the label:**

```
Check whether the parsed label is in VALID_LABELS. If it is, return that label.
If it is not in VALID_LABELS, set the label to "unknown" rather than trusting
the model output.

This protects the app from hallucinated labels like "documentary", "story",
"conversation", or labels with formatting problems.
```

---

**Step 5 — Handle errors gracefully:**

```
Wrap the LLM call and parsing logic in a try/except block.

Things that could go wrong include a missing or invalid Groq API key, network
errors, rate limits, an empty response, or a response that does not match the
requested format.

If something fails, return:
{"label": "unknown", "reasoning": f"Error: {e}"}

This prevents one bad API response from crashing the 20-call evaluation loop.
```

---

### Return value structure

```python
{
    "label": str,      # one of VALID_LABELS, or "unknown" if invalid/error
    "reasoning": str,  # brief explanation from the LLM
}
```

---

## Notes on label quality

The classifier is only as good as your labels. If your training examples have
inconsistent or ambiguous labels, the LLM will learn the wrong pattern.

Before implementing the classifier, re-read `data/taxonomy.md` and double-check
any labels you're unsure about. Annotation quality is part of the lab.

---

## Implementation Notes

*Fill this in after implementing and testing both functions.*

**Test: what does the raw LLM response look like for one episode?**

```
Episode tested: The Aral Sea: A Disaster in Four Acts
Raw response text: Label: narrative
Reasoning: The episode tells a story assembled from external information, including historical decisions, industry collapses, community adaptations, and scientific discoveries, with a clear narrative arc that explores the consequences of an ecosystem and economy collapsing. This structure, which weaves together various elements to create a cohesive story, is characteristic of a narrative format.
```

**How did you parse the label out of the response?**

```
The parser splits the response into lines, looks for a line that starts with "Label:", takes the text after the colon, strips whitespace and punctuation, lowercases it, and validates it against VALID_LABELS.
```

**Did any episodes return `"unknown"`? If so, why?**

```
No. The tested examples returned labels in the expected "Label: ..." format.
```

**One thing about the output format that surprised you:**

```
The model followed the requested structure consistently, but the raw response still needs normalization because future responses could include capitalization, punctuation, or markdown.
```
