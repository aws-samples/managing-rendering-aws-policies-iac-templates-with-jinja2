import ast
import json
# import boto3
from jinja2 import Environment, PackageLoader


class PolicyGen:
    """
    This is a sample to generate AWS IAM policy.
    if you wish to deploy to AWS, Kindly setup your AWS credentials and uncomment boto3 client refernces, if required add additional code for deploying to AWS as per your needs."""

    partition = "aws"

    def __init__(self, region, account_id):
        self.region = region
        self.account_id = account_id
        # self.iam_client = boto3.client('iam')  # Create IAM client
        self.my_managed_policy = {
            "Version": "2012-10-17",
            "Statement": []}

    def render_s3_policy(self, bucket_list, actions, policy_template):
        # create jinja2 template generator
        j2 = Environment(loader=PackageLoader("templates", "."), trim_blocks=True,
                         autoescape=True)
        template = j2.get_template(policy_template)
        # Generate policy
        my_managed_s3_policy = template.render(partition=self.partition, bucket_list=bucket_list,
                                               actions=actions)
        # Create policy
        self.my_managed_policy["Statement"].append(ast.literal_eval(my_managed_s3_policy))

    def render_cw_policy(self, cw_resources, cw_actions, policy_template):
        # create jinja2 template generator
        j2 = Environment(loader=PackageLoader("templates", "."), trim_blocks=True,
                         autoescape=True)
        template = j2.get_template(policy_template)
        # Generate policy
        my_managed_cw_policy = template.render(partition=self.partition, region=self.region, account=self.account_id,
                                               actions=cw_actions, resources=cw_resources)
        # Create policy
        self.my_managed_policy["Statement"].append(ast.literal_eval(my_managed_cw_policy))

    def render_general_policy(self, resources, actions, service, policy_template):
        # create jinja2 template generator
        j2 = Environment(loader=PackageLoader("templates", "."), trim_blocks=True,
                         autoescape=True)
        template = j2.get_template(policy_template)
        # Generate policy
        my_managed_policy = template.render(partition=self.partition, region=self.region, account=self.account_id,
                                               actions=actions, resources=resources, service=service)
        # Create policy
        self.my_managed_policy["Statement"].append(ast.literal_eval(my_managed_policy))

    def create_iam_policy(self):
        self.iam_client.create_policy(PolicyName='testS3Policydemo1', PolicyDocument=json.dumps(self.my_managed_policy))


if __name__ == '__main__':
    policy_gen = PolicyGen("us-east-1", "1234567890")

    # Add your sample policy below and generate combine policy for multiple services

    # s3 bucket
    bucket_list = ["test123"]
    s3_actions = ["s3:GetObject", "s3:GetObjectTagging", "s3:GetObjectVersion",
                  "s3:ListBucket", "s3:PutObject", "s3:PutObjectAcl"]
    policy_gen.render_s3_policy(bucket_list, s3_actions, "s3.j2")

    # cloudwatch
    cw_actions = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
    cw_resources = ["/aws/codebuild/test"]
    policy_gen.render_cw_policy(cw_resources, cw_actions, "cw.j2")

    # codebuild
    cb_resources = ["report-group/test-*"]
    cb_actions = ["codebuild:CreateReportGroup", "codebuild:CreateReport", "codebuild:UpdateReport",
                  "codebuild:BatchPutTestCases",  "codebuild:BatchPutCodeCoverages"]
    policy_gen.render_general_policy(cb_resources, cb_actions, "codebuild", "general.j2")

    # codecommit
    cb_resources = ["code_stepfunction_latest"]
    cb_actions = ["codecommit:GitPull"]
    policy_gen.render_general_policy(cb_resources, cb_actions, "codecommit", "general.j2")

    # generate policy
    # policy_gen.create_iam_policy()  # This is only required during AWS deployment.


