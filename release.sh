set -euf -o pipefail

cd koboanki && zip ../koboanki.ankiaddon __init__.py config.json config.md manifest.json
