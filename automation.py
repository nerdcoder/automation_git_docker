
import yaml
import argparse

from utils import git_utils
from utils import docker_utils

import logging
from logging.handlers import TimedRotatingFileHandler

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logname = "automate.log"
handler = TimedRotatingFileHandler(logname, when="midnight", interval=1)
handler.suffix = "%Y-%m-%d"
logger.addHandler(handler)


def parse_build_yaml():
    yaml_args = dict()

    build_ymal = open("build.yaml")
    logger.info("Opening build yaml file")

    deploy_obj = yaml.load(build_ymal, Loader=yaml.FullLoader)
    artifact = deploy_obj.get('artifact', '')

    if not artifact:
        raise Exception('Artifact details not found in build.yaml')

    artifact_name = artifact.get('name', '')
    repo_url = artifact.get('repo', '')
    branch = artifact.get('branch', 'main')
    version = artifact.get('version', 'latest')

    if not repo_url:
        logging.error("Repo url not found in build.yaml")
        raise Exception('Repo url not found in build.yaml')

    build_info = deploy_obj.get('build', '')
    synced_path = build_info.get('directory', '')

    docker_image_tag = '{}_{}'.format(branch, version)

    yaml_args['artifact_name'] = artifact_name
    yaml_args['repo_url'] = repo_url
    yaml_args['branch'] = branch
    yaml_args['version'] = version
    yaml_args['synced_path'] = synced_path

    yaml_args['docker_image_tag'] = docker_image_tag

    deploy = deploy_obj.get('deploy', '')
    container_port = deploy.get('port', 8000)
    external_port = deploy.get('external', 80)

    yaml_args['container_port'] = container_port
    yaml_args['external_port'] = external_port

    return yaml_args


def build(deploy_args):
    try:
        # Clone the repo from git
        status, out, err = git_utils.clone_repo(deploy_args['repo_url'], deploy_args['synced_path'])
        if not status:
            logging.error('Failed to clone the repo from git : \n{}'.format(err))

            raise Exception('Failed to clone the repo from git : \n{}'.format(err))
        print(out)
        logger.info('After git process completed - {}'.format(out))
        # Build docker image
        docker_image = '{}:{}'.format(deploy_args['artifact_name'], deploy_args['docker_image_tag'])
        status, out, err = docker_utils.build_image(image=docker_image,
                                                    source_dir=deploy_args['synced_path'])
        if not status:
            raise Exception('Failed to build docker images : {}\n'.format(err))

        print(out)
        logger.info('After docker build image - {}'.format(out))

    except Exception as ex:
        print(ex)
        logger.exception('Exception - {}'.format(ex))


def deploy(deploy_args):
    try:
        # Run docker container

        status, out, err = docker_utils.deploy(image=deploy_args['artifact_name'],
                                               tag=deploy_args['docker_image_tag'],
                                               local_port=deploy_args['container_port'],
                                               external_port=deploy_args['external_port'])
        if not status:
            logging.error('status invalid - {}'.format(status))
            raise Exception('Failed to start docker container : {}'.format(err))
        logger.info('Deploying - {}'.format(out))

        print(out)

    except Exception as ex:
        print(str(ex))
        logger.exception('Exception - {}'.format(ex))


if __name__=="__main__":
    parser = argparse.ArgumentParser()

    # Add the arguments to the parser
    parser.add_argument("-a", "--action", required=False, help="Build action")
    args = vars(parser.parse_args())

    deploy_args = parse_build_yaml()
    print(deploy_args)

    if args['action'] == 'build':
        build(deploy_args)

    if args['action'] == 'deploy':
        deploy(deploy_args)
