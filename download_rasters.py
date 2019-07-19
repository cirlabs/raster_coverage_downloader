import os
import re
import fiona
import requests

import concurrent.futures

from local_settings import DOWNLOAD_BASE, COVERAGE_SHP_PATH, COVERAGE_FILENAME, DESTINATION_DIRECTORY_BASE

files_to_acquire = []


def url_write_file(file_info):
    r = requests.get(file_info[0], stream=True)
    print(file_info[0], r)

    with open(file_info[1], 'wb') as f:
        for ch in r:
            f.write(ch)


with fiona.open(os.path.join(COVERAGE_SHP_PATH, COVERAGE_FILENAME), layer=COVERAGE_FILENAME.replace('.shp', '')) as src:
    # Create a list of files to pass to the ThreadPool
    for f in src:
        img_id = f['properties']['ID']
        img_src_folder = re.search(r'^M_(\d{5})', img_id).group(1)

        # check if folder exists
        destination_directory_full = os.path.join(DESTINATION_DIRECTORY_BASE, img_src_folder)
        if not os.path.isdir(destination_directory_full):
            os.makedirs(destination_directory_full)

        for extension in ['.tif', '.tif.aux.xml', '.tif.ovr']:
            filename = '{0}{1}'.format(img_id.lower(), extension)
            full_download_path = os.path.join(DOWNLOAD_BASE, img_src_folder, filename)
            full_destination_path = os.path.join(destination_directory_full, filename)

            # Check if this file already exists locally. This assumes the download was successful and the file is not corrupt, so if that's not true you could still have partially incomplete files.
            if not os.path.isfile(full_destination_path):
                files_to_acquire.append((full_download_path, full_destination_path))

    # We can use a with statement to ensure threads are cleaned up promptly
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Start the load operations and mark each future with its URL
        future_to_url = {executor.submit(url_write_file, image_file): image_file for image_file in files_to_acquire}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                data = future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (url, exc))
