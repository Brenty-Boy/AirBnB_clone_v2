#!/usr/bin/python3
"""
Fabric script to deploy web_static content to multiple servers.
"""
from fabric.api import env, local, put, run
from os.path import exists
from datetime import datetime

# Set the environment
env.hosts = ['54.237.15.59', '52.3.249.72']
env.user = 'ubuntu'
env.key_filename = "~/.ssh/id_rsa"


def do_pack():
    """
    Create a compressed archive of web_static contents.
    Returns path of the created archive, or None if failed.
    """
    now = datetime.now().strftime('%Y%m%d%H%M%S')
    archive_path = 'versions/web_static_{}.tgz'.format(now)
    local('mkdir -p versions')
    result = local('tar -cvzf {} web_static'.format(archive_path))
    if result.failed:
        return None
    return archive_path


def do_deploy(archive_path):
    """
    Distribute an archive to the web servers and deploy it.
    """
    if not exists(archive_path):
        return False

    try:
        # Upload archive to /tmp/ on the remote server
        put(archive_path, '/tmp/')

        # Extract archive to /data/web_static/releases/<archive_name>/
        archive_filename = archive_path.split('/')[-1].split('.')[0]
        run('mkdir -p /data/web_static/releases/{}/'.format(archive_filename))
        run('tar -xzf /tmp/{}.tgz -C /data/web_static/releases/{}/'
            .format(archive_filename, archive_filename))

        # Remove uploaded archive from /tmp/
        run('rm /tmp/{}.tgz'.format(archive_filename))

        # Move contents to the proper location and create symlink
        run('mv /data/web_static/releases/{}/web_static/* '
            '/data/web_static/releases/{}/'
            .format(archive_filename, archive_filename))
        run('rm -rf /data/web_static/releases/{}/web_static'
            .format(archive_filename))
        run('rm -rf /data/web_static/current')
        run('ln -s /data/web_static/releases/{}/ /data/web_static/current'
            .format(archive_filename))

        print('New version deployed!')
        return True
    except:
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
