#!/usr/bin/env bash

# Run this script pointing to all libraries required to package them for the Lambda.

terraform init

cp -r /home/udallmo/spotify_etl/.venv/lib/python3.8/site-packages/spotipy ../lambda_payloads/avg_album_length_playlist_payload/
cp -r /home/udallmo/spotify_etl/.venv/lib/python3.8/site-packages/requests ../lambda_payloads/avg_album_length_playlist_payload/

cp /home/udallmo/spotify_etl/get_data.py ../lambda_payloads/avg_album_length_playlist_payload/
cp /home/udallmo/spotify_etl/spotify_analysis/playlist.py ../lambda_payloads/avg_album_length_playlist_payload/config/

cd ../lambda_payloads/avg_album_length_playlist_payload/

zip -r ../../payload.zip *

cd ../../.tf/

terraform plan