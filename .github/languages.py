import json
import subprocess
from collections import Counter
from html import escape
from pathlib import Path


def api(endpoint, *args):
    return json.loads(subprocess.check_output(["gh", "api", endpoint, *args]))


def render(totals):
    total = sum(totals.values())
    rows = []
    colors = ["#2f81f7", "#2da44e", "#8250df", "#bf8700", "#db61a2"]
    for index, (name, size) in enumerate(totals.most_common(5)):
        y = 73 + index * 30
        pct = 100 * size / total
        rows.append(
            f'<text x="20" y="{y}">{escape(name)}</text>'
            f'<rect x="138" y="{y - 10}" width="245" height="9" rx="4" fill="#30363d"/>'
            f'<rect x="138" y="{y - 10}" width="{245 * size / total:.1f}" height="9" rx="4" fill="{colors[index]}"/>'
            f'<text x="460" y="{y}" text-anchor="end">{pct:.1f}%</text>'
        )
    height = 62 + 30 * len(rows)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="480" height="{height}" viewBox="0 0 480 {height}">\n'
        '<title>Most used languages by code size</title>\n'
        f'<rect x=".5" y=".5" width="479" height="{height - 1}" rx="10" fill="#0d1117" stroke="#30363d"/>\n'
        '<g fill="#e6edf3" font-family="system-ui, sans-serif" font-size="13">\n'
        '<text x="20" y="27" font-size="16" font-weight="600">Most used languages</text>\n'
        '<text x="20" y="46" fill="#9da7b3">Code size across selected public repositories</text>\n'
        + "\n".join(rows)
        + "\n</g>\n</svg>\n"
    )


if __name__ == "__main__":
    totals = Counter()
    # The profile's generated assets and the Rust runner's vendored exercises skew the breakdown.
    excluded = {"terry-xyz", "01-rust-local-test"}
    pages = api("users/terry-xyz/repos?per_page=100", "--paginate", "--slurp")
    for page in pages:
        for repo in page:
            if not repo["fork"] and repo["name"] not in excluded:
                totals.update(api(f'repos/{repo["full_name"]}/languages'))
    if not totals:
        raise SystemExit("GitHub returned no language data")
    Path("github-languages.svg").write_text(render(totals), encoding="utf-8", newline="\n")
