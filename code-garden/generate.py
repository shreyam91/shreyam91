import json
import os
import urllib.request

USERNAME = "shreyam91"
TOKEN = os.environ["GH_TOKEN"]

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
            weekday
          }
        }
      }
    }
  }
}
"""

request = urllib.request.Request(
    "https://api.github.com/graphql",
    data=json.dumps({
        "query": QUERY,
        "variables": {"login": USERNAME}
    }).encode(),
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": USERNAME
    }
)

with urllib.request.urlopen(request) as response:
    result = json.loads(response.read())

if "errors" in result:
    raise RuntimeError(result["errors"])

calendar = result["data"]["user"]["contributionsCollection"]["contributionCalendar"]
weeks = calendar["weeks"]
total = calendar["totalContributions"]

CELL = 16
GAP = 5
LEFT = 35
GROUND = 235

WIDTH = LEFT + len(weeks) * (CELL + GAP) + 35
HEIGHT = 310

svg = f"""<svg xmlns="http://www.w3.org/2000/svg"
viewBox="0 0 {WIDTH} {HEIGHT}"
width="{WIDTH}"
height="{HEIGHT}">

<defs>

<style>

.plant {{
    transform-box: fill-box;
    transform-origin: bottom center;
    animation: grow 1.4s ease-out both;
}}

.leaf {{
    transform-box: fill-box;
    transform-origin: center;
    animation: sway 3s ease-in-out infinite alternate;
}}

.flower {{
    transform-box: fill-box;
    transform-origin: center;
    animation: bloom 1s ease-out both;
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
    from {{ transform: rotate(-3deg); }}
    to   {{ transform: rotate(3deg); }}
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

<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#f8fbff"/>
    <stop offset="100%" stop-color="#ffffff"/>
</linearGradient>

</defs>

<rect
    width="100%"
    height="100%"
    rx="18"
    fill="url(#sky)"
/>

<text
    x="30"
    y="32"
    font-family="Arial, sans-serif"
    font-size="18"
    font-weight="600"
    fill="#111827">
    🌱 Code Garden
</text>

<text
    x="30"
    y="53"
    font-family="Arial, sans-serif"
    font-size="11"
    fill="#64748b">
    Growing from my GitHub activity
</text>

<!-- Ground -->
<line
    x1="25"
    y1="{GROUND}"
    x2="{WIDTH-25}"
    y2="{GROUND}"
    stroke="#475569"
    stroke-width="5"
    stroke-linecap="round"
/>

"""

# --------------------------------------------
# CONTRIBUTION DATA → PLANTS
# --------------------------------------------

for week_index, week in enumerate(weeks):

    x = LEFT + week_index * (CELL + GAP)

    for day in week["contributionDays"]:

        count = day["contributionCount"]
        weekday = day["weekday"]

        if count == 0:
            continue

        # Contribution level controls plant height.
        if count <= 2:
            height = 25
            color = "#86efac"

        elif count <= 5:
            height = 42
            color = "#4ade80"

        elif count <= 9:
            height = 62
            color = "#22c55e"

        else:
            height = 85
            color = "#15803d"

        # Position from actual GitHub weekday.
        # Monday=1 ... Sunday=7
        # This keeps the contribution calendar structure.
        spacing = (GROUND - 70) / 6
        base_y = GROUND - ((weekday - 1) * spacing)

        # Garden plant grows upward from its contribution cell.
        plant_bottom = GROUND - (weekday - 1) * 2
        plant_top = plant_bottom - height

        delay = (week_index * 0.025) + (weekday * 0.04)

        svg += f"""

<g
    class="plant"
    style="animation-delay:{delay:.2f}s">

    <!-- stem -->
    <line
        x1="{x}"
        y1="{plant_bottom}"
        x2="{x}"
        y2="{plant_top}"
        stroke="{color}"
        stroke-width="3"
        stroke-linecap="round"
    />

    <!-- left leaf -->
    <ellipse
        class="leaf"
        cx="{x-7}"
        cy="{plant_top + height*0.45:.1f}"
        rx="8"
        ry="4"
        fill="{color}"
        transform="rotate(-25 {x-7} {plant_top + height*0.45:.1f})"
    />

    <!-- right leaf -->
    <ellipse
        class="leaf"
        cx="{x+7}"
        cy="{plant_top + height*0.60:.1f}"
        rx="8"
        ry="4"
        fill="{color}"
        transform="rotate(25 {x+7} {plant_top + height*0.60:.1f})"
    />
"""

        # High contribution = flower
        if count >= 6:

            flower_y = plant_top - 3

            flower_color = (
                "#60a5fa"
                if count < 10
                else "#a78bfa"
            )

            svg += f"""

    <g
        class="flower"
        style="animation-delay:{delay + 0.7:.2f}s">

        <circle cx="{x-5}" cy="{flower_y}" r="4"
                fill="{flower_color}"/>

        <circle cx="{x+5}" cy="{flower_y}" r="4"
                fill="{flower_color}"/>

        <circle cx="{x}" cy="{flower_y-5}" r="4"
                fill="{flower_color}"/>

        <circle cx="{x}" cy="{flower_y+5}" r="4"
                fill="{flower_color}"/>

        <circle cx="{x}" cy="{flower_y}" r="3"
                fill="#fbbf24"/>

    </g>
"""

        svg += "</g>\n"

# --------------------------------------------
# ACTIVITY GRID
# --------------------------------------------

GRID_Y = 265

svg += f"""
<text
    x="30"
    y="{GRID_Y - 10}"
    font-family="Arial, sans-serif"
    font-size="10"
    fill="#64748b">
    GitHub activity
</text>
"""

for week_index, week in enumerate(weeks):

    x = LEFT + week_index * (CELL + GAP)

    for day_index, day in enumerate(week["contributionDays"]):

        count = day["contributionCount"]

        if count == 0:
            color = "#f1f5f9"
        elif count <= 2:
            color = "#dcfce7"
        elif count <= 5:
            color = "#86efac"
        elif count <= 9:
            color = "#22c55e"
        else:
            color = "#15803d"

        y = GRID_Y + (day_index * (CELL + GAP) / 7)

        svg += f"""
<rect
    x="{x}"
    y="{y:.1f}"
    width="{CELL}"
    height="{CELL}"
    rx="3"
    fill="{color}"
/>
"""

svg += f"""

<text
    x="30"
    y="{HEIGHT - 15}"
    font-family="Arial, sans-serif"
    font-size="10"
    fill="#94a3b8">
    {total} contributions
</text>

<text
    x="{WIDTH - 30}"
    y="{HEIGHT - 15}"
    text-anchor="end"
    font-family="Arial, sans-serif"
    font-size="10"
    fill="#94a3b8">
    github.com/{USERNAME}
</text>

</svg>
"""

os.makedirs("code-garden", exist_ok=True)

with open(
    "code-garden/garden.svg",
    "w",
    encoding="utf-8"
) as file:
    file.write(svg)

print(f"🌱 Code Garden generated: {total} contributions")
