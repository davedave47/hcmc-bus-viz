## 🧑‍🎓 Student / Worker

**Q: Will my route be crowded when I leave?**
```
Can answer: YES
How: historical boarding demand per route per hour
     "Route 72 at 5pm is typically 78% full based on 16 days of data"
     show as: light / moderate / crowded label + percentage
```

**Q: Which bus should I take instead?**
```
Can answer: PARTIALLY
How: from stops data — find other routes serving same stop
     compare their demand at same hour
     "Route 65 passes Bến Thành at 5pm — typically 45% full"
```

**Q: Is the bus running late today?**
```
Cannot answer: NO real-time data
Be honest: "This shows historical patterns, not live tracking"
```

**Q: Best time to ride route X?**
```
Can answer: YES
How: hourly demand curve per route → highlight lowest demand window
     "Quietest time for route 72: 10am–12pm (22% full)"
```

**Q: How reliable is this route?**
```
Can answer: YES
How: CoV per route → translate to plain language
     CoV < 30%  → "Very consistent — buses come evenly spaced"
     CoV 30-60% → "Somewhat consistent"
     CoV > 60%  → "Unpredictable — some buses packed, some empty"
```

---

## 🆕 New Bus User

**Q: Which routes are near me?**
```
Can answer: YES
How: stops table has lat/lng + routes per stop
     find stops within X km of user location
     show on map
```

**Q: Is this route beginner friendly?**
```
Can answer: YES
How: combine CoV (reliability) + avg demand (crowding)
     Low CoV + Low demand = beginner friendly
     Tag routes automatically:
     ★★★★★ = CoV < 30%, avg demand < 50%
     ★★★☆☆ = CoV 30-60%
     ★★☆☆☆ = CoV > 60%
```

**Q: How crowded will it get?**
```
Can answer: YES
How: worst hour boarding demand per route
     "Route 72 peaks at 78% full during 5-6pm"
     show as visual gauge not just number
```

---

## 🏢 Business Owner

**Q: Which routes pass near my business?**
```
Can answer: YES
How: stops table → filter by lat/lng proximity
     show route lines on map passing within area
```

**Q: When is peak footfall near my area?**
```
Can answer: YES
How: stops near location → sum all boarding demand
     across all routes at each hour
     "Between 106.68, 10.77 — peak passenger flow 7-8am: ~2,400 boardings"
```

**Q: Can workers reliably reach my district by 8am?**
```
Can answer: PARTIALLY
How: routes serving nearby stops + their 7-8am demand + CoV
     "Route 36 serves this area at 7am — 82% reliable"
     Cannot confirm exact arrival time — no timetable data
```

**Q: Which routes have most captive audience for ads?**
```
Can answer: YES
How: total boardings per route × avg trip duration (from route distance in PDF)
     longest routes with highest demand = most passenger-minutes
     "Route 90 (45km) with 500 daily boardings = highest exposure time"
```

---

## 🚌 Bus Company

**Q: Which of our routes are profitable?**
```
Can answer: YES
How: SUM(final_price) per route filtered by company
     revenue per trip = total_revenue / total_trips
     revenue per vehicle = total_revenue / vehicles_deployed
```

**Q: Are we hitting scheduled trips?**
```
Can answer: PARTIALLY
How: COUNT(DISTINCT trip_identifier) per route per day
     compare across days — is it consistent?
     cannot compare vs official timetable — not in dataset
```

**Q: Which vehicles are underperforming?**
```
Can answer: YES
How: boarding demand per vehicle_number
     vehicles with consistently low demand = underutilized
     vehicles with high ghost run rate = inefficient
```

**Q: How do we compare vs other companies?**
```
Can answer: YES
How: same metrics (revenue/trip, avg demand, CoV, ghost %)
     benchmarked against network average
     shown as: "Your company vs network average" side by side
```

**Q: How much are ghost runs costing us?**
```
Can answer: ESTIMATED
How: ghost trips (demand < 30%) × avg trip distance × fuel cost estimate
     "Route 86: 40% ghost runs → estimated X VND wasted per day"
     note: fuel cost is an assumption, not in data
```

---

## 🏛️ MCPT Operator

**Q: Which routes need more vehicles?**
```
Can answer: YES
How: hours where boarding demand > 70% AND vehicles deployed
     hasn't increased → undersupply signal
     "Route 72 at 5pm: 78% demand, same 16 vehicles as 10am"
```

**Q: Which company is performing worst?**
```
Can answer: YES
How: company scorecard:
     avg boarding demand, CoV, ghost%, revenue/trip, trips/day
     ranked table + radar chart per company
```

