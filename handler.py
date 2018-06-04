import os
import shutil
from zipfile import ZipFile
from boto3 import client
from pygit2 import clone_repository

# Retain the .git folder in the artifact
EXCLUDE_GIT = False

s3 = client('s3')

def zip_repo(repo_path, repo_name):
    zf = ZipFile('/tmp/'+repo_name.replace('/', '_')+'.zip', 'w')
    for dirname, subdirs, files in os.walk(repo_path):
        if EXCLUDE_GIT:
            try:
                subdirs.remove('.git')
            except ValueError:
                pass
        zdirname = dirname[len(repo_path)+1:]
        zf.write(dirname, zdirname)
        for filename in files:
            zf.write(os.path.join(dirname, filename), os.path.join(zdirname, filename))
    zf.close()
    return '/tmp/'+repo_name.replace('/', '_')+'.zip'


def push_s3(filename, repo_name, outputbucket):
    s3key = '%s/%s' % (repo_name, filename.replace('/tmp/', ''))
    data = open(filename, 'rb')
    s3.put_object(Bucket=outputbucket, Body=data, Key=s3key)


def lambda_handler(event, context):
    outputbucket = event['context']['output-bucket']
    repo_url = event['body-json']['repository']['clone_url']
    full_name = event['body-json']['repository']['full_name']
    repo_branch = event['body-json']['ref'].replace('refs/heads/', '')

    repo_path = '/tmp/%s' % full_name

    clone_repository(repo_url, repo_path, checkout_branch=repo_branch)
    zipfile = zip_repo(repo_path, full_name)
    push_s3(zipfile, full_name, outputbucket)

    shutil.rmtree(repo_path)
    os.remove(zipfile)

    return 'Successfully updated %s' % full_name

