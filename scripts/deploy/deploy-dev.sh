#ssh into amazon s3 instance
# OLD: ssh -i ~/.ssh/transients-keypair.pem ec2-user@52.11.202.99 << EOF
ssh -i ~/.ssh/transients_key_pair.pem ec2-user@ec2-52-11-57-55.us-west-2.compute.amazonaws.com << EOF

cd transients/dev/transients-server/ 

git fetch --all

git checkout -b development origin/development

git pull 

cd /home/ec2-user/supervisor

supervisorctl restart transients

EOF
