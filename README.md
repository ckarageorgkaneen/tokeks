[![PyPI version](https://badge.fury.io/py/tokeks.svg)](https://badge.fury.io/py/tokeks) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# tokeks

![](resources/aws_eks_icon.png)

A standard Python library for getting the Kubernetes token of a AWS EKS cluster.

**No** AWS CLI, third-party client or library (boto3, botocore, etc.) required.

## Library Usage

```python
from tokeks import Tokeks
tokeks = Tokeks(
    access_key_id='YOUR_AWS_ACCESS_KEY_ID',
    secret_access_key='YOUR_AWS_SECRET_ACCESS_KEY',
    region_id='YOUR_REGION_ID',
    cluster_id='YOUR_CLUSTER_ID')
token = tokeks.get_token()
```

## CLI Usage

1. Add your credentials to `credentials.py`

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
