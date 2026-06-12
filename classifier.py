import json
import os
from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL, VALID_LABELS, DATA_PATH, TRAIN_FILE, LABELS_FILE

_client = Groq(api_key=GROQ_API_KEY)


def load_labeled_examples() -> list[dict]:
    """
    Load the training episodes and merge them with the student's labels.

    Returns a list of dicts, each with:
      - "id"          : episode ID
      - "title"       : episode title
      - "podcast"     : podcast name
      - "description" : episode description
      - "label"       : the label from my_labels.json (may be None if not yet annotated)

    Only returns episodes where the label is a valid, non-null string.
    Episodes with null labels are silently skipped.
    """
    train_path = os.path.join(DATA_PATH, TRAIN_FILE)
    labels_path = os.path.join(DATA_PATH, LABELS_FILE)

    with open(train_path, encoding="utf-8") as f:
        episodes = {ep["id"]: ep for ep in json.load(f)}

    with open(labels_path, encoding="utf-8") as f:
        labels = {entry["id"]: entry["label"] for entry in json.load(f)}

    labeled = []
    for ep_id, ep in episodes.items():
        label = labels.get(ep_id)
        if label in VALID_LABELS:
            labeled.append({**ep, "label": label})

    return labeled


def build_few_shot_prompt(labeled_examples: list[dict], description: str) -> str:
    """
    Build a few-shot classification prompt using the student's labeled training examples.
    """
    task_instruction = """
You are classifying podcast episodes by their structural format.

Classify the episode into exactly one of these four labels:

- interview: a conversation between a host and one or more guests
- solo: a single host speaking from memory, experience, or opinion; no guests and no assembled external sources
- panel: three or more speakers discussing a topic together as rough equals, without a clear host-guest dynamic
- narrative: a story assembled from external sources such as interviews, archival audio, documents, reporting, or recordings, with a clear narrative arc

Important:
- Classify by structure, not topic, tone, or how dramatic/story-like the description sounds.
- Return exactly one of the four labels.
- Use this exact output format:

Label: <interview | solo | panel | narrative>
Reasoning: <one or two sentences>
""".strip()

    if labeled_examples:
        examples_block = "\n\n---\n\n".join(
            f"Title: {example['title']}\n"
            f"Description: {example['description']}\n"
            f"Label: {example['label']}"
            for example in labeled_examples
        )
    else:
        examples_block = "No labeled examples were provided. Use the taxonomy above."

    new_episode_block = (
        "Title: Unknown\n"
        f"Description: {description}\n"
        "Label: ?"
    )

    return (
        f"{task_instruction}\n\n"
        f"Here are labeled examples:\n\n"
        f"{examples_block}\n\n"
        f"---\n\n"
        f"Now classify this new episode:\n\n"
        f"{new_episode_block}\n\n"
        f"Return your answer in this exact format:\n"
        f"Label: <interview | solo | panel | narrative>\n"
        f"Reasoning: <one or two sentences>"
    )


def classify_episode(description: str, labeled_examples: list[dict]) -> dict:
    """
    Classify a single podcast episode description using the few-shot LLM classifier.
    """
    try:
        prompt = build_few_shot_prompt(labeled_examples, description)

        response = _client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=250,
        )

        response_text = response.choices[0].message.content or ""

        # Temporary/debug-friendly: helps students inspect what the LLM actually returned.
        print("\n--- Raw LLM response ---")
        print(response_text)
        print("------------------------\n")

        label = "unknown"
        reasoning = response_text.strip()

        for line in response_text.splitlines():
            cleaned_line = line.strip()

            if cleaned_line.lower().startswith("label:"):
                candidate = cleaned_line.split(":", 1)[1]
                candidate = candidate.strip().lower()
                candidate = candidate.strip("`*_-.,:; ")

                if candidate in VALID_LABELS:
                    label = candidate
                break

        for line in response_text.splitlines():
            cleaned_line = line.strip()

            if cleaned_line.lower().startswith("reasoning:"):
                reasoning = cleaned_line.split(":", 1)[1].strip()
                break

        return {
            "label": label,
            "reasoning": reasoning,
        }

    except Exception as e:
        return {
            "label": "unknown",
            "reasoning": f"Error: {e}",
        }
