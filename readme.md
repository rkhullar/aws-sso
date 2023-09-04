## AWS Single Sign On

## Deprecation Notice
If your AWS organization has been configured with Identity Center you should use the `aws sso` command that's
included in the AWS cli. After going through the configuration step your `~/.aws/config` might look like the following,
where `example` refers to the name of your company or organization. You can define multiple AWS profiles linked to
one sso session.

```text
[sso-session example]
sso_start_url = https://example.awsapps.com/start
sso_region = us-east-1

[profile example-stage-admin]
sso_session = example
sso_account_id = REDACTED
sso_role_name = AdministratorAccess
region = us-east-1
output = json
```

The `aws sso configure` and `aws sso login` actions attempt to open your default web browser and initiate the login process
for your AWS org. For more information see their official documentation:
- https://docs.aws.amazon.com/cli/latest/userguide/sso-configure-profile-token.html


### Example Usage
```shell
pip install aws-sso
aws-sso site add --domain example.com --username {your_name}
aws-sso discover --domain example.com --skip-names
aws-sso login --domain example.com
```

```shell
pip install awscli
cd path/to/project
echo "export AWS_PROFILE=sbx" > .envrc
direnv allow
aws s3 ls
```

### Code Quality
Run the following commands to analyze the project with sonar.
```shell
docker run -d --name sonarqube -p 9000:9000 sonarqube
nosetests --with-xunit --with-coverage --cover-xml
sonar-scanner -D project.settings=cicd/sonar-project.properties
```

### Links
- [blog][blog]
- [code][code]

[blog]: https://aws.amazon.com/premiumsupport/knowledge-center/adfs-grant-ad-access-api-cli/
[code]: https://awsiammedia.s3.amazonaws.com/public/sample/SAMLAPICLIADFS/0192721658_1562696757_blogversion_samlapi_python3.py
