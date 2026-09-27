# ameenagz.github.io

Personal portfolio of **Ameen Aghazadeh**, data analyst. Live at **https://ameenagz.github.io**.

## Projects

| Project | What it shows | Links |
|---|---|---|
| **Citi Bike Demand & Rebalancing** | SQL (DuckDB) + Python analysis of 1M+ 2025 bike-share trips in Jersey City and Hoboken, with rebalancing recommendations and an interactive dashboard | [Dashboard](https://ameenagz.github.io/projects/citibike-jersey-city/dashboard/) · [Code](projects/citibike-jersey-city/) |
| **Chicago Crime Analysis** | SQLite database built from public crime, census and school data, analyzed with SQL joins and aggregations | [Repo](https://github.com/ameenagz/sql-python-chicago-crime-analysis) |
| **Post-HCT Survival Prediction** | Kaplan-Meier survival analysis on 28,800 transplant records | [Repo](https://github.com/ameenagz/equity-post-HCT-survival-predictions) |

## Homepage animation

The opening screen shows the real Citi Bike network: 110 stations at their actual positions and the busiest routes between them, with riders moving along each route in proportion to how often it was ridden in 2025. The data comes from `projects/citibike-jersey-city/playground/flows.json`. Clicking the animation opens the dashboard.

## Live SQL

The homepage has a **Query my data** section where visitors can run SQL against a summary of the Citi Bike data. It uses [sql.js](https://github.com/sql-js/sql.js) (SQLite compiled to WebAssembly), so queries run in the browser with no server. The database is built by `projects/citibike-jersey-city/pipeline/04_export_sqlite.py`.

## Repository layout

```
├── index.html                      # the portfolio site (single page, no build step)
├── preview.png                     # link preview image for LinkedIn, iMessage, etc.
├── assets/vendor/sql.js/           # SQLite in the browser, for the Live SQL section (MIT license)
└── projects/
    └── citibike-jersey-city/       # full project: pipeline, SQL, charts, dashboard (see its README)
```

The site is plain HTML and CSS served by GitHub Pages from the `main` branch.
