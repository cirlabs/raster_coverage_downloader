# raster_coverage_downloader
A very simple script to download California NAIP imagery from a California government site, using a coverage shapefile.

There is a very nice WMS layer for NAIP, but when you're rendering out printed maps or video, the tiles don't always load. I find it easy to take a coverage shapefile, select the tiles I want, make a new layer in QGIS, then download away.

This uses semi-fancy concurrent threading, which I am not an expert on. But it does it.

Requirements:
 - Fiona
 - GDAL
 - Requests
 
 Usage:
 ```python download_rasters.py```
