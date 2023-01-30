import os
import shutil
from mbot.openapi import mbot_api
from mbot.common.osutils import OSUtils
import logging

_LOGGER = logging.getLogger(__name__)


def os_tool(src, dst, rename, copy_type):
    if not os.path.exists(src):
        _LOGGER.error("源目录/文件不存在")
        return
    dst = dst.strip()
    dst = dst.rstrip("\\")
    basename = os.path.basename(src)
    if rename:
        basename = rename
    dst = f"{dst.rstrip('/')}/{basename}"
    if os.path.exists(dst):
        _LOGGER.error("目标目录已存在该目录或文件")
        return

    if copy_type == 'link':
        hard_link(src, dst)
    if copy_type == 'copy':
        copy(src, dst)


def hard_link(src, dst):
    if os.path.isdir(src):
        shutil.copytree(src, dst, copy_function=os.link)
    if os.path.isfile(src):
        os.link(src, dst)


def copy(src, dst):
    if os.path.isdir(src):
        shutil.copytree(src, dst)
    if os.path.isfile(src):
        shutil.copy(src, dst)


def move(src, dst):
    shutil.move(src, dst)


def clear_notify_tool(uid):
    mbot_api.notify.clear_system_message(uid)


def list_user():
    return mbot_api.user.list()


def delete_hard_link_tool(source_filepath, find_path=None, use_cache: bool = True):
    files = OSUtils.find_hardlink_files(source_filepath, find_path, use_cache)
    for file_path in files:
        if os.path.exists(file_path):
            os.remove(file_path)


