# Snowflake Showcase Application

This python application for the Multi Angle Snowflake Camera (MASC) tracks snowflake images in real time and provides a GUI for users to sort incoming images by size and clarity (sharpness).

NOTE: This app is built ONLY for the MASC mini mac near Alta Ski resort where it is hosted.

# USAGE

## User Interface

1. To start the application click the black snowflake logo on the Desktop entitiled `Showcase` OR In the `masc_showcase` folder, run `START.py`.
2. Log in with your CHPC credentials.
3. Use sliders to set lower bound thresholds for snowflakes.
   - Only snowflakes with values higher than these will be uploaded to the showcase.
4. As snowflakes are photographed, if they meet the threshold criteria, they will be displayed in the Image Subset.
   - The newest image that meets the criteria will be shown in the top left.
5. Size is calculated by the longest linear dimension (in pixels) and normalized by an exponential function.
6. Sharpness is calculated using a Laplacian transform, which also prefers sharper images.

## Data Parameters

To calibrate the system for size calculation, change values in the `dataparam.txt` file (e.g., `data=123`).

## File Management

- The `chosen` folder contains all images that have been selected by the algorithm with selected parameters all-time
- Deleting files from the sort folder is okay whenever possible, but **do not** delete files from `sort` or `chosen` while the showcase is running.

## Website

- **Current link:** [MASC Showcase Live Feed](https://www.inscc.utah.edu/~snowflake/LiveFeed/)
- HTML data plots are uploaded roughly every 60 seconds.
- Storms are started when a threshold of 3 snowflakes in 10 seconds is crossed.
- Storms end when 60 seconds pass with no snowflakes.


