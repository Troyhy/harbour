import os
from os.path import normpath, dirname, basename

from fabric.api import *
from fabric.contrib.project import rsync_project
from fabric.contrib import console
from fabric import utils
from fabric.colors import red, green


PROJECT_FOLDER = basename(normpath(dirname(__file__)))
PRODUCTION_SERVER = 'pro.designhouseilo.fi'
STAGING_SERVER = 'sta.designhouseilo.fi'

NGINX_DATA_DIR = '/srv/harbour/nginx-data'
NGINX_HTPASSWD = os.path.join(NGINX_DATA_DIR, 'htpasswd')

VALID_HOSTS = ('staging',
               'production', )

env.home = '/srv/'
env.docker_group = 'docker_adm'
env.project = PROJECT_FOLDER

SSH_USERNAME = None
if not SSH_USERNAME:
    import getpass
    SSH_USERNAME = getpass.getuser()


env.RSYNC_EXCLUDE = [
    '.DS_Store',
    '.hg',
    '*.pyc',
    '*.py.ex',
    '*.example',
    'elastic-data/data/*',
    'elastic-data/log/*',
]


def _setup_path():
    # /srv/
    env.root = env.home
    # local directory where this file is
    env.local_path = os.path.dirname(__file__)
    # project directory
    env.project_root = os.path.join(env.root, env.project)


def install_requirements(host_string):
    """Install docker & docker-compose to host"""
    with settings(host_string=host_string):
        # Update
        with hide('output'):
            sudo('apt-get update')
        # Make sure curl is installed
        sudo('apt-get install -y curl')
        # Docker
        sudo('curl -sSL https://get.docker.com/ | sh')
        # Docker-compose
        sudo('curl -L https://github.com/docker/compose/releases/download/'
             '1.1.0/docker-compose-`uname -s`-`uname -m` > '
             '/usr/local/bin/docker-compose')
        sudo('chmod +x /usr/local/bin/docker-compose')


def sync(host_string):
    """Sync project to host"""
    # sync opts for rsync
    extra_opts = '--omit-dir-times --chmod=u+rw -L --chmod=o-rw'

    # Run commands on host...
    with settings(host_string=host_string):
        # dir
        sudo('mkdir -p %(root)s' % env)
        sudo('mkdir -p %(project_root)s' % env)
        sudo('chown -R %(user)s:%(docker_group)s %(project_root)s' % env)
        sudo('chmod -R g+rw %s' % env.project_root)

        # sync
        print(red("rsync starting"))
        rsync_project(
            local_dir=env.local_path,
            remote_dir=env.root,
            exclude=env.RSYNC_EXCLUDE,
            #delete=True,
            extra_opts=extra_opts,
        )


        sudo('chown -R %(user)s:%(docker_group)s %(project_root)s' % env)
        sudo('chmod -R o+r %s' % env.project_root)

        # htpasswd permissions...
        sudo('chmod -R 777 %s' % NGINX_HTPASSWD)



def build_container(host_string):
    # Run commands on host...
    with settings(host_string=host_string):
        # cd to project
        with cd(env.project_root):
            print(green('Start building container on %s:%s' %
                        (host_string, env.project_root)))
            with settings(warn_only=True):
                build = sudo('docker-compose build')
            if build.failed:
                print(red('Build failed on %s:%s' %
                          (host_string, env.project_root)))
                utils.abort('Failed to build on %s' % env.environment)
            print(green('Build successful'))


def create_es_template(host_string):
    # Run commands on host...
    with settings(host_string=host_string):
        # cd to project
        with cd(env.project_root):
            print(green('Creating ES index template on %s:%s' %
                        (host_string, env.project_root)))
            with settings(warn_only=True):
                sudo('docker-compose stop')
                sudo('docker-compose up -d elasticsearch && sleep 5')
                with cd('bin'):
                    sudo('./make_elastic_template.sh')
                    sudo('./dashboard_load.sh')
                sudo('docker-compose stop')

@task
def container_status(host):
    if host not in VALID_HOSTS:
        utils.abort('Please enter a valid host')

    if host == 'production':
        host_string = PRODUCTION_SERVER
    else:
        host_string = STAGING_SERVER

    _setup_path()
    require('root')

    with settings(host_string=host_string):
        with cd(env.project_root):
            print(green('Info about containers in %s:%s'
                        % (host_string, env.project_root)))
            with settings(warn_only=True):
                r = run('docker-compose ps')
            if r.failed:
                print(red('No containers found on %s:%s'
                          % (host_string, env.project_root)))


def stop_container(host_string):
    # Run commands on host...
    with settings(host_string=host_string):
        # cd to project
        with cd(env.project_root):
            # Ask nicely for container to stop
            with settings(warn_only=True):
                stop = sudo('docker-compose stop')
            # It's not listening! We have to kill it!
            if stop.failed:
                sudo('docker-compose kill')

            print(green('Containers stopped'))


def start_container(host_string):
    # Run commands on host...
    with settings(host_string=host_string):
        # cd to project
        with cd(env.project_root):
            with settings(warn_only=True):
                start = sudo('docker-compose up -d')
            if start.failed:
                print(red('Containers failed to start on %s:%s' %
                          (host_string, env.project_root)))
                utils.abort('Start failed on %s' % env.environment)
            print(green('Containers are running on %s' % env.environment))


@task
def show_version_info(host):
    """Show docker & docker-compose versions installed on :host"""
    if host not in VALID_HOSTS:
        utils.abort('Please enter a valid host')

    if host == 'production':
        host_string = PRODUCTION_SERVER
    else:
        host_string = STAGING_SERVER

    with settings(host_string=host_string):
        with hide('output'):
            d = sudo('docker version')
            f = sudo('docker-compose --version')
        print('==============  DOCKER  ===============')
        print(green('%s' % d))
        print('============ DOCKER-COMPOSE ===========')
        print(green('%s' % f))
        print('=======================================')


@task
def update_harbour(host,
                   ignore_requirements=True,
                   create_index_template=False,
                   **kwargs):
    execute(create_new_harbour, host,
            ignore_requirements=ignore_requirements,
            create_index_template=create_index_template,
            **kwargs)


@task
def create_new_harbour(host,
                       ignore_requirements=False,
                       create_index_template=True, **kwargs):
    """Create a new harbour to :host"""
    if host not in VALID_HOSTS:
        utils.abort('Please enter a valid host')
    env.user = SSH_USERNAME
    env.environment = host
    if host == 'production':
        host_string = PRODUCTION_SERVER
    else:
        host_string = STAGING_SERVER

    _setup_path()
    require('root')
    print(green('Creating a new harbour to %s (%s)' % (host, host_string)))
    if not console.confirm('Continue?',
                           default=False):
                utils.abort('Deployment aborted.')

    # install docker and docker-compose to host machine
    if not ignore_requirements:
        install_requirements(host_string)

    # sync
    sync(host_string)
    # build container
    build_container(host_string)
    if create_index_template:
        create_es_template(host_string)
    # stop container
    stop_container(host_string)
    # start container
    start_container(host_string)
    # show some info...
    show_version_info(host)
    container_status(host)


@task
def container_status(host):
    """Displays container status on :host"""
    if host not in VALID_HOSTS:
        utils.abort('Please enter a valid host')

    env.user = SSH_USERNAME
    env.environment = host
    if host == 'production':
        host_string = PRODUCTION_SERVER
    else:
        host_string = STAGING_SERVER
    _setup_path()

    require('root')
    with settings(host_string=host_string):
        with cd(env.project_root):
            print(green('Info about containers in %s:%s'
                        % (host_string, env.project_root)))
            with settings(warn_only=True):
                r = run('docker-compose ps')
            if r.failed:
                print(red('No containers found on %s:%s'
                          % (host_string, env.project_root)))


@task
def container_stop(host):
    """Stop container on :host"""
    if host not in VALID_HOSTS:
        utils.abort('Please enter a valid host')

    env.user = SSH_USERNAME
    env.environment = host
    if host == 'production':
        host_string = PRODUCTION_SERVER
    else:
        host_string = STAGING_SERVER
    _setup_path()

    require('root')
    stop_container(host_string)


@task
def container_restart(host):
    """Restart container on :host"""
    if host not in VALID_HOSTS:
        utils.abort('Please enter a valid host')

    env.user = SSH_USERNAME
    env.environment = host
    if host == 'production':
        host_string = PRODUCTION_SERVER
    else:
        host_string = STAGING_SERVER
    _setup_path()

    require('root')
    stop_container(host_string)
    start_container(host_string)