#!/usr/local/bin/python3

import boto3

################################################################################

# START OF CONFIG SECTION

AWS_ACCOUNT_ID = ''
AWS_USER = ''
AWS_SECRET = ''

# END OF CONFIG SECITON

################################################################################

# open clients for different regions
print('Connecting to AWS EC2 and CloudFormation...')
ec2_ca = boto3.client('ec2', region_name='us-west-1',
                      aws_access_key_id=AWS_USER, aws_secret_access_key=AWS_SECRET)
cfn_ca = boto3.client('cloudformation', region_name='us-west-1',
                      aws_access_key_id=AWS_USER, aws_secret_access_key=AWS_SECRET)
ec2_or = boto3.client('ec2', region_name='us-west-2',
                      aws_access_key_id=AWS_USER, aws_secret_access_key=AWS_SECRET)
cfn_or = boto3.client('cloudformation', region_name='us-west-2',
                      aws_access_key_id=AWS_USER, aws_secret_access_key=AWS_SECRET)

# deploy vpc stacks
print('Creating VPC Stacks with CloudFormation...')
cfn_ca.create_stack(
    StackName='pwStackVPCCA',
    TemplateURL='https://s3-us-west-1.amazonaws.com/previouswindow/pwvpc-1.0.0.json'
)

cfn_or.create_stack(
    StackName='pwStackVPCOR',
    TemplateURL='https://s3-us-west-1.amazonaws.com/previouswindow/pwvpc-1.0.0.json'
)

# wait for stack create
print('Waiting for VPC Stacks to be created...')
cfn_ca.get_waiter('stack_create_complete').wait(
    StackName='pwStackVPCCA'
)
cfn_or.get_waiter('stack_create_complete').wait(
    StackName='pwStackVPCOR'
)

# get VPC IDs
print("Getting VPC IDs from CloudFormation...")
pwStackVPCCA = cfn_ca.describe_stacks(
    StackName='pwStackVPCCA'
)
pwStackVPCOR = cfn_or.describe_stacks(
    StackName='pwStackVPCOR'
)

# create VPC Peering Connection
print('Creating VPC Peering Connection with API calls...')
vpc_peering_connection_response = ec2_ca.create_vpc_peering_connection(
    PeerOwnerId=AWS_ACCOUNT_ID,
    PeerVpcId=pwStackVPCOR['Stacks'][0]['Outputs'][0]['OutputValue'],
    VpcId=pwStackVPCCA['Stacks'][0]['Outputs'][0]['OutputValue'],
    PeerRegion='us-west-2'
)

# wait
print('Waiting for the VPC Peering Connection to become available...')
ec2_or.get_waiter('vpc_peering_connection_exists').wait(
    Filters=[
        {
            'Name': 'status-code',
            'Values': [
                'pending-acceptance',
            ]
        },
        {
            'Name': 'vpc-peering-connection-id',
            'Values': [
                vpc_peering_connection_response['VpcPeeringConnection']['VpcPeeringConnectionId'],
            ]
        }
    ],
    VpcPeeringConnectionIds=[
        vpc_peering_connection_response['VpcPeeringConnection']['VpcPeeringConnectionId'],
    ]
)

print('Finializing VPC Peering Connection...')
ec2_or.accept_vpc_peering_connection(
    VpcPeeringConnectionId=vpc_peering_connection_response[
        'VpcPeeringConnection']['VpcPeeringConnectionId']
)

# wait
print('Waiting for the VPC Peering Connection to become available (this may take some time)...')
vpc_ca_waiter = ec2_ca.get_waiter('vpc_peering_connection_exists').wait(
    Filters=[
        {
            'Name': 'status-code',
            'Values': [
                'active',
            ]
        },
        {
            'Name': 'vpc-peering-connection-id',
            'Values': [
                vpc_peering_connection_response['VpcPeeringConnection']['VpcPeeringConnectionId'],
            ]
        }
    ],
    VpcPeeringConnectionIds=[
        vpc_peering_connection_response['VpcPeeringConnection']['VpcPeeringConnectionId'],
    ]
)

#print('Created VPC Peering Connection!')
# print(pwStackVPCCA['Stacks'][0]['Outputs'][0]['OutputValue'])
# print(pwStackVPCOR['Stacks'][0]['Outputs'][0]['OutputValue'])
# print(
#    vpc_peering_connection_response['VpcPeeringConnection']['VpcPeeringConnectionId'])


#
# TODO create private keys
#
#print('Generating RSA keys...')

fp = open('pwKeyPair.pub')
pw_key_pair_public = fp.read()
fp.close()

# upload public keys to ec2
print('Importing Key Pairs...')
ec2_ca.import_key_pair(
    KeyName='pwKeyPair',
    PublicKeyMaterial=pw_key_pair_public
)
ec2_or.import_key_pair(
    KeyName='pwKeyPair',
    PublicKeyMaterial=pw_key_pair_public
)

# wait for KPs
print('Waiting for Key Pairs to become available...')
ec2_ca.get_waiter('key_pair_exists').wait(
    KeyNames=[
        'pwKeyPair',
    ]
)
ec2_or.get_waiter('key_pair_exists').wait(
    KeyNames=[
        'pwKeyPair',
    ]
)

# deploy route stacks
print('Deploying CloudFormtion Stacks...')
cfn_ca.create_stack(
    StackName='pwStackCA',
    TemplateURL='https://s3-us-west-1.amazonaws.com/previouswindow/pwstack-1.0.6.json',
    Parameters=[
        {
            'ParameterKey': 'inVPC',
            'ParameterValue': pwStackVPCCA['Stacks'][0]['Outputs'][0]['OutputValue']
        },
        {
            'ParameterKey': 'inPCX',
            'ParameterValue': vpc_peering_connection_response['VpcPeeringConnection']['VpcPeeringConnectionId']
        }
    ]
)

cfn_or.create_stack(
    StackName='pwStackOR',
    TemplateURL='https://s3-us-west-1.amazonaws.com/previouswindow/pwstack-1.0.6.json',
    Parameters=[
        {
            'ParameterKey': 'inVPC',
            'ParameterValue': pwStackVPCOR['Stacks'][0]['Outputs'][0]['OutputValue']
        },
        {
            'ParameterKey': 'inPCX',
            'ParameterValue': vpc_peering_connection_response['VpcPeeringConnection']['VpcPeeringConnectionId']
        }
    ]
)

# wait for stack create
print('Waiting for Stacks to be created...')
cfn_ca.get_waiter('stack_create_complete').wait(
    StackName='pwStackCA'
)
cfn_or.get_waiter('stack_create_complete').wait(
    StackName='pwStackOR'
)

# get VPC IDs
print("Getting IDs from CloudFormation...")
pwStackCA = cfn_ca.describe_stacks(
    StackName='pwStackCA'
)
pwStackOR = cfn_or.describe_stacks(
    StackName='pwStackOR'
)

print('')
print('IP Addresses')
print('--------------------------------')
for output in pwStackCA['Stacks'][0]['Outputs']:
    print(output['OutputKey'] + ' = ' + output['OutputValue'])
for output in pwStackOR['Stacks'][0]['Outputs']:
    print(output['OutputKey'] + ' = ' + output['OutputValue'])
print('--------------------------------')
