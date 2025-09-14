#!/bin/bash

# This script safely installs Playwright browser binaries by temporarily disabling SSL verification
# Only use in trusted environments (e.g. local VM with self-signed certificates)

echo "🔧 Disabling SSL verification temporarily..."
export NODE_TLS_REJECT_UNAUTHORIZED=0

echo "🌐 Running 'playwright install'..."
playwright install

echo "✅ Re-enabling SSL verification..."
unset NODE_TLS_REJECT_UNAUTHORIZED

echo "🎉 Playwright installation complete with SSL verification restored."