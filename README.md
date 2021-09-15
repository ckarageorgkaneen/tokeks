[![PyPI version](https://badge.fury.io/py/tokeks.svg)](https://badge.fury.io/py/tokeks) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# tokeks

![](resources/aws_eks_icon.png)

A zero-dependency Python library for getting the Kubernetes token of a AWS EKS cluster.

**No** AWS CLI, third-party client or library (boto3, botocore, etc.) required.

## Installation
```bash
pip install tokeks
```

## Usage prerequisites
Assign your credentials to environment variables:
```bash
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
```

## Library usage

```python
from tokeks import Tokeks
tokeks = Tokeks(
    access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
    secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
    region_id='YOUR_REGION_ID',
    cluster_id='YOUR_CLUSTER_ID')
token = tokeks.get_token()
```

## CLI usage
1. Go to project directory 

2. Run script:
```bash
TOKEN=$(./getekstoken us-west-1 cluster-1)
```

3. Verify Kubernetes API access:
```bash
APISERVER=...
curl -X GET $APISERVER/api --header "Authorization: Bearer $TOKEN" --insecure
```

If the response is something like:

```json
{
  "kind": "APIVersions", 
  "versions": [
    "v1"
  ],
  "serverAddressByClientCIDRs": [
    {
      "clientCIDR": "0.0.0.0/0",
      "serverAddress": "..."
    }  
  ]
}
```

(and does not contain "Unauthorized"), you're good to go!

### Inspired by:
1. [API Authorization from Outside a Cluster](https://github.com/kubernetes-sigs/aws-iam-authenticator#api-authorization-from-outside-a-cluster)
2. [eks-token](https://github.com/peak-ai/eks-token)
