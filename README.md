# Arabic Perfect Setup (auto-updating AIOStreams template)

This repository rebuilds the Arabic edition of the numb3rs AIOStreams template
every day and hosts it at a fixed link, so AIOStreams can offer **Apply Update**
when numb3rs (or the Arabic layer) changes.

## Template link

`https://raw.githubusercontent.com/aelhusseini/arabic-perfect-setup/main/templates/AIOStreams-Arabic-Edition.json`

In AIOStreams: **Save & Install → Import → Import Template**, paste that link,
**Go**, and continue as in the guide. Import by link (not from a file) so
AIOStreams remembers where to check for updates.

## How it stays current

- Every day at 03:17 UTC the workflow downloads numb3rs' current template,
  reapplies the Arabic layer with `scripts/build_aiostreams.py`, and commits
  only when something changed.
- A change gets a date-based version (for example `2026.1122.1838`) and a
  changelog line, which is what makes AIOStreams show the update prompt.
- Editing `scripts/build_aiostreams.py` triggers a rebuild too. To rebuild by
  hand, open **Actions → Rebuild Arabic template → Run workflow**.

TamTaro's filters and Vidhin's regexes are synced by AIOStreams itself and
never need a rebuild. The template holds no API keys, debrid keys or addon links;
those stay in your own AIOStreams configuration.
