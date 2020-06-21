#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : git_service.py
# @Author: zaoshu
# @Date  : 2020-04-10
# @Desc  :
import os

from git import Repo


class GitService:

    def __init__(self, code_path, project, branch='master', console=print):
        self.code_path = code_path
        self.project = project
        self.branch = branch
        self.repo: Repo = None
        self.console = console

    def init(self):
        if os.path.exists(self.code_path):
            repo = Repo(self.code_path)
        else:
            repo = Repo.init(self.code_path)
        if len(repo.remotes) != 0 and repo.remote('origin').exists():
            repo.delete_remote(repo.remote('origin'))
        repo.create_remote(name='origin', url=self.project.git)
        assert repo.remote().exists()
        self.repo = repo

    def pull(self):
        self.repo.remote().pull(refspec=self.branch)

    def get_branches(self):
        refs = self.repo.remote().fetch()
        return [ref.name.split('/')[-1] for ref in refs]

    def check_out_branch(self):
        self.repo.git.checkout(self.branch)

    def pull_project(self):
        self.console('初始化仓库')
        self.init()
        self.console(f'切换到{self.branch}分支')
        self.check_out_branch()
        self.console('拉取代码')
        self.pull()
