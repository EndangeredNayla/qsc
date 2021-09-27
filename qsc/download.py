# QSC (Qt SDK Creator) - A tool for automatically downloading, building and stripping down Qt
# Copyright (C) 2020 spycrab0
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""All the download related stuff goes here"""

import os
import qsc
import requests
import shutil
import datetime

def source_url(release):
    base_release = release[:release.rfind('.')]
    return qsc.REPO_SRC_PATH.format(qsc.REPO_BASE_URL, base_release, release)

def download_file(url, path):
    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        processed = 0
        total = int(response.headers['content-length'])
        with open(path, "wb") as file:
            for chunk in response.iter_content(chunk_size=shutil.COPY_BUFSIZE):
                if not chunk:
                    continue
                file.write(chunk)
                processed += len(chunk)
                print("{}/{}".format(processed, total))

def download_release(release):
    url = source_url(release)
    download_path = os.path.join("archives", "qtbase-everywhere-src-{}.zip".format(release))

    print("Downloading Qt {}...".format(release))
    print(datetime.datetime.now())

    if not os.path.isdir("archives"):
        os.mkdir("archives")

    if qsc.USE_CACHE and os.path.isfile(download_path):
        print("Cached")
        return

    download_file(url, download_path)

    print("Done")
    print(datetime.datetime.now())
