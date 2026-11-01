"""Save a chat-app teardown from the clipboard as clean JSON.

Usage: python3 evals/save_result.py E11 chatgpt
Copy the model's whole reply first. Handles code fences and the markdown
escaping chat apps add when copying (trailing backslashes, &#x20;, \\").
"""
import html, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def clean(text):
    text = html.unescape(text)
    text = re.sub(r"\\\s*$", "", text, flags=re.M)        # markdown hard line breaks
    text = re.sub(r"\\([\\_*\[\]\-#`>!])", r"\1", text)   # markdown escapes
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, flags=re.S)
    if fence:
        text = fence.group(1)
    start, end = text.find("{"), text.rfind("}")
    return text[start:end + 1] if start != -1 else text


def main():
    if len(sys.argv) != 3:
        sys.exit("Usage: python3 evals/save_result.py <E01|E11|...> <chatgpt|claude>")
    eid, tool = sys.argv[1], sys.argv[2]
    raw = subprocess.run(["pbpaste"], capture_output=True, text=True).stdout
    try:
        data = json.loads(clean(raw))
    except json.JSONDecodeError as e:
        sys.exit(f"Not valid JSON ({e}). Did you copy the model's whole reply? Clipboard starts: {raw[:80]!r}")
    if "friction_points" not in data:
        sys.exit("JSON has no friction_points: this doesn't look like a teardown reply.")
    path = os.path.join(ROOT, "evals", "results", f"{eid}.{tool}.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"saved {eid}.{tool}.json | {data.get('page_type')} | score {data.get('overall_score')} | "
          f"{len(data['friction_points'])} issues | {len(data.get('hypotheses', []))} hypotheses")


if __name__ == "__main__":
    main()