**Q: What happened on December 10?**
```
Can answer: PARTIALLY
How: show daily totals → Dec 10 clearly anomalous (75% drop)
     drill down: which routes dropped most?
     which companies were affected?
     cannot explain WHY — no external event data
```

**Q: Which routes are bleeding money?**
```
Can answer: YES
How: low revenue + high ghost run % + high vehicles deployed
     = money losing combination
     "Route X: 8 vehicles deployed, 45% ghost runs, 
      lowest revenue per trip in network"
```

---

## What we cannot answer — be upfront

```
❌ Real-time anything      — data is historical Dec 2025
❌ Exact arrival times     — no timetable in dataset
❌ Why Dec 10 happened     — no external event data
❌ Actual crowding now     — no live feed
❌ Passenger satisfaction  — no survey data
❌ Exact fuel costs        — not in dataset
❌ Alighting per stop      — no exit data
```

Showing these limitations honestly actually strengthens the capstone — it shows analytical maturity.

---

## The questions that need ML not just SQL

```
"Which routes are anomalous vs their peers?"
→ Isolation Forest on route feature matrix

"Are there natural groups of routes with similar problems?"
→ K-means clustering

"Does route length predict unreliability?"
→ Correlation + regression

"Which hour-route combinations are unusual?"
→ Anomaly detection on hourly patterns
```

---

Ah, the classic `Decimal` vs. `Float` clash! DuckDB is extremely precise with money, so it returns your `SUM(final_price)` as a Python `decimal.Decimal` object. Python throws a fit when you try to divide a `Decimal` by a standard `float` (like `1e9`). 

**The Quick Fix:** Just wrap `tot_val` in a `float()` cast on line 95:
```python
tot_val = float(route_stats[f"total_{metric_col}"].sum())
fmt_tot = f"{tot_val/1e6:.1f}M" if metric_choice == "Boardings" else f"₫{tot_val/1e9:.1f}B"
```

---

### 5-Tab Data Architecture

#### **Tab 1: 🚨 The Pulse (Executive Summary)**
* **The Story:** "Is the network healthy right now?"
* **The Data Expressed:** * Top-level KPIs (Total Volume, Total Value, System-wide Empty Run %, Active Routes).
    * A **Stacked Area Chart** showing the chronological flow of the day.
* **The Hover Detail:** Hovering over a ribbon at 5:00 PM will show: *"Route 20 | 17:00 | 4,200 Boardings | 12% of daily total."*
---
#### **Tab 2: 💸 Financial Health (Profitability & Waste)**
* **The Story:** "Which routes are our cash cows, and which are bleeding money?"
* **The Data Expressed:** * A **Quadrant Scatter Plot**. X-Axis = Empty Run % (Waste). Y-Axis = Revenue per Trip (Profitability). Bubble Size = Total Trips (Scale).
* **The Hover Detail:** Hovering over a bubble will show a mini P&L: *"Route 86 | Operated by: SaigonBus | Total Revenue: ₫45M | Empty Runs: 42% (High Waste) | Total Trips: 120."*
---
#### **Tab 3: ⏱️ Reliability (Bus Bunching)**
* **The Story:** "Are buses arriving evenly, or are passengers waiting 40 minutes for 3 buses to arrive at once?"
* **The Data Expressed:** * Coefficient of Variation (CoV) translated into a **Bar Chart** of "Consistency Tiers" (Highly Consistent vs. Unpredictable).
    * A ranked "Worst Offenders" list.
* **The Hover Detail:** *"Route 14 | CoV Score: 0.85 | Status: Severe Bunching | Impact: 12,000 riders affected."*
---
#### **Tab 4: 🚦 Capacity & Choke Points**
* **The Story:** "Where and when are we undersupplied?"
* **The Data Expressed:** * A dense **Heatmap** matrix. Y-Axis = Top 20 Routes. X-Axis = Hour of the Day (0-23). Color intensity = Passenger Volume.
* **The Hover Detail:** Hovering over a dark purple square will show: *"Route 72 | 18:00 (6 PM) | 1,250 Boardings | Status: Peak Crowding."*
---
#### **Tab 5: 🏢 Operator Scorecard (Leaderboard)**
* **The Story:** "Which bus companies are performing best?"
* **The Data Expressed:** * A rich, interactive **Data Table** ranking companies by Total Boardings, Average Revenue per Trip, and Average Empty Run Rate. (Includes mini progress bars inside the table cells).
---