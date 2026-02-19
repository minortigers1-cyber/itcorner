name: Update My IPTV List
on:
  schedule:
    - cron: '0 0 * * *'
  workflow_dispatch:

permissions:
  contents: write  # This gives the bot permission to push changes

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install Dependencies
        run: pip install requests urllib3

      - name: Run Merge Script
        run: python update_playlist.py

      - name: Commit and Push
        run: |
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          git add playlist.m3u
          # The next line prevents the error if there are no channel updates
          git commit -m "Automated Playlist Update" || echo "No changes to commit"
          git push origin main