#!/usr/bin/env
from datetime import datetime

import git

COMMITID = git.Repo().head.object.hexsha[:7]
now = datetime.now()
version = COMMITID + " " + now.strftime("%d/%m/%Y %H:%M:%S")

with open("api_VERSION.txt", "w") as f:
    f.write(version)

with open("frontend_VERSION.txt", "w") as f:
    f.write(version)
