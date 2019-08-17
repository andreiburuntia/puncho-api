## AWS specifics:

- public DNS: 
    > ec2-13-58-252-233.us-east-2.compute.amazonaws.com

- host OS: Amazon Linux 2 AMI 2.0.20190618 x86_64 HVM gp2

- instance type: t2.medium (burstable performance instance with baseline level of CPU performance and the the ability to burst above baseline):
    
    - 2 vCPUs

    - 36 CPU credits / hour

    - 8 gigs of memory

- SSH access is available via the keypair1.pem file:
    > ssh -i "keypair1.pem" ec2-user@ec2-13-58-252-233.us-east-2.compute.amazonaws.com
    
- ec2-user user is in the sudoers file and its privilleges can be elevated to root

- VPC and security group configuration:

    - launch-wizard-1 security group

    - vpc-e6150d8e VPC -> this is required to be able to access the RDS instance

- region: us-east-2c -> RDS instance is hosted on us-east-2; it is mandatory that both EC2 and RDS instances are on the same availability zone due performance constraints

## Environment setup for webserver machine

- aside from the pre-installed packages, the following packages have been installed by means of yum:

    - python3
    - mysql
    - git
    - python3-devel
    - gcc
    - mysql-devel

- after installing python3, the list of pip3 installed packages should look like this:

        Package         Version
        -------------- -------
        Click           7.0    
        Flask           1.1.1  
        Flask-MySQLdb   0.2.0  
        itsdangerous    1.1.0  
        Jinja2          2.10.1 
        MarkupSafe      1.1.1  
        mysql-connector 2.2.9  
        mysqlclient     1.4.4  
        pip             9.0.3  
        protobuf        3.9.1  
        setuptools      41.0.1 
        six             1.12.0 
        Werkzeug        0.15.5 

