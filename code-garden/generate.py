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

calendar = (
    result["data"]["user"]
    ["contributionsCollection"]
    ["contributionCalendar"]
)

weeks = calendar["weeks"]
total = calendar["totalContributions"]


# ============================================================
# LAYOUT
# ============================================================

LEFT = 42
CELL = 14
GAP = 4

WEEK_WIDTH = CELL + GAP

GRID_WIDTH = len(weeks) * WEEK_WIDTH

WIDTH = LEFT + GRID_WIDTH + 45

GROUND_Y = 225

HEATMAP_TOP = 245
HEATMAP_CELL = 14
HEATMAP_GAP = 4

HEIGHT = HEATMAP_TOP + (7 * (HEATMAP_CELL + HEATMAP_GAP)) + 45


# ============================================================
# COLORS
# ============================================================

def activity_color(count):

    if count == 0:
        return "#eef2f7"

    if count <= 2:
        return "#bbf7d0"

    if count <= 5:
        return "#4ade80"

    if count <= 9:
        return "#22c55e"

    return "#15803d"


def plant_color(count):

    if count <= 2:
        return "#86efac"

    if count <= 5:
        return "#4ade80"

    if count <= 9:
        return "#22c55e"

    return "#15803d"


def plant_height(count):

    if count <= 2:
        return 25

    if count <= 5:
        return 42

    if count <= 9:
        return 60

    return 82


# ============================================================
# SVG START
# ============================================================

svg = f"""<svg
xmlns="http://www.w3.org/2000/svg"
viewBox="0 0 {WIDTH} {HEIGHT}"
width="{WIDTH}"
height="{HEIGHT}"
role="img"
aria-label="Shreyam's GitHub Code Garden">

<defs>

    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#f8fbff"/>
        <stop offset="100%" stop-color="#ffffff"/>
    </linearGradient>

    <linearGradient id="soil" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0%" stop-color="#57534e"/>
        <stop offset="50%" stop-color="#44403c"/>
        <stop offset="100%" stop-color="#57534e"/>
    </linearGradient>

    <style>

        .plant {{
            transform-box: fill-box;
            transform-origin: bottom center;
            animation: grow 1.5s ease-out both;
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


<!-- ====================================================== -->
<!-- BACKGROUND                                             -->
<!-- ====================================================== -->

<rect
    width="100%"
    height="100%"
    rx="18"
    fill="url(#sky)"
/>


<!-- ====================================================== -->
<!-- HEADER                                                  -->
<!-- ====================================================== -->

<text
    x="32"
    y="34"
    font-family="Arial, Helvetica, sans-serif"
    font-size="19"
    font-weight="600"
    fill="#111827">

    Code Garden

</text>

<text
    x="32"
    y="55"
    font-family="Arial, Helvetica, sans-serif"
    font-size="11"
    fill="#64748b">

    Growing from my GitHub activity

</text>


<!-- ====================================================== -->
<!-- SUN                                                     -->
<!-- ====================================================== -->

<circle
    cx="{WIDTH - 55}"
    cy="45"
    r="18"
    fill="#fde68a"
    opacity="0.9"
/>


<!-- ====================================================== -->
<!-- SOIL                                                    -->
<!-- ====================================================== -->

<path
    d="
        M25 {GROUND_Y}
        Q {WIDTH//4} {GROUND_Y-8}
          {WIDTH//2} {GROUND_Y}
        T {WIDTH-25} {GROUND_Y}
    "
    fill="none"
    stroke="url(#soil)"
    stroke-width="8"
    stroke-linecap="round"
/>

<path
    d="
        M25 {GROUND_Y+8}
        Q {WIDTH//4} {GROUND_Y}
          {WIDTH//2} {GROUND_Y+8}
        T {WIDTH-25} {GROUND_Y+8}
    "
    fill="none"
    stroke="#a8a29e"
    stroke-width="2"
    opacity="0.6"
/>


<!-- ====================================================== -->
<!-- PLANTS                                                  -->
<!-- ====================================================== -->
"""


# ============================================================
# GENERATE PLANTS FROM REAL CONTRIBUTIONS
# ============================================================

