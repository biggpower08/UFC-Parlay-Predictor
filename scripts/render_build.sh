#!/usr/bin/env bash
set -euo pipefail

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Building frontend..."
cd app/frontend
npm ci
npm run build

echo "Copying frontend into backend static folder..."
cd ../..
rm -rf ufc_predictor/static_app
mkdir -p ufc_predictor/static_app
cp -R app/frontend/out/. ufc_predictor/static_app/

echo "Verifying frontend build..."
test -f ufc_predictor/static_app/index.html
ls -la ufc_predictor/static_app | head
