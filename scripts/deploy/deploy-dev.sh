#ssh into amazon s3 instance
ssh -i ~/.ssh/transients-keypair.pem ec2-user@52.11.202.99 << EOF

cd transients/dev/transients-server/ 

git fetch --all

git checkout -b development origin/development

git pull 

supervisorctl restart transients

EOF
