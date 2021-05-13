#!/usr/bin/env
import git

COMMITID = git.Repo().head.object.hexsha[:7]

with open("VERSION.txt", "w") as f:
    f.write(COMMITID)
