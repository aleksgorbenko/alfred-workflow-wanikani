# WaniKani for Alfred

Check WaniKani progress and search WaniKani subjects from Alfred.

## Usage

Browse lessons, reviews, level history, SRS statistics, accuracy, and leeches via the `wk` keyword.

Search WaniKani radicals, kanji, and vocabulary as you type via the `wks` keyword. Select a result to open its WaniKani page.

## Install

1. Download the latest `WaniKani.alfredworkflow` from [Releases](https://github.com/aleksgorbenko/alfred-workflow-wanikani/releases).
2. Double-click it and let Alfred import it.
3. Requires [Alfred](https://www.alfredapp.com) with a Powerpack licence.

## Development

- Python 3.14, standard library only.
- Runtime code is in `src/wkapi/`.
- Maintainer tools are in `tools/`.

```sh
make check   # lint, format check, and tests
make build   # package dist/WaniKani.alfredworkflow
make verify  # audit the built bundle
make release VERSION=v1.0.0
make sync-plist WORKFLOW_DIR=/path/to/installed/workflow
make link-live WORKFLOW_DIR=/path/to/installed/workflow
```

## My Other Workflows

- [BunPro for Alfred](https://github.com/aleksgorbenko/alfred-workflow-bunpro)
- [Nihongo for Alfred](https://github.com/aleksgorbenko/alfred-workflow-nihongo)
- [Netlify for Alfred](https://github.com/aleksgorbenko/alfred-workflow-netlify)
- [2Do for Alfred](https://github.com/aleksgorbenko/alfred-workflow-2do)
- [Discogs for Alfred](https://github.com/aleksgorbenko/alfred-workflow-discogs)
- [Bandcamp for Alfred](https://github.com/aleksgorbenko/alfred-workflow-bandcamp)
- [config](https://github.com/aleksgorbenko/config)
