#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : git_service.py
# @Author: zaoshu
# @Date  : 2020-04-10
# @Desc  :
import logging
import os

from git import Repo


class GitService:

    def __init__(self, workspace, project, branch='master', console=print):
        self.workspace = workspace
        self.project = project
        self.branch = branch
        self.repo: Repo = None
        self.dir = None
        self.console = console

    def init(self):
        dir = os.path.join(self.workspace, f'{self.project.name}')
        if os.path.exists(dir):
            repo = Repo(dir)
        else:
            repo = Repo.init(dir)
            repo.create_remote(name='origin', url=self.project.git)
        # type(repo.git).GIT_PYTHON_TRACE = 'full'
        # logging.basicConfig(level=logging.INFO)
        assert repo.remote().exists()
        self.dir = dir
        self.repo = repo

    def pull(self):
        self.repo.remote().pull(refspec=self.branch)

    def get_branches(self):
        refs = self.repo.remote().fetch()
        return [ref.name.split('/')[-1] for ref in refs]

    def check_out_branch(self):
        self.repo.git.checkout(self.branch)
