from seeq import spy, sdk
from packaging import version
from pathlib import Path
import os

from getpass import getpass
from urllib.parse import urlparse, urlunparse
import re

__all__ = ('install_addon',)

DATA_LAB_PROJECT_ID_REGEX = r'.*/data-lab/([0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}).*'

def copy_and_paste_notebook():
    _dir = Path(__file__).resolve().parent

    with open(os.path.join(_dir, '_notebook.ipynb'), 'rb') as f:
        lines = f.readlines()

    with open(os.path.join(os.getcwd(), 'App.ipynb'), 'wb') as f:
        f.writelines(lines)

    return


def get_tools_api_name():
    server_version = version.parse(spy.server_version)
    if server_version > version.parse(f"R{spy.__version__}"):
        raise RuntimeError(f"The SPy module version doesn't match the Seeq server version. "
                           f"Please update the SPy module to version ~={spy.server_version.split('-')[0]}")

    if server_version < version.parse('R52.1.5'):
        return 'external'
    elif version.parse('R52.1.5') <= server_version < version.parse('R53'):
        return 'add_on'
    elif version.parse('R53') <= server_version < version.parse('R53.0.2'):
        return 'external'
    elif server_version >= version.parse('R53.0.2'):
        return 'add_on'
                           
def permissions_defaults(permissions_group: list, permissions_users: list):
    if permissions_group is None:
        permissions_group = ['Everyone']

    if permissions_users is None:
        permissions_users = []
    return permissions_group, permissions_users
                           
def get_user_group(group_name, user_groups_api):
    try:
        group = user_groups_api.get_user_groups(name_search=group_name)
        assert len(group.items) != 0, 'No group named "%s" was found' % group_name
        assert len(group.items) == 1, 'More that one group named "%s" was found' % group_name
        return group
    except AssertionError as error:
        print_red(error)
    except ApiException as error:
        print_red(error.body)


def get_user(user_name, users_api):
    try:
        user_ = users_api.get_users(username_search=user_name)
        if len(user_.users) == 0:
            raise ValueError(f'No user named {user_name} was found')
        if len(user_.users) > 1:
            raise ValueError(f'More than one user named {user_name} was found')
        return user_
    except AssertionError as error:
        print_red(error)
    except ApiException as error:
        print_red(error.body)
                           
def add_datalab_project_ace(data_lab_project_id, ace_input, items_api):
    if data_lab_project_id:
        try:
            items_api.add_access_control_entry(id=data_lab_project_id, body=ace_input)
        except Exception as error:
            print_red(error.body)

def get_tool_config(app_url, sort_key=None, permissions_group: list = None, permissions_users: list = None):
    """
    Return a configuration dict for the Clustering Addon tool.

    Parameters
    ----------
    sort_key: str, default None
        A string, typically one character letter. The sort_key determines the
        order in which the Add-on Tools are displayed in the tool panel
    permissions_group: list
        Names of the Seeq groups that will have access to each tool
    permissions_users: list
        Names of Seeq users that will have access to each tool
    
    Returns 
    --------
    -: Dict
        Dictionary used for specifying addon tool.

    """

    permissions_group, permissions_users = permissions_defaults(permissions_group, permissions_users)

    if sort_key is None:
        sort_key = 'a'

    my_tool_config = dict(
        name='Clustering',
        description="Density based clustering tool.",
        iconClass="fa fa-object-group",
        targetUrl='{}?workbookId={{workbookId}}&worksheetId={{worksheetId}}'.format(app_url),
        linkType="window",
        windowDetails="toolbar=0,location=0,left=800,top=400,height=1000,width=1400",
        sortKey=sort_key,
        reuseWindow=True,
        permissions=dict(groups=permissions_group,
                         users=permissions_users)
    )
    return my_tool_config

def sanitize_app_url(url):
    if 'notebooks' in url:
        return url.replace('notebooks', 'apps')
    if 'apps' not in url:
        raise ValueError('app_url is malformed.')

def sanitize_sdl_url(url):
    parsed = urlparse(url)
    project_id_search = re.search(DATA_LAB_PROJECT_ID_REGEX, url, re.IGNORECASE)
    if parsed.scheme == '' or parsed.netloc == '' or parsed.path == '':
        raise ValueError(f"The SDL_url should have the format "
                         f"https://my.seeq.com/data-lab/6AB49411-917E-44CC-BA19-5EE0F903100C/ but got {url}")
    if project_id_search is None:
        raise ValueError(f"Invalid URL. Could not find data-lab project ID. Got URL: {url}")
    id = project_id_search.group(1)
    return urlunparse(parsed).strip(" ").split(id)[0] + id


