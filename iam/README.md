# AWS Production Level IAM Configuration Settings 
This README explains how to configure AWS IAM for a production environment.  

In order to create an equivalent iam policy to the one used in this repository, run the commands below. 

## Pre-requisites 
The following instructions assume you have installed the following tools in your development environment.  Older versions may work, the versions listed are the ones that were used at the time this code was written. 
* AWS Command Line Interface - `aws-cli/1.10.47`
* Python - `Python/2.7.10`
* Darwin - `Darwin/15.5.0`
* Botocore - `botocore/1.4.37`
* Valid AWS credentials (to set your credentials, simply type `aws configure` and enter the values when prompted) 
* Replace the `Resource` in `role-policy.json` to correspond to a resource that your AWS account has access to. 

### Important considerations 
Please bear in mind the following considerations about the choice of using the identifier `facebook-ctf` throughout these instructions and how IAM actually works. 
* The identifier `facebook-ctf` is used in this example for the names of the iam instance profile, and the iam role, and the iam role policy. 
* The value `facebook-ctf` is simply used as convention and for simplicity. 
* You can indeed specify different identifiers for the instance profile, the role, and the associated policy.  
* Your use case should choose an identifier that makes the most sense. 

## Create the IAM Policy 
``` 
#!/bin/bash 
aws iam create-policy --policy-name facebook-ctf --policy-document file://${ABSOLUTE_PATH_TO_POLICY_DOCUMENT} | tee aws-iam-policy-creation-output.json
```
A successful call to the command above will result in a JSON document containing the PolicyId, Arn, and other relevant data. The aws-iam-policy-creation-output.json will contain the resulting output as well. This file contains your `arn` and other relevant data. 

* The file `role-policy.json` is an the policy we will be using with the role we intended to create. 

* An example ARN for the response would be `arn:aws:iam::000000000000:policy/facebook-ctf where 000000000000` is the amazon account ID and `facebook-ctf` is the name of the policy you created. 

You have now created a policy for use with your production deployment of fbctf. 

## Retrieve an existing policy 

Sometimes we will want to use an existing policy.  You will need to replace the variables shown in the example with your relevant values. 
* The call below would retrieve the policy that was created with your ${ABSOLUTE_PATH_TO_POLICY_DOCUMENT} using the commands under the "Create the IAM Policy" subsection of this README. 
* `v1` is the default version ID, if you have more than one version, this will be different. 
* The pipe (`|`) sends the resulting output of the CLI call to a file called `facebook-ctf-policy.json` in your current working directory. 

```
#!/bin/bash 

aws iam get-policy-version --policy-arn arn:aws:iam::000000000000:policy/facebook-ctf --version-id v1 | tee facebook-ctf-policy.json
```
At this point, `facebook-ctf-policy.json` is the contents policy we will be using to create the iam role. 

The following command will retrieve the `arn` and other relevant metadata of a given policy. If you are following these instructions, this will also be the resulting output of the `create-policy` command shown above in the file `aws-iam-policy-creation-output.json`

```
#!/bin/bash 

aws iam get-policy  --policy-arn arn:aws:iam::000000000000:policy/facebook-ctf | tee aws-iam-get-policy-output.json
```


## Create the IAM Role 
* NOTE: the `trust-relationship-assume-role-policy.json` file in this document contains the desired trust relationship for the role, therefore we will be referencing in the role creation. 
* To create the IAM role, simply run the proper commands as shown in an example below. 
* The value `FULL_PATH_TO_REPO` is the full path to this repository, local to your workstation. 
* The below example is for a Jenkins execution of these commands via a jenkins job is shown below, with a fallback to the repository existing in the home directory of the ubuntu use (`/home/ubuntu/fbctf_puppetized`). 

```
#!/bin/bash 

ROLE_NAME=facebook-ctf
FULL_PATH_TO_REPO=${WORKSPACE:-"/home/ubuntu/fbctf_puppetized"} 
RESPONSE_OUTPUT_FILE="${ROLE_NAME}-response.json" 

aws iam create-role --role-name "${ROLE_NAME}"" --assume-role-policy-document file://${FULL_PATH_TO_REPO}/iam/trust-relationship-assume-role-policy.json | tee "${RESPONSE_OUTPUT_FILE}"
```

You will now need to attach the policy created in step 1 to the IAM role created in step 2. 


## Attach policy to role 
This step requires you to have the `arn` for your desired policy.  If you need to locate this value, simply look at the `aws-iam-policy-creation-output.json` if you piped your command output to said file.  If you lost it, go to the AWS console, click around and find it.  

An example ARN for the policy we will be attaching to the `facebook-ctf` iam role created in the instructions above would be `arn:aws:iam::000000000000:policy/facebook-ctf where 000000000000` is the amazon account ID and `facebook-ctf` is the name of the policy you created. 

The below instructions associate the policy with the role you created. 

NOTE: `facebook-ctf` is both the policy and the role name, THIS DOES NOT HAVE TO BE THE CASE.  They CAN be named different values. 

```
#!/bin/bash 
aws iam attach-role-policy --role-name facebook-ctf --policy-arn arn:aws:iam::000000000000:policy/facebook-ctf

# If the resulting value of the echo command below is equal to 0, your policy was attached to the role properly. 
echo $?
```

