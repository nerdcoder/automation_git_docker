import subprocess
import logging
from logging.handlers import TimedRotatingFileHandler

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logname = "automate.log"
handler = TimedRotatingFileHandler(logname, when="midnight", interval=1)
handler.suffix = "%Y-%m-%d"
logger.addHandler(handler)


DOCKER_BUILD_CMD = r'docker build . -t {}'
DOCKER_RUN_CMD = r'docker run --name {} -p{}:{} -d {}:{}'
DOCKER_STOP_CMD = r'docker stop {}'
DOCKER_RM_CMD = r'docker rm {}'
DOCKER_RMI_CMD = r'docker rmi {}'


def build_image(image, source_dir):
    status = False

    # Remove existing image
    docker_cmd = DOCKER_RMI_CMD.format(image)
    print('Removing old image : \n{}'.format(docker_cmd))
    logger.info("Removing old image {}".format(docker_cmd))

    p = subprocess.Popen(docker_cmd, shell=True, cwd=source_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()

    # Create new image
    docker_build_cmd = DOCKER_BUILD_CMD.format(image)
    print('Creating new image : \n{}'.format(docker_build_cmd))
    logger.info("Creating new image {}".format(docker_build_cmd))

    p = subprocess.Popen(docker_build_cmd, shell=True, cwd=source_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    status = True
    return status, out, err


def deploy(image, tag, local_port, external_port):
    status = False

    # Stop existing container

    docker_cmd = DOCKER_STOP_CMD.format(image)
    print('Stopping existing container : \n{}'.format(docker_cmd))
    execute_docker_cmd(docker_cmd=docker_cmd)
    logger.info("Stopping existing container {}".format(docker_cmd))


    # Remove existing container
    docker_cmd = DOCKER_RM_CMD.format(image)
    print('Removing existing container : \n{}'.format(docker_cmd))
    execute_docker_cmd(docker_cmd=docker_cmd)
    logger.info("Removing existing container {}".format(docker_cmd))

    # Start new container
    docker_cmd = DOCKER_RUN_CMD.format(image, external_port, local_port, image, tag)

    print('Starting new container : \n{}'.format(docker_cmd))
    p = subprocess.Popen(docker_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()

    status = True
    return status, out, err


def execute_docker_cmd(docker_cmd='docker images'):

    p = subprocess.Popen(docker_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    print(out)
    logger.info("container executed {}".format(out))



