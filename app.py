from math import isfinite


def analyze(data):
    (start, ref_start), (end, ref_end) = data["anchors"]
    samples = data["samplesMs"]
    if not isinstance(samples, list) or len(samples) > 100000:
        raise ValueError("Use up to 100,000 sample timestamps")
    if not all(type(n) in (int, float) and isfinite(n) and abs(n) <= 1e15 for n in (start, ref_start, end, ref_end, *samples)):
        raise ValueError("Provide finite millisecond timestamps within 10^15 of zero")
    if end <= start or ref_end <= ref_start:
        raise ValueError("Both clocks must advance between the two anchors")
    scale = (ref_end - ref_start) / (end - start)
    return {"mappedMs": [round(ref_start + (n - start) * scale, 6) for n in samples],
            "ratePpm": round((scale - 1) * 1000000, 6), "offsetAtZeroMs": round(ref_start - start * scale, 6),
            "extrapolated": sum(n < start or n > end for n in samples)}

if __name__ == "__main__":
    import json
    from pathlib import Path
    import sys
    try:
        path, = sys.argv[1:]
        result = analyze(json.loads(Path(path).read_text(encoding="utf-8")))
        print(json.dumps(result, ensure_ascii=True, allow_nan=False))
    except (OSError, ValueError, TypeError, KeyError, AttributeError, OverflowError) as error:
        print(f"Invalid input: {error}", file=sys.stderr)
        sys.exit(2)
