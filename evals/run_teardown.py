"""Run the teardown prompt on screenshots via the Gemini API.

Usage: .venv/bin/python evals/run_teardown.py E01 E03 ...   (or: all)
       add --prompt v2 to pick prompts/<v>-teardown.md (default v1)
       add --max-tiles N to send only the top N screens
       add --skip-existing to keep results already written
On HTTP 429 (free-tier per-minute quota) it waits for the suggested delay and retries, up to 5 times.
Reads GEMINI_API_KEY and GEMINI_MODEL from .env.
Each screenshot is split into viewport-height tiles (app/tiling.py) and sent in one request.
Writes evals/results/<prompt>/<id>.<model>.json and prints a one-line summary per screenshot.
"""
import base64, csv, json, os, sys, time, urllib.error, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "app"))
from tiling import tiles  # noqa: E402

TILE_NOTE = ("The page is given as {n} screenshots: consecutive {device} screen-height slices "
             "of ONE page, in order from top to bottom. Treat them as a single page.")
DATE_NOTE = " The screenshots were captured on {date}."


def load_env():
    env = {}
    with open(os.path.join(ROOT, ".env")) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def load_prompt(version):
    text = open(os.path.join(ROOT, "prompts", f"{version}-teardown.md")).read()
    # The prompt itself is everything after the first '---' separator.
    return text.split("\n---\n", 1)[1].strip()


def retry_info(body):
    """Return (seconds to wait, quota id) from a 429 error body."""
    wait, quota = 60, "unknown quota"
    try:
        for d in json.loads(body)["error"].get("details", []):
            if d.get("@type", "").endswith("RetryInfo"):
                wait = int(float(d["retryDelay"].rstrip("s"))) + 2
            for v in d.get("violations", []):
                quota = v.get("quotaId", quota)
    except (ValueError, KeyError):
        pass
    return wait, quota


def teardown(key, model, prompt, image_path, max_tiles=None, captured_on=None):
    with open(image_path, "rb") as f:
        device, total, parts = tiles(f.read(), max_tiles)
    images = [{"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(p).decode()}}
              for p in parts]
    body = {
        "contents": [{"parts": [
            {"text": TILE_NOTE.format(n=len(parts), device=device)
                     + (DATE_NOTE.format(date=captured_on) if captured_on else "")},
            {"text": prompt},
            *images,
        ]}],
        "generationConfig": {"responseMimeType": "application/json"},
    }
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        data=json.dumps(body).encode(),
        headers={"x-goog-api-key": key, "Content-Type": "application/json"},
    )
    for attempt in range(6):
        start = time.time()
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                data = json.load(r)
            break
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempt == 5:
                raise
            wait, quota = retry_info(e.read().decode())
            if wait > 300:
                raise SystemExit(f"Quota {quota} exhausted; resets in about {wait // 3600}h. "
                                 "Re-run later with --skip-existing.")
            print(f"  429 on {os.path.basename(image_path)} ({quota}); waiting {wait}s", flush=True)
            time.sleep(wait)
    elapsed = time.time() - start
    text = data["candidates"][0]["content"]["parts"][0]["text"]
    usage = data.get("usageMetadata", {})
    tile_info = {"device": device, "tiles_sent": len(parts), "tiles_total": total,
                 "input_tokens": usage.get("promptTokenCount")}
    return json.loads(text), elapsed, tile_info


def main():
    env = load_env()
    key, model = env["GEMINI_API_KEY"], env["GEMINI_MODEL"]
    args = sys.argv[1:]
    version = "v1"
    if "--prompt" in args:
        i = args.index("--prompt")
        version = args[i + 1]
        del args[i:i + 2]
    prompt = load_prompt(version)
    out_dir = os.path.join(ROOT, "evals", "results", version)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(ROOT, "evals", "eval-set.csv")) as f:
        dates = {r["id"]: r["captured_on"] for r in csv.DictReader(f)}
    max_tiles = None
    skip_existing = "--skip-existing" in args
    if skip_existing:
        args.remove("--skip-existing")
    if "--max-tiles" in args:
        i = args.index("--max-tiles")
        max_tiles = int(args[i + 1])
        del args[i:i + 2]
    shots = os.path.join(ROOT, "evals", "screenshots")
    if args == ["all"]:
        args = sorted(f[:-4] for f in os.listdir(shots) if f.endswith(".png"))
    for eid in args:
        path = os.path.join(shots, f"{eid}.png")
        if skip_existing and os.path.exists(os.path.join(out_dir, f"{eid}.{model}.json")):
            print(f"{eid}: skipped (exists)", flush=True)
            continue
        try:
            result, secs, tile_info = teardown(key, model, prompt, path, max_tiles, dates.get(eid))
        except urllib.error.HTTPError as e:
            print(f"{eid}: HTTP {e.code} {e.read().decode()[:200]}")
            continue
        except Exception as e:
            print(f"{eid}: FAILED {type(e).__name__}: {str(e)[:200]}")
            continue
        result["_meta"] = {"model": model, "seconds": round(secs, 1), "prompt": version, **tile_info}
        with open(os.path.join(out_dir, f"{eid}.{model}.json"), "w") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"{eid}: {secs:.1f}s | {tile_info['tiles_sent']}/{tile_info['tiles_total']} tiles | "
              f"{tile_info['input_tokens']} tokens | {result.get('page_type')} | score {result.get('overall_score')} | "
              f"{len(result.get('friction_points', []))} friction points | "
              f"{len(result.get('hypotheses', []))} hypotheses", flush=True)


if __name__ == "__main__":
    main()
