import json
import os
import urllib.request
import urllib.error
from datetime import datetime, timedelta

USERNAME = "shreyam91"
TOKEN = os.environ.get("GH_TOKEN")

if not TOKEN:
    raise RuntimeError("GH_TOKEN environment variable is missing")

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""

payload = json.dumps({
    "query": QUERY,
    "variables": {"login": USERNAME}
}).encode("utf-8")

request = urllib.request.Request(
    "https://api.github.com/graphql",
    data=payload,
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": USERNAME
    }
)

with urllib.request.urlopen(request) as response:
    data = json.loads(response.read().decode("utf-8"))

if "errors" in data:
    raise RuntimeError(data["errors"])

calendar = (
    data["data"]["user"]
    ["contributionsCollection"]
    ["contributionCalendar"]
)

weeks = calendar["weeks"]

days = []

for week in weeks:
    for day in week["contributionDays"]:
        days.append(day)

# --------------------------------------------------
# SVG SETTINGS
# --------------------------------------------------

CELL = 13
GAP = 4
COLS = len(weeks)
ROWS = 7

WIDTH = COLS * (CELL + GAP) + 80
HEIGHT = 260

GROUND_Y = 205

# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def esc(value):
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def plant_color(count):
    if count == 0:
        return None

    if count <= 2:
        return "#86efac"

    if count <= 5:
        return "#4ade80"

    if count <= 9:
        return "#22c55e"

    return "#15803d"


def plant_size(count):
    if count <= 2:
        return 22

    if count <= 5:
        return 32

    if count <= 9:
        return 45

    return 60


# --------------------------------------------------
# SVG
# --------------------------------------------------

svg = f'''<svg xmlns="http://www.w3.org/2000/svg"
width="{WIDTH}"
height="{HEIGHT}"
viewBox="0 0 {WIDTH} {HEIGHT}"
role="img"
aria-label="Shreyam Kanaujiya's GitHub Code Garden">

<defs>

    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#f8fbff"/>
        <stop offset="100%" stop-color="#ffffff"/>
    </linearGradient>

    <linearGradient id="ground" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0%" stop-color="#334155"/>
        <stop offset="50%" stop-color="#475569"/>
        <stop offset="100%" stop-color="#334155"/>
    </linearGradient>

    <filter id="soft">
        <feGaussianBlur stdDeviation="2"/>
    </filter>

    <style>
        .plant {{
            transform-box: fill-box;
            transform-origin: bottom center;
            animation: grow 1.8s ease-out both;
        }}

        .leaf {{
            transform-box: fill-box;
            transform-origin: center;
            animation: sway 3s ease-in-out infinite alternate;
        }}

        .flower {{
            transform-box: fill-box;
            transform-origin: center;
            animation: bloom 1.2s ease-out both;
        }}

        @keyframes grow {{
            from {{
                transform: scaleY(0);
                opacity: 0;
            }}
            to {{
                transform: scaleY(1);
                opacity: 1;
            }}
        }}

        @keyframes sway {{
            from {{
                transform: rotate(-3deg);
            }}
            to {{
                transform: rotate(3deg);
            }}
        }}

        @keyframes bloom {{
            from {{
                transform: scale(0);
                opacity: 0;
            }}
            to {{
                transform: scale(1);
                opacity: 1;
            }}
        }}
    </style>

</defs>

<!-- Background -->
<rect width="100%" height="100%" rx="18" fill="url(#sky)"/>

<!-- Title -->
<text
    x="40"
    y="38"
    font-family="Inter, Arial, sans-serif"
    font-size="18"
    font-weight="600"
    fill="#111827">
    🌱 Code Garden
</text>

<text
    x="40"
    y="61"
    font-family="Inter, Arial, sans-serif"
    font-size="11"
    fill="#64748b">
    Growing one contribution at a time.
</text>

<!-- Soft sun -->
<circle
    cx="{WIDTH - 55}"
    cy="48"
    r="18"
    fill="#fef3c7"
    opacity="0.8"/>

<circle
    cx="{WIDTH - 55}"
    cy="48"
    r="25"
    fill="#fef3c7"
    opacity="0.25"
    filter="url(#soft)"/>

<!-- Ground -->
<path
    d="M20 {GROUND_Y}
       Q {WIDTH//4} {GROUND_Y-8}
         {WIDTH//2} {GROUND_Y}
       T {WIDTH-20} {GROUND_Y}"
    fill="none"
    stroke="url(#ground)"
    stroke-width="5"
    stroke-linecap="round"/>

<path
    d="M20 {GROUND_Y+5}
       Q {WIDTH//4} {GROUND_Y-3}
         {WIDTH//2} {GROUND_Y+5}
       T {WIDTH-20} {GROUND_Y+5}"
    fill="none"
    stroke="#94a3b8"
    stroke-width="1"
    opacity="0.5"/>
'''