for week_index, week in enumerate(weeks):

    x = LEFT + week_index * WEEK_WIDTH

    for day in week["contributionDays"]:

        count = day["contributionCount"]

        if count == 0:
            continue

        color = plant_color(count)
        height = plant_height(count)

        # Every contribution day gets a plant.
        # More contributions = taller plant.

        bottom = GROUND_Y

        top = bottom - height

        delay = (
            week_index * 0.018
            + day["weekday"] * 0.04
        )

        svg += f"""

<g
    class="plant"
    style="animation-delay:{delay:.2f}s">

    <!-- STEM -->

    <line
        x1="{x}"
        y1="{bottom}"
        x2="{x}"
        y2="{top}"
        stroke="{color}"
        stroke-width="3"
        stroke-linecap="round"
    />


    <!-- LEFT LEAF -->

    <ellipse
        class="leaf"
        cx="{x - 7}"
        cy="{top + height * 0.48:.1f}"
        rx="9"
        ry="4.5"
        fill="{color}"
        transform="
            rotate(
                -25
                {x - 7}
                {top + height * 0.48:.1f}
            )
        "
    />


    <!-- RIGHT LEAF -->

    <ellipse
        class="leaf"
        cx="{x + 7}"
        cy="{top + height * 0.65:.1f}"
        rx="9"
        ry="4.5"
        fill="{color}"
        transform="
            rotate(
                25
                {x + 7}
                {top + height * 0.65:.1f}
            )
        "
    />
"""


        # ====================================================
        # FLOWER
        # ====================================================

        if count >= 6:

            flower_y = top - 5

            if count >= 10:
                flower = "#a78bfa"
            else:
                flower = "#60a5fa"

            svg += f"""

    <g
        class="flower"
        style="animation-delay:{delay + 0.6:.2f}s">

        <circle
            cx="{x - 5}"
            cy="{flower_y}"
            r="4"
            fill="{flower}"
        />

        <circle
            cx="{x + 5}"
            cy="{flower_y}"
            r="4"
            fill="{flower}"
        />

        <circle
            cx="{x}"
            cy="{flower_y - 5}"
            r="4"
            fill="{flower}"
        />

        <circle
            cx="{x}"
            cy="{flower_y + 5}"
            r="4"
            fill="{flower}"
        />

        <circle
            cx="{x}"
            cy="{flower_y}"
            r="3"
            fill="#fbbf24"
        />

    </g>
"""


        svg += "</g>\n"


# ============================================================
# ACTIVITY HEATMAP
# ============================================================

svg += f"""

<!-- ====================================================== -->
<!-- ACTIVITY                                               -->
<!-- ====================================================== -->

<text
    x="{LEFT}"
    y="{HEATMAP_TOP - 12}"
    font-family="Arial, Helvetica, sans-serif"
    font-size="11"
    font-weight="500"
    fill="#475569">

    GitHub activity

</text>
"""


# IMPORTANT:
# contributionDays are Monday-Sunday.
# We explicitly give each day its own 14x14 box.

for week_index, week in enumerate(weeks):

    x = LEFT + week_index * WEEK_WIDTH

    for day in week["contributionDays"]:

        count = day["contributionCount"]

        weekday = day["weekday"]

        color = activity_color(count)

        y = (
            HEATMAP_TOP
            + (weekday - 1) * (HEATMAP_CELL + HEATMAP_GAP)
        )

        svg += f"""

<rect
    x="{x}"
    y="{y}"
    width="{HEATMAP_CELL}"
    height="{HEATMAP_CELL}"
    rx="3"
    fill="{color}"
/>
"""


# ============================================================
# LEGEND
# ============================================================

legend_y = HEIGHT - 24

svg += f"""

<text
    x="{LEFT}"
    y="{legend_y}"
    font-family="Arial, Helvetica, sans-serif"
    font-size="10"
    fill="#94a3b8">

    Less

</text>
"""


legend_x = LEFT + 32

for i, color in enumerate([
    "#eef2f7",
    "#bbf7d0",
    "#4ade80",
    "#22c55e",
    "#15803d"
]):

    x = legend_x + i * 20

    svg += f"""

<rect
    x="{x}"
    y="{legend_y - 10}"
    width="13"
    height="13"
    rx="3"
    fill="{color}"
/>
"""


svg += f"""

<text
    x="{legend_x + 110}"
    y="{legend_y}"
    font-family="Arial, Helvetica, sans-serif"
    font-size="10"
    fill="#94a3b8">

    More

</text>


<!-- CONTRIBUTION TOTAL -->

<text
    x="{WIDTH - 30}"
    y="{legend_y}"
    text-anchor="end"
    font-family="Arial, Helvetica, sans-serif"
    font-size="10"
    fill="#64748b">

    {total} contributions

</text>


</svg>
"""


# ============================================================
# WRITE FILE
# ============================================================

os.makedirs("code-garden", exist_ok=True)

with open(
    "code-garden/garden.svg",
    "w",
    encoding="utf-8"
) as file:

    file.write(svg)

print(
    f"🌱 Code Garden generated from {total} contributions"
)
