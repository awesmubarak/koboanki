set -euf -o pipefail

cd ../koboanki && zip ../dev/koboanki.ankiaddon __init__.py config.json config.md manifest.json