def install_addon(*, seeq_url: str = None, app_url: str = None, sort_key=None, 
    permissions_group: list = None, permissions_users: list = None, username=None, 
    password=None, ignore_ssl_errors=True):
    """
    Install as an Add-on Tool in Seeq Workbench

    Parameters
    ----------
    seeq_url: str
        URL of the Seeq Server.
        E.g. https://my.seeq.com/
    app_url: str
        URL of Clustering App Jupyter Notebook. 
        E.g. https://my.seeq.com/data-lab/CBA9A827-35A8-4944-8A74-EE7008DC3ED8/notebooks/hb/seeq/addons/clustering/App.ipynb
    sort_key: str, default None
        A string, typically one character letter. The sort_key determines the
        order in which the Add-on Tools are displayed in the tool panel
    permissions_group: list
        Names of the Seeq groups that will have access to each tool
    permissions_users: list
        Names of Seeq users that will have access to each tool
    username: str
        Username or access key to login to the Seeq Server where the addon tool will be installed
    password: str
        Password to login to the Seeq Server where the addon tool will be installed
    Returns
    --------
    -: None
        Correlation will appear as Add-on Tool(s) in Seeq
        Workbench
    """
    if spy.client == None:
        if username is None:
            username = input("Username or Access Key: ")
        if password is None:
            password = getpass("Password: ")
        spy.login(username=username, password=password, ignore_ssl_errors=ignore_ssl_errors)

    if seeq_url is None:
        seeq_url = input(f"\n Enter Seeq base URL for [{spy.client.host.split('/api')[0]}] (e.g. https://my.seeq.com/): ")
        if seeq_url == '':
            seeq_url = spy.client.host.split('/api')[0]
    url_parsed = urlparse(seeq_url)
    seeq_url_base = f"{url_parsed.scheme}://{url_parsed.netloc}"

    project_id = spy.utils.get_data_lab_project_id()
    sdl_url = f'{seeq_url_base}/data-lab/{project_id}'
    sdl_url = sanitize_sdl_url(sdl_url)
    app_url = os.path.join(os.path.join(sdl_url, 'notebooks'), 'App.ipynb')

    system_api = sdk.SystemApi(spy.client)
    users_api = sdk.UsersApi(spy.client)
    user_groups_api = sdk.UserGroupsApi(spy.client)
    items_api = sdk.ItemsApi(spy.client)

    tools_api_name = get_tools_api_name()
    if tools_api_name == 'external':
        tools = system_api.get_external_tools().external_tools
    elif tools_api_name == 'add_on':
        # TODO: Needs updated API call once the SDK is released
        tools = system_api.get_add_on_tools().add_on_tools

    #get existing tools
    tools_config = list()
    for tool in tools:
        tools_config.append({
            "name": tool.name,
            "description": tool.description,
            "iconClass": tool.icon_class,
            "targetUrl": tool.target_url,
            "linkType": tool.link_type,
            "windowDetails": tool.window_details,
            "sortKey": tool.sort_key,
            "reuseWindow": tool.reuse_window,
            "permissions": {
                "groups": list(),
                "users": list()
            }
        })
        tool_acl = items_api.get_access_control(id=tool.id)
        for ace in tool_acl.entries:
            identity = ace.identity
            if identity.type.lower() == "user":
                tools_config[-1]["permissions"]["users"].append(identity.username)
            elif identity.type.lower() == "usergroup":
                tools_config[-1]["permissions"]["groups"].append(identity.name)

    #get config of tool to add or update:
    app_url = sanitize_app_url(app_url)
    my_tool_config = get_tool_config(app_url, sort_key=sort_key, permissions_group=permissions_group, permissions_users=permissions_users)

    # If the tool is in the list, update it
    if my_tool_config["name"] in [t["name"] for t in tools_config]:
        list_index = [t["name"] for t in tools_config].index(my_tool_config["name"])
        tools_config[list_index].update(my_tool_config)
    # if the tool is not in the list, add it
    else:
        tools_config.append(my_tool_config)

    # Delete all existing add-on tools (only deletes the tools, not what they point to)
    for tool in tools:
        if tools_api_name == 'external':
            system_api.delete_external_tool(id=tool.id)
        elif tools_api_name == 'add_on':
            # TODO: Needs updated API call once the SDK is released
            system_api.delete_add_on_tool(id=tool.id)

    # Add add-on tools and assign add-on tool and data lab permissions to groups and users

    for tool_with_permissions in tools_config:
        # Create add-on tool
        tool = tool_with_permissions.copy()
        tool.pop("permissions")
        if tools_api_name == 'external':
            tool_id = system_api.create_external_tool(body=tool).id
        elif tools_api_name == 'add_on':
            # TODO: Needs updated API call once the SDK is released
            tool_id = system_api.create_add_on_tool(body=tool).id
        else:
            tool_id = None

        print(tool["name"])
        print(f'Add-on Tool ID - {tool_id}')
        
        ###data_lab_project_id = get_datalab_project_id(tool["targetUrl"], items_api)
        ###if data_lab_project_id:
        ###    print("Target Data Lab Project ID - %s" % data_lab_project_id)
        ###else:
        ###    print("TargetUrl does not reference a Data Lab project")

        # assign group permissions to add-on tool and data lab project
        groups = tool_with_permissions["permissions"]["groups"]
        for group_name in groups:
            group = get_user_group(group_name, user_groups_api)
            if group:
                ace_input = {'identityId': group.items[0].id, 'permissions': {'read': True}}
                # Add permissions to add-on tool item
                items_api.add_access_control_entry(id=tool_id, body=ace_input)
                # Add permissions to data lab project if target URL references one
                ace_input['permissions']['write'] = True  # Data lab project also needs write permission
                ###add_datalab_project_ace(data_lab_project_id, ace_input, items_api)
        print("Groups:", end=" "), print(*groups, sep=", ")

        # assign user permissions to add-on tool and data lab project
        users = tool_with_permissions["permissions"]["users"]
        for user_name in users:
            user = get_user(user_name, users_api)
            if user:
                ace_input = {'identityId': user.users[0].id, 'permissions': {'read': True}}
                items_api.add_access_control_entry(id=tool_id, body=ace_input)
                # Add permissions to data lab project if target URL references one
                ace_input['permissions']['write'] = True  # Data lab project also needs write permission
                ###add_datalab_project_ace(data_lab_project_id, ace_input, items_api)
        print("Users:", end=" "), print(*users, sep=", ")

    copy_and_paste_notebook()
    return