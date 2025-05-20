set -euo pipefail

autoflake \
  --in-place \
  --remove-all-unused-imports \
  --remove-unused-variables \
  --recursive \
  .

isort .

black .

flake8 .
