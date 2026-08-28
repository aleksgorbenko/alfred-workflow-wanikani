# alfred-workflow-wanikani

Alfred Workflow to check [WaniKani](https://www.wanikani.com) lesson/review status via the [WaniKani API v2](https://docs.api.wanikani.com/20170710).

## Commands

### `wk` - browse your progress

Selecting any row opens the relevant WaniKani page in your browser.

| Command | Shows |
|---|---|
| **Summary** | Current level, lessons & reviews available now, when the next review batch unlocks |
| **Levels** | ETA to next level, then level history with time spent per level |
| **Stats** | SRS stage breakdown (Apprentice / Guru / Master / Enlightened / Burned) |
| **Accuracy** | Overall, meaning, and reading review accuracy |
| **Leeches** | Worst-accuracy items, with ETA to burn |
| **Lessons** | Current lesson queue, searchable |
| **Reviews** | Current review queue, searchable |

Lessons and Reviews rows show `𝐖level・type・parts of speech`, colour-coded by subject type (radical / kanji / vocabulary).

### `wks <query>` - dictionary search

Searches wanikani.com as you type; no Enter needed. Returns radicals, kanji, and vocabulary with readings and meanings. Selecting a row opens that subject's WaniKani page.

Results are parsed from the public search page - the API has no full-text subject search endpoint.

## Install

1. Download the latest `WaniKani.alfredworkflow` from [Releases](https://github.com/aleksgorbenko/alfred-workflow-wanikani/releases).
2. Double-click it - Alfred will prompt to import.
3. Requires [Alfred](https://www.alfredapp.com) with a Powerpack license.

## Setup

1. Open the workflow in Alfred, click the `[x]` (Configure Workflow) button.
2. Paste your [WaniKani personal access token](https://www.wanikani.com/settings/personal_access_tokens) into the **Wanikani API Key** field (needs `all_data:read`).

## Development

- Python 3.14, stdlib only.
- `src/wkapi/` - runtime scripts Alfred calls.
- `tools/` - dev-only scripts (icon gen, bundle verification), not shipped.

```sh
make check    # lint + format check + tests
make build    # package dist/WaniKani.alfredworkflow
make verify   # audit the built bundle for local paths, tokens, junk files
make release VERSION=v1.0.0
make sync-plist WORKFLOW_DIR=/path/to/installed/workflow   # pull info.plist edits back
make link-live WORKFLOW_DIR=/path/to/installed/workflow    # symlink src/ for live dev
```

## My Other Workflows

- [2Do for Alfred](https://github.com/aleksgorbenko/alfred-workflow-2do)
- [BunPro for Alfred](https://github.com/aleksgorbenko/alfred-workflow-bunpro)
