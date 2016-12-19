# user script:
apt-get install -y python python-pip python-dev build-essential

pip install --upgrade pip

# startup script:
#!/bin/bash
DIR=/home/ubuntu
APP_DIR=/home/ubuntu/analyticsService
LOG_DIR=/home/ubuntu/logs
NODE=/usr/bin/node

if [ `pgrep python` ]; then
    python_process_id=$(pidof python)
    kill $python_process_id
    echo "Killed Python Process"
fi

aws s3 cp s3://ms-codedeploy/authorized_keys /home/ubuntu/.ssh/authorized_keys --region us-west-2

# Make sure the keys have the correct permissions
chown ubuntu:ubuntu /home/ubuntu/.ssh/authorized_keys
chmod 600 /home/ubuntu/.ssh/authorized_keys

# Change ownership of repo
chown -R ubuntu:ubuntu $APP_DIR

pip install virtualenv

cd $APP_DIR
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt

cd $DIR
git clone git@github.com:metricstory/config.git
chown -R ubuntu:ubuntu $DIR/config

cd $DIR
chown -R ubuntu:ubuntu $DIR

cd $APP_DIR
python iWorker.py &

exit 0
