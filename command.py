import logging
from mbot.core.params import ArgSchema, ArgType
from mbot.core.plugins import plugin, PluginCommandContext, PluginCommandResponse

from .tools import *
from .os_tools import *
from .plugin_tools import *
from .task_tools import *

_LOGGER = logging.getLogger(__name__)

def tasks_enum():
    tasks = get_tasks()
    enum_list = []
    for task in tasks:
        name = task["name"] + " —— " + task["desc"]
        enum_list.append({"name": name, "value": task["name"]})
    return enum_list

def get_copy_type():
    copy_type = [
        {'value': 'link', 'name': '硬链'},
        {'value': 'copy', 'name': '复制'},
        {'value': 'move', 'name': '移动'}
    ]
    return copy_type


@plugin.command(name='os', title='文件操作', desc='文件操作工具', icon='', run_in_background=True)
def os(
        ctx: PluginCommandContext,
        src: ArgSchema(ArgType.String, '源文件/目录路径', ''),
        dst: ArgSchema(ArgType.String, '目标目录', ''),
        rename: ArgSchema(ArgType.String, '文件或目录重命名', '传空则默认源文件/目录名称'),
        copy_type: ArgSchema(ArgType.Enum, '', '', enum_values=get_copy_type, multi_value=False)):
    os_tool(src, dst, rename, copy_type)
    return PluginCommandResponse(True, f'操作完成')


def get_user_option():
    user_list = list_user()
    return [{'name': user.nickname, 'value': user.uid} for user in user_list]


@plugin.command(name='clear_notify', title='清空通知', desc='一键清空通知', icon='',
                run_in_background=True)
def clear_notify(
        ctx: PluginCommandContext,
        uids: ArgSchema(ArgType.Enum, '用户', '选择用户清空通知', enum_values=get_user_option, multi_value=True)):
    _LOGGER.info(uids)
    for uid in uids:
        clear_notify_tool(uid)
    return PluginCommandResponse(True, f'清空完成')


def get_use_cache():
    return [{'value': 1, 'name': '使用缓存'}, {'value': 2, 'name': '不使用缓存'}]


@plugin.command(name='delete_hard_link', title='删除硬链文件', desc='', icon='',
                run_in_background=True)
def delete_hard_link(
        ctx: PluginCommandContext,
        src: ArgSchema(ArgType.String, '源文件路径', ''),
        find_path: ArgSchema(ArgType.String, '查找目录', ''),
        use_cache: ArgSchema(ArgType.Enum, '使用缓存', '', enum_values=get_use_cache, multi_value=False)
):
    flag = True
    if use_cache:
        if use_cache == 1:
            flag = True
        if use_cache == 2:
            flag = False
    delete_hard_link_tool(src, find_path, flag)
    return PluginCommandResponse(True, f'删除硬链完成')


def get_plugins():
    return list_plugins()


@plugin.command(name='install_plugin', title='安装插件', desc='', icon='',
                run_in_background=True)
def install_plugin(
        ctx: PluginCommandContext,
        download_url: ArgSchema(ArgType.String, '插件下载地址', '')
):
    _LOGGER.info("安装插件")
    install(download_url)
    return PluginCommandResponse(True, f'安装完成')


@plugin.command(name='upgrade_plugin', title='升级插件', desc='', icon='',
                run_in_background=True)
def upgrade_plugin(
        ctx: PluginCommandContext,
        plugin: ArgSchema(ArgType.Enum, '选择插件', '', enum_values=get_plugins, multi_value=False),
        download_url: ArgSchema(ArgType.String, '插件下载地址', '')
):
    _LOGGER.info("升级插件")
    upgrade(plugin_name=plugin['plugin_name'], download_url=download_url)
    return PluginCommandResponse(True, f'升级插件完成')


@plugin.command(name='reload_plugin', title='重启插件', desc='', icon='',
                run_in_background=True)
def reload_plugin(
        ctx: PluginCommandContext,
        plugin: ArgSchema(ArgType.Enum, '选择插件', '', enum_values=get_plugins, multi_value=False)
):
    _LOGGER.info("重启插件")
    load(plugin['plugin_path'])
    return PluginCommandResponse(True, f'重启插件完成')


@plugin.command(name='edit_task', title='修改定时任务配置', desc='修改注册到mr的定时任务运行时间等', icon='HourglassFull',run_in_background=False)
def edit(ctx: PluginCommandContext,
                task: ArgSchema(ArgType.Enum, '定时任务', '选择需要修改的定时任务', enum_values=tasks_enum,
                                   multi_value=False),
                jitter: ArgSchema(ArgType.String, '随机延迟', '随机延迟时间，单位为秒，不填则无', required=False),
                cron_expression: ArgSchema(ArgType.String, 'cron表达式', 'cron表达式，和下面minute second二选一。两者都填取cron表达式', required=False),
                minute: ArgSchema(ArgType.String, '分钟', '任务执行间隔分钟，和上面cron表达式二选一', required=False),
                second: ArgSchema(ArgType.String, '秒', '任务执行间隔秒，和上面cron表达式二选一', required=False),
                ):
    task_meta = get_task_meta(task)
    minute = int(minute) if minute else None
    second = int(second) if second else None
    if not task_meta:
        return PluginCommandResponse(False, "未找到该任务")
    if not jitter:
        jitter = None
    else:
        jitter = int(jitter)
    if cron_expression:
        res = edit_task(task_meta.task, task_meta.name, task_meta.desc, cron_expression=cron_expression, jitter=jitter, plugin_name=task_meta.plugin_name)
    elif minute or second:
        res = edit_task(task_meta.task, task_meta.name, task_meta.desc, minutes=minute, seconds=second, jitter=jitter, plugin_name=task_meta.plugin_name)
    else:
        return PluginCommandResponse(False, "请填写cron表达式或者minute second")
    if res is False:
        return PluginCommandResponse(False, f"修改定时 {task} 任务失败")
    return PluginCommandResponse(True, f"修改定时 {task} 任务成功")
