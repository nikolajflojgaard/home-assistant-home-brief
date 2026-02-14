#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
src="${repo_root}/docs/workflows/validate.yml"
dst_dir="${repo_root}/.github/workflows"
dst="${dst_dir}/validate.yml"

mkdir -p "${dst_dir}"
cp "${src}" "${dst}"

echo "Enabled CI workflow: ${dst}"