You will probably want to verify that the role was indeed associated with the policy granting access to the resources contained within. In order to do that, follow the commands in the section following this one. 

## Validation of IAM Role Policy Attachment  

You will want to validate that the necessary policy is attached to the role you created. In order to do so, follow the commands below. 

* The value for the role created is the same as above, `facebook-ctf` 
* The policy that should be attached is the same one as shown above, also named `facebook-ctf` (although we could have a policy attached named `foobar` instead) 

```
#!/bin/bash 
aws iam list-attached-role-policies --role-name facebook-ctf | tee facebook-ctf-attached-role-policies.json
```

* The response of the call to get attached role policies (also present in facebook-ctf-attached-role-policies.json if you used the command example above) will contain a value called `AttachedPolicies` which are the associated policies of the role you provided.  
* If the value of `AttachedPolicies` is `[]` than you have no policies attached to the role. 
* The value of `AttachedPolicies` should at this point, contain the policy shown in this example as well as any other policies you may desire for your production environment. 

## Create the IAM Instance Profile 

Since we will be deploying to an amazon instance, we will need to create a profile to associate to it.  This is done with one simple command as shown below. 

```
#!/bin/bash 
aws iam create-instance-profile --instance-profile-name facebook-ctf | tee facebook-ctf-iam-role-creation-output.json
```

The file facebook-ctf-iam-role-creation-output.json will have the resulting output that is written to `stdout` if you use the example shown above. The file should have values for `InstanceProfileId` (the ID of the profile), `Arn` (the amazon resource number), and `InstanceProfileName` amongst some other pieces of metadata such as `CreationDate`, `Path`, and `Roles` (there may be others) 

Now that we have a profile to associate with the fbctf image we will be using in production, we must ensure that the role containing the required policies is associated with the facebook-ctf instance profile. 

## Attach role to profile 

We will now attach our `facebook-ctf` _IAM Role_ to our `facebook-ctf` _IAM Instance Profile._

* The profile `facebook-ctf` needs to be attached to the role `facebook-ctf` (which has the policy `facebook-ctf` attached to it), which has instructions on what resources any instances using this profile will be allowed to interact with _without requiring any additonal credentials._
* Because of the fact that an instance profile can access all the resources associated with the role contained within it -- it is imperative that you take extreme care and caution when configuring these items, especially for a production environment. 
* The commands below show how to associate a role with a profile, `facebook-ctf` is used as the identiier for both the role and profile. 

```
#!/bin/bash 
aws iam add-role-to-instance-profile --instance-profile-name facebook-ctf --role-name facebook-ctf

# If the resulting value of the echo command below is equal to 0, your policy was attached to the role properly. 
echo $?
```

You should now have the `facebook-ctf` role associated with the instance profile `facebook-ctf`

## Validation of IAM Instance Profile Role Attachent 
You will need to validate that the `facebook-ctf` IAM Instance profile has the `facebook-ctf` role associated it with it.  

* Keep in mind that in your environment you may need to have additional roles associated with an instance profile. 
* At the very minimum, the `facebook-ctf` role should be associated with the IAM profile that is deploying it. 

```
#!/bin/bash
aws iam get-instance-profile --instance-profile-name facebook-ctf | tee facebook-ctf-instance-profile.json 
```

## A Successful Configuration
This section explains how to detect a successful IAM configuration for the fbctf deployment. 

* If you followed these instructions, the values shown in the code block below should be really similar to the ones in a file named `facebook-ctf-instance-profile.json` with the values unique to your account located in the directory you executed the final command. 
* If you don't have the above file, an example of a completely successful configuration of the role, policy, and profile can be found in `outputs/valid-facebook-ctf-iam-profile.json` for your own reference. The values shown below are the same as that in outputs/valid-facebook-ctf-iam-profile.json. 

```
{
    "InstanceProfile": {
        "InstanceProfileId": "AIPAJH5BFDHZRMADXXXXX", 
        "Roles": [
            {
                "AssumeRolePolicyDocument": {
                    "Version": "2012-10-17", 
                    "Statement": [
                        {
                            "Action": "sts:AssumeRole", 
                            "Effect": "Allow", 
                            "Principal": {
                                "Service": "ec2.amazonaws.com"
                            }
                        }
                    ]
                }, 
                "RoleId": "AROAJBOMZEST4ACKXXXXX", 
		        "CreateDate": "0000-00-00T00:00:00Z", 
                "RoleName": "facebook-ctf", 
                "Path": "/", 
                "Arn": "arn:aws:iam::000000000000:role/facebook-ctf"
            }
        ], 
        "CreateDate": "0000-00-00T00:00:00Z", 
        "InstanceProfileName": "facebook-ctf", 
        "Path": "/", 
        "Arn": "arn:aws:iam::000000000000:instance-profile/facebook-ctf"
    }
}
```

Hope these instructions were helpful to you.  If you found something to be inaccurate, confusing, or out of date I would greatly appreciate it if you could at the very least notify me so that I may improve this file when i have the time to allocate to it.  If you are really feeling like being an active member of the community, you can always contribute an improvement to this `README` or any other files in this project. Contributions are encouraged! Even the smallest ones! 