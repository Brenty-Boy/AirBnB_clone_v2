#!/usr/bin/python3
"""
Fabric script to deploy web_static content to multiple servers.
"""

from fabric.api import env, local, put, run
from datetime import datetime
import os

# Set the environment
env.hosts = ['54.237.15.59', '52.3.249.72']
env.user = 'ubuntu'
env.key_filename = "~/.ssh/id_rsa"


def do_pack():
    """
    Create a compressed archive of web_static contents.
    Returns path of the created archive, or None if failed.
    """
    try:
        now = datetime.now().strftime('%Y%m%d%H%M%S')
        archive_path = 'versions/web_static_{}.tgz'.format(now)
        local('mkdir -p versions')
        local('tar -cvzf {} web_static'.format(archive_path))
        print('web_static packed: {} -> {}Bytes'.format(
            archive_path, os.path.getsize(archive_path)))
        return archive_path
    except Exception as e:
        print(e)
        return None


def do_deploy(archive_path):
    """
    Distribute an archive to the web servers and deploy it.
    """
    if not archive_path or not os.path.exists(archive_path):
        return False

    try:
        # Upload archive to /tmp/ on the remote server
        put(archive_path, '/tmp/')

        # Extract archive to /data/web_static/releases/<archive_name>/
        archive_filename = os.path.basename(archive_path).split('.')[0]
        release_path =
        '/data/web_static/releases/{}/'.format(archive_filename)
        run('mkdir -p {}'.format(release_path))
        run('tar -xzf /tmp/{}.tgz -C {}'.format(
            archive_filename, release_path))

        # Remove uploaded archive from /tmp/
        run('rm /tmp/{}.tgz'.format(archive_filename))

        # Move contents to the proper location
        run('mv {}web_static/* {}'.format(release_path, release_path))

        # Delete the now-empty web_static directory
        run('rm -rf {}web_static'.format(release_path))

        # Create symbolic link
        current_path = '/data/web_static/current'
        run('rm -rf {}'.format(current_path))
        run('ln -s {} {}'.format(release_path, current_path))

        print('New version deployed!')
        return True
    except Exception as e:
        print(e)
        return False


def deploy():
    """
    Deploy web_static content to web servers.
    """
    # Create archive and get archive path
    archive_path = do_pack()
    if not archive_path:
        return False

    # Deploy the created archive
    if not do_deploy(archive_path):
        return False

    return True
