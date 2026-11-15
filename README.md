# Coin Break Timer

A coin-themed "be right back" countdown for live streams. One static page, no backend.

Add it to OBS as a Browser source and set it up in the URL:

`?m=15&msg=Out%20to%20lunch&name=Your%20Stream&autostart=1&controls=0`

- `m` is minutes; `until=13:30` counts down to a clock time instead
- `theme=light` or `theme=dark`
- `bg=0` for a transparent background

## Coin photos

Photos are from Wikimedia Commons: US half eagles from the National Numismatic Collection,
Smithsonian Institution, and the Walking Liberty half dollar by BrandonBigheart (CC BY-SA 3.0).
`scripts/fetch_coins.py` downloads them and cuts each coin out to a transparent WebP in `coins/`.
