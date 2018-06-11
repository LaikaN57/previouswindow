# PreviousWindow
Amazon Web Services CloudFormation Multi-Region VPC Peering Connection Creation

PreviousWindow is a demo which shows how to implement AWS Multi-Region VPC Peering Connections using mostly CloudFormation templates and a little bit of Python/boto3.
## Requirements
- [x] Two regions (us-west-1 and us-west-2).
- [x] One VPC per region.
- [x] Three networks per VPC (Trusted, Stage, and Prod).
- [x] Connectivity from the Trusted network in region A to the Stage/Prod networks in region A and region B.
- [x] Global application access to Stage/Prod networks. (In our case, we chose a simple HTTP server.)
- [x] (Optional) Connectivity between the Stage networks in region A and region B.
- [x] (Optional) Connectivity between the Prod networks in region A and region B.
## Running the Demo
To run this demo you will need the following pre-reqs. This section will provide instructions for installation, testing of the above requirements, and manual uninstallation of the demo.
### Prerequisites
* Python 3 - main scripting language used for running the demo
  * boto3 (`pip3 install boto3`) - AWS API bindings for Python
* ssh - for requirements verificaion and key generation
* web browser - for requirements verification
### Install Demo
In order to successfully deploy this demo, you will need to do the following:
1. Create an IAM User in your AWS Account with the AdministatorAccess permission policy
   * Access type: **Programmatic access**
   * Permissions:
     * Attach existing policies directly
       * **AdministratorAccess**
2. Edit the **config** section of `previouswindow.py` with the following:
   * AWS Account ID
   * IAM User Access Key ID
   * IAM User Access Key Secret
2. Run `run-demo.sh` (This will output an SSH private key along with IP information you will need to access the hosts.)
### Demo Testing Guide
1. Test global application connectivity
   * In your web browser, navigiate to the 4 stage/prod public addresses listed in the PreviousWindow output. These shoould be the public IP addresses for all stage and prod servers. (Public IP)
   * Open SSH and connect to each of the 2 bastion hosts. (Public IP)
2. Test cross-region Trusted network connectivity
   * Open SSH and connect to a bastion host. (Public IP)
   * From the bastion host, ssh to a stage or prod server in the **same** region. (Private IP)
   * From the bastion host, ssh to a stage or prod server in the **other** region. (Private IP)
3. (For optional requirements) Test cross-region nextwork connectivity
   * Open SSH and connect to a bastion host. (Public IP)
   * From the bastion host, ssh to a stage or prod server. (Private IP)
   * From the stage or prod server, ssh to a server in the **same** nextwork teir, but a **different** region (ex. ca-prod-1 to or-prod-1). (Private IP)
### Uninstall Demo (Manual)
1. Remove pwStackCA and pwStackOR
2. Remove VPC Peering Connection from us-west-1 (or us-west-2)
3. Remove pwStackVPCCA and pwStackVPCOR
4. Remove pwKeyPair from us-west-1
5. Remove pwKeyPair from us-west-2
6. rm -rf pwKeyPair.*
7. Remove IAM User
## Call Graph
This is a just a graph of what scripts call what other scripts for debugging if needed.
1. run-demo.sh
   1. previouswindow.py
      1. pwvpc-1.0.0.json
      2. pwstack-1.0.6.json
## Wishlist
This demo is currently just a basic connectivity proof of concept. In order to make this into a minimum viable product and beyond, the following enhancements should be made.
- [ ] NACLs
- [ ] NAT Gateways or proxies
- [ ] Auto-scale/load balancing
- [ ] Route 53 GeoDNS
- [ ] Modularize CloudFormation templates
- [ ] User configuration
## Questions
Please let me know if you have any questions, comments, issues, etc. Feel free to create issue and/or pull requests in github.
## Refernces
* [VPC Connectivity Options](https://docs.aws.amazon.com/aws-technical-content/latest/aws-vpc-connectivity-options/amazon-vpc-to-amazon-vpc-connectivity-options.html)
* [VPC Peering Limitations](https://docs.aws.amazon.com/AmazonVPC/latest/PeeringGuide/vpc-peering-basics.html#vpc-peering-limitations)
* [CloudFormation StackSets Pre-reqs](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/stacksets-prereqs.html)
  * [AWSCloudFormationStackSetAdministrationRole.yml](https://s3.amazonaws.com/cloudformation-stackset-sample-templates-us-east-1/AWSCloudFormationStackSetAdministrationRole.yml)
  * [AWSCloudFormationStackSetExecutionRole.yml](https://s3.amazonaws.com/cloudformation-stackset-sample-templates-us-east-1/AWSCloudFormationStackSetExecutionRole.yml)
