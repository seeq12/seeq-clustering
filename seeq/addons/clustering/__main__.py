import os
import sys
import argparse

from ._install_addon import install_addon


def cli_interface():
    """ Installs Seeq Add-on Tool """
    parser = argparse.ArgumentParser(description='Install Clustering as a Seeq Add-on Tool')
    parser.add_argument('--username', type=str, default=None,
                        help='Username or Access Key of Seeq admin user installing the tool(s) ')
    parser.add_argument('--seeq_url', type=str,
                        help="Seeq hostname URL with the format https://my.seeq.com/ or https://my.seeq.com:34216")
    parser.add_argument('--app_url', type=str,
                        help="URL of clustering app notebook with the format e.g. https://my.seeq.com/data-lab/CBA9A827-35A8-4944-8A74-EE7008DC3ED8/notebooks/hb/seeq/addons/clustering/App.ipynb")
    parser.add_argument('--users', type=str, nargs='*', default=[],
                        help="List of the Seeq users to will have access to the Correlation Add-on Tool,"
                             " default: %(default)s")
    parser.add_argument('--groups', type=str, nargs='*', default=['Everyone'],
                        help="List of the Seeq groups to will have access to the Correlation Add-on Tool, "
                             "default: %(default)s")
    parser.add_argument('--password', type=str, default=None,
                        help="Password of Seeq user installing the tool. Must supply a password if not supplying an accesskey for username")
    parser.add_argument('--sort_key', type=str, default=None,
                        help="A string, typically one character letter. The sort_key determines the order in which the Add-on Tools are displayed in the tool panel, "
                        "default: %(default)s")
    return parser.parse_args()


if __name__ == '__main__':

    args = cli_interface()

    install_addon(
        sort_key=args.sort_key, 
        permissions_group=args.groups, 
        permissions_users=args.users, 
        username=args.username, 
        password=args.password
    )