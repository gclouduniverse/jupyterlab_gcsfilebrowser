INSTANCE_NAME=${1?}

rm -rf dist
python setup.py sdist

ARCHIVE="$(ls dist)"

gcloud compute scp "dist/${ARCHIVE?}" "jupyter@${INSTANCE_NAME?}:/home/jupyter"
gcloud compute ssh "jupyter@${INSTANCE_NAME?}" -- \
       "sudo pip3 install ${ARCHIVE?} && \
        sudo su -p -l root -c '/opt/conda/bin/jupyter lab build' && \
        sudo service jupyter restart"

