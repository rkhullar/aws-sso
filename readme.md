## AWS Single Sign On

### Example Usage
``` sh
$ pip install aws-sso
$ aws-sso site add --domain example.com --username {your_name}
$ aws-sso discover --domain example.com --skip-names
$ aws-sso login --domain example.com
```

``` sh
$ pip install awscli
$ cd path/to/project
$ echo "export AWS_PROFILE=sbx" > .envrc
$ direnv allow
$ aws s3 ls
```

### Code Quality
Run the following commands to analyze the project with sonar.
``` sh
docker run -d --name sonarqube -p 9000:9000 sonarqube
nosetests --with-xunit --with-coverage --cover-xml
sonar-scanner -D project.settings=cicd/sonar-project.properties
```

### Links
- [blog][blog]
- [code][code]

[blog]: https://aws.amazon.com/premiumsupport/knowledge-center/adfs-grant-ad-access-api-cli/
[code]: https://awsiammedia.s3.amazonaws.com/public/sample/SAMLAPICLIADFS/0192721658_1562696757_blogversion_samlapi_python3.py
