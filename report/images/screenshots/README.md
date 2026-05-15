# Real screenshots and photos

The report references several real screenshots that the LaTeX
build expects to find here. Capture each one as a PNG (or PDF)
and save with the filename below.

| File                       | What to capture                                                                  | Used in    |
|----------------------------|----------------------------------------------------------------------------------|------------|
| `mcpt_directory.png`       | A screenshot of the MCPT public route directory at <http://buyttphcm.com.vn>      | §1.1, §2.4 |
| `hcmc_bus_photo.jpg`       | A wide outdoor photo of an HCMC city bus or interchange (your own or licensed)    | §1.1       |
| `eda_hourly_demand.png`    | The hourly-demand chart from `notebooks/eda_tickets.ipynb`                        | §4.3       |
| `eda_segment_donut.png`    | The passenger-segment donut from `notebooks/eda_tickets.ipynb`                    | §4.3       |
| `eda_ghost_distribution.png` | The near-ghost-rate-by-route bar from `notebooks/eda_tickets.ipynb`             | §4.3       |
| `dashboard_network.png`    | Dashboard screenshot with the Network lens active and the map canvas             | §4.5       |
| `dashboard_route.png`      | Dashboard screenshot with the Route Explorer lens and a chart canvas open        | §4.5       |
| `dashboard_stop.png`       | Dashboard screenshot with the Stop Analysis lens and a stop selected              | §4.5       |

Tips for clean screenshots:

* Use a full HD viewport (1920×1080) so the canvas-swap rule
  (≥60 % of screen) reads correctly in print.
* Crop tightly around the dashboard chrome — no browser title bar.
* For notebook charts, use Plotly's PNG export
  (`fig.write_image(..., width=1400, height=600, scale=2)`).
* For the bus photo, prefer a daytime shot showing the route
  number painted on the bus.
