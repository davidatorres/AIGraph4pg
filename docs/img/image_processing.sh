#!/bin/bash

# Process images with ImageMagick.
# Chris Joakim, Microsoft

# Normalize the raw image sizes
convert -thumbnail 500 apache-age-logo.png  age-500.jpeg
convert -thumbnail 500 python-log-large.png python-500.jpeg
convert -thumbnail 500 azure-postgresql-logo-400x400.png azure-pg-500.jpeg
convert -thumbnail 500 openai-icon-1011x1024.png oai-500.jpeg

ls -al 