# --------------------------------------------------
# PLANTS
# --------------------------------------------------

for index, week in enumerate(weeks):

    x = 35 + index * (CELL + GAP)

    for day_index, day in enumerate(week["contributionDays"]):

        count = day["contributionCount"]

        if count == 0:
            continue

        color = plant_color(count)
        size = plant_size(count)

        # Map GitHub weekday position to garden height.
        # Higher contribution days become taller plants.
        y = GROUND_Y - (size / 2)

        # Slight natural variation.
        variation = ((index * 17 + day_index * 13) % 9) - 4
        y += variation

        delay = (index * 0.025) + (day_index * 0.08)

        # Stem
        svg += f'''
        <g class="plant" style="animation-delay:{delay:.2f}s">

            <line
                x1="{x}"
                y1="{GROUND_Y}"
                x2="{x}"
                y2="{y}"
                stroke="{color}"
                stroke-width="3"
                stroke-linecap="round"/>

            <ellipse
                class="leaf"
                cx="{x-5}"
                cy="{y+size*0.35}"
                rx="7"
                ry="4"
                fill="{color}"
                transform="rotate(-25 {x-5} {y+size*0.35})"/>

            <ellipse
                class="leaf"
                cx="{x+5}"
                cy="{y+size*0.55}"
                rx="7"
                ry="4"
                fill="{color}"
                transform="rotate(25 {x+5} {y+size*0.55})"/>
        '''

        # Flower for higher activity
        if count >= 6:

            flower_y = y - 4

            flower_colors = [
                "#60a5fa",
                "#a78bfa",
                "#f472b6",
                "#fbbf24"
            ]

            flower = flower_colors[(index + day_index) % len(flower_colors)]

            svg += f'''
            <g class="flower" style="animation-delay:{delay + 0.7:.2f}s">

                <circle cx="{x-5}" cy="{flower_y}" r="4" fill="{flower}"/>
                <circle cx="{x+5}" cy="{flower_y}" r="4" fill="{flower}"/>
                <circle cx="{x}" cy="{flower_y-5}" r="4" fill="{flower}"/>
                <circle cx="{x}" cy="{flower_y+5}" r="4" fill="{flower}"/>

                <circle
                    cx="{x}"
                    cy="{flower_y}"
                    r="3"
                    fill="#fbbf24"/>

            </g>
            '''

        svg += "</g>"

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

total = calendar["totalContributions"]

svg += f'''

<!-- Contribution total -->
<text
    x="40"
    y="{HEIGHT - 30}"
    font-family="Inter, Arial, sans-serif"
    font-size="11"
    fill="#64748b">
    {esc(total)} contributions
</text>

<text
    x="{WIDTH - 40}"
    y="{HEIGHT - 30}"
    text-anchor="end"
    font-family="Inter, Arial, sans-serif"
    font-size="11"
    fill="#94a3b8">
    github.com/{USERNAME}
</text>

</svg>
'''

os.makedirs("code-garden", exist_ok=True)

with open("code-garden/garden.svg", "w", encoding="utf-8") as file:
    file.write(svg)

print(f"🌱 Code Garden generated!")
print(f"🌿 Total contributions: {total}")