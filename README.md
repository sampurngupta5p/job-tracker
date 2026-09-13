# Sampurn FMCG Live Internship Tracker

A persistent FMCG-focused internship dashboard seeded from the current job-search dashboard and designed to refresh automatically.

## What it does
- Keeps a persistent `data/jobs.json` database.
- Runs every 6 hours with GitHub Actions.
- Searches configured FMCG company sources through a web-search provider.
- Deduplicates jobs and records first/last seen timestamps.
- Keeps direct apply and company-career links.
- Can be published as a GitHub Pages site.

## One-time setup
1. Create a new **public GitHub repository** and upload this folder.
2. In GitHub: **Settings → Secrets and variables → Actions → New repository secret**.
3. Create `SERPER_API_KEY` using a Serper API key. The workflow uses Google-style web search for discovery; without this secret the seeded dashboard still works but automatic discovery is disabled.
4. In **Settings → Pages**, set the source to **GitHub Actions**.
5. Run **Actions → FMCG Job Tracker Sync → Run workflow** once.
6. Open the GitHub Pages URL shown under **Settings → Pages**.

The scheduled workflow then runs every 6 hours and commits updated `data/jobs.json` back into the repository before redeploying the dashboard.

## Source strategy
The tracker prioritizes official company career pages and uses web search for discovery. ATS platforms can be added as dedicated adapters later. Lever exposes published postings through its public Postings API, which is useful for direct ATS ingestion.

## Important
The tracker does not auto-apply to jobs. It only discovers, scores, tracks, and links to them.
