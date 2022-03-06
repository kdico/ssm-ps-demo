# ssm-ps-demo

This repository is part of
a [Medium article](https://blog.gecogeco.com/an-alternative-to-environment-variables-in-aws-lambda) showing a
rudimentary example demonstrating how developers can make use
of [AWS Systems Manager Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html)
with AWS Lambda (Python 3.9). This includes two handlers meant to be deployed in AWS Lambda.

## Requirements

* Python 3.9
* [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* Access to consoles for AWS Lambda, IAM, and Systems Manager Parameter Store.
* [Poetry](https://python-poetry.org/)

## Development

Install the project from the root.

```
# If you don't have Poetry globally installed yet.
python3 -m pip install poetry
poetry config virtualenvs.in-project true --local

# Install the project.
poetry install .
```

This should install any dependency, including `boto3`. If you're not familiar with Poetry, head on to
their [website](https://python-poetry.org/). To view dependencies, see `pyproject.toml`.

### Linting

This project uses [`black`](https://pypi.org/project/black/) and [`isort`](https://pypi.org/project/isort/) for linting.
Run them as below.

```
poetry run black ./ssm_ps_demo
poetry run isort ./ssm_ps_demo
```

## AWS

The packaging and deployment process should be the same if the project had dependencies or if it were to be deployed as
an AWS Lambda layer.

### Packaging

Install the project for AWS Lambda deployment from the root. This will create the deployment package
as `package/ssm-ps-demo.zip`.

```
# Install the project to ./.install/.
pip3 install --target ./package .

# Archive the installation for deployment.
(cd ./package/ && zip -rm ssm-ps-demo.zip .)
```

Below is the shape of the deployment package.

```
ssm-ps-demo.zip
├── ssm_ps_demo
│         ├── __init__.py
│         ├── __pycache__
│         │         ├── __init__.cpython-39.pyc
│         │         ├── consumer.cpython-39.pyc
│         │         └── store.cpython-39.pyc
│         ├── consumer.py
│         └── store.py
└── ssm_ps_demo-0.1.0.dist-info
    ├── INSTALLER
    ├── LICENSE
    ├── METADATA
    ├── RECORD
    ├── REQUESTED
    ├── WHEEL
    └── direct_url.json
```

### Deployment

Upload the `ssm-ps-demo.zip` archive to your AWS Lambda function.
See [Deploy your .zip file to the function](https://docs.aws.amazon.com/lambda/latest/dg/python-package.html#python-package-upload-code)
.

When deploying the project to Lambda, you'll have to update the function handlers and environment variables. You can
find the design in the [medium article](https://blog.gecogeco.com/an-alternative-to-environment-variables-in-aws-lambda)
.

| Path                      | Handler                      | Environment Variable | Value                          | IAM Policy                                     |
|---------------------------|------------------------------|----------------------|--------------------------------|------------------------------------------------|
| `ssm_ps_demo/store.py`    | ssm_ps_demo.store.handler    | -                    | -                              | See [Store IAM Policy](#store-function).       |
| `ssm_ps_demo/consumer.py` | ssm_ps_demo.consumer.handler | `STORE_FN_ARN`       | The ARN of the store function. | See [Consumer IAM Policy](#consumer-function). |

#### IAM Policies

On top of the basic execution policies for the deployed functions, they will require additional permissions as below.
Replace the `***` masks with your AWS region and account number respectively.

##### Store Function

IAM policy for the store function.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ssm:DescribeParameters"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ssm:GetParameters"
      ],
      "Resource": "arn:aws:ssm:***:***:parameter/*"
    }
  ]
}
```

##### Consumer Function

IAM policy for the consumer functions.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PermissionToInvoke",
      "Effect": "Allow",
      "Action": "lambda:InvokeFunction",
      "Resource": "arn:aws:lambda:***:***:function:smps-store-fn"
    }
  ]
}
```

### AWS SAM

This project includes templates in the `sam`
directory for use with the AWS SAM CLI. Provide your AWS region and credentials in the `sam/*.yml` files before running
the commands below.

```
# Invoke the store function handler.
sam local invoke --template ./sam/template-store.yml --event ./sam/event.json

# Invoke the consumer function handler.
sam local invoke --template ./template-consumer.yml --no-event
```

## References

* https://blog.gecogeco.com/an-alternative-to-environment-variables-in-aws-lambda
* https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html
* https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html
* https://python-poetry.org/
* https://pypi.org/project/black/
* https://pypi.org/project/isort/
* https://docs.aws.amazon.com/lambda/latest/dg/python-package.html#python-package-upload-code
