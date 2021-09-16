import subprocess
import os
import logging
from logging.handlers import TimedRotatingFileHandler

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logname = "automate.log"
handler = TimedRotatingFileHandler(logname, when="midnight", interval=1)
handler.suffix = "%Y-%m-%d"
logger.addHandler(handler)

GIT_CMD = r'git clone {} {}'
REMOVE_DIR_CMD = r'rm -rf {}'
MKDIR_CMD = r'mkdir -p {}'




def clone_repo(repo_url, target_dir):
    status = False

    # rm_cmd = REMOVE_DIR_CMD.format(target_dir)
    # os.system(rm_cmd)
    mkdir_cmd = MKDIR_CMD.format(target_dir)
    os.system(mkdir_cmd)
    git_cmd = GIT_CMD.format(repo_url, target_dir)
    print(git_cmd, 'clone')
    logger.info("git clone completed in this path {}".format(target_dir))

    p = subprocess.Popen(git_cmd, shell=True, cwd=target_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    status = True
    return status, out, err
