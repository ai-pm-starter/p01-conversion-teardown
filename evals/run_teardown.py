"""Run the teardown prompt on screenshots via the Gemini API (stdlib only).

Usage: python3 evals/run_teardown.py E01 E11 E16
Reads GEMINI_API_KEY and GEMINI_MODEL from .env.
Writes evals/results/<id>.<model>.json and prints a one-line summary per screenshot.
"""
import base64, json, os, sys, time, urllib.error, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROMPT_FILE = os.path.join(ROOT, "prompts", "v1-teardown.md")


def load_env():
    env = {}
    with open(os.path.join(ROOT, ".env")) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def load_prompt():
    text = open(PROMPT_FILE).read()
    # The prompt itself is everything after the first '---' separator.
    return text.split("\n---\n", 1)[1].strip()


def teardown(key, model, prompt, image_path):
    with open(image_path, "rb") as f:
        img = base64.b64encode(f.read()).decode()
    body = {
        "contents": [{"parts": [
            {"text": prompt},
            {"inline_data": {"mime_type": "image/png", "data": img}},
        ]}],
        "generationConfig": {"responseMimeType": "application/json"},
    }
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        data=json.dumps(body).encode(),
        headers={"x-goog-api-key": key, "Content-Type": "application/json"},
    )
    start = time.time()
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.load(r)
    elapsed = time.time() - start
    text = data["candidates"][0]["content"]["parts"][0]["text"]
    return json.loads(text), elapsed


def main():
    env = load_env()
    key, model = env["GEMINI_API_KEY"], env["GEMINI_MODEL"]
    prompt = load_prompt()
    out_dir = os.path.join(ROOT, "evals", "results")
    os.makedirs(out_dir, exist_ok=True)
    for eid in sys.argv[1:]:
        path = os.path.join(ROOT, "evals", "screenshots", f"{eid}.png")
        try:
            result, secs = teardown(key, model, prompt, path)
        except urllib.error.HTTPError as e:
            print(f"{eid}: HTTP {e.code} {e.read().decode()[:200]}")
            continue
        except Exception as e:
            print(f"{eid}: FAILED {type(e).__name__}: {str(e)[:200]}")
            continue
        result["_meta"] = {"model": model, "seconds": round(secs, 1), "prompt": "v1"}
        with open(os.path.join(out_dir, f"{eid}.{model}.json"), "w") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"{eid}: {secs:.1f}s | {result.get('page_type')} | score {result.get('overall_score')} | "
              f"{len(result.get('friction_points', []))} friction points | "
              f"{len(result.get('hypotheses', []))} hypotheses")


if __name__ == "__main__":
    main()
