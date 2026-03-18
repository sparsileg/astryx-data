# Help System

## Overview

The Astryx help system is built using [MkDocs](https://www.mkdocs.org/) with the
[Material theme](https://squidfunk.github.io/mkdocs-material/). Help pages are
authored in Markdown and built into static HTML files deployed with the app.

## Directory Structure
```
astryx-data/
└── help/
    ├── mkdocs.yml        # MkDocs configuration
    ├── build-help.py     # Build script
    └── docs/
        ├── index.md      # Help home page
        ├── best-months.md
        ├── target-database.md
        ├── yearly-observability.md
        └── logo-wo-ring.png

astryx/
└── src/
    └── help/             # Generated HTML (do not edit directly)
```

## Adding a New Help Topic

1. Create a new markdown file in `astryx-data/help/docs/`:
```
   docs/my-new-topic.md
```

2. Add it to the `nav` section in `mkdocs.yml`:
```yaml
   nav:
     - Home: index.md
     - My New Topic: my-new-topic.md
```

3. Add a link to it in `docs/index.md`

4. Run the build script:
```bash
   python3 build-help.py
```

5. Copy the generated files from `astryx/src/help/` into the deployed app.

## Editing Existing Help

1. Edit the `.md` file in `astryx-data/help/docs/`
2. Run `python3 build-help.py`
3. Deploy updated `astryx/src/help/` contents

## Build Script
```bash
# Default output to ../../astryx/src/help
python3 build-help.py

# Custom output path
python3 build-help.py --output /path/to/output
```

## Linking from Astryx

Each help page has a predictable URL. From within the app:
```javascript
window.open('help/index.html', '_blank');
window.open('help/best-months.html', '_blank');
window.open('help/target-database.html', '_blank');
window.open('help/yearly-observability.html', '_blank');
```

## Requirements

- Python 3.x
- MkDocs: `pip3 install mkdocs`
- Material theme: `pip3 install mkdocs-material`
