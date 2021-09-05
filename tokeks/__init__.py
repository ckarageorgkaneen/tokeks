"""A standard Python library for getting the Kubernetes token
of a AWS EKS cluster

No AWS CLI, third-party client or library (boto3, botocore, etc.) required.
"""
import hmac
import hashlib
import datetime
import base64
import re
from urllib.parse import quote as urlquote
from urllib.parse import urlsplit
from urllib.parse import urlencode


def _canonical_query_string(url):
    parts = urlsplit(url)
    canonical_query_string = ''
    if parts.query:
        key_val_pairs = []
        for pair in parts.query.split('&'):
            key, _, value = pair.partition('=')
            key_val_pairs.append((key, value))
        sorted_key_vals = []
        # Sort by the URI-encoded key names, and in the case of
        # repeated keys, then sort by the value.
        for key, value in sorted(key_val_pairs):
            sorted_key_vals.append('%s=%s' % (key, value))
        canonical_query_string = '&'.join(sorted_key_vals)
    return canonical_query_string


def _get_canonical_headers(headers):
    return '\n'.join([':'.join([k.lower(), str(v).strip()])
                      for k, v in sorted(headers.items())]) + '\n'


def _get_signed_headers(headers):
    return ';'.join([k.lower() for k in sorted(headers.keys())])


def _hash(msg):
    return hashlib.sha256(msg.encode()).hexdigest()


def _get_request_params(params):
    return '&'.join(["%s=%s" %
                     (urlquote(k, safe=''), urlquote(str(v), safe='~'))
                     for k, v in sorted(params.items())])


def _get_payload_hash():
    return _hash('')


def _get_canonical_request(params, headers, method, path, data,
                           use_canonical_query_string=False):
    if use_canonical_query_string:
        request_params = _canonical_query_string(params['url'])
    else:
        request_params = _get_request_params(params)
    return '\n'.join([
        method,
        path,
        request_params,
        _get_canonical_headers(headers),
        _get_signed_headers(headers),
        _get_payload_hash()
    ])


def _sign(key, msg, hex=False):
    if hex:
        return hmac.new(
            key.encode() if isinstance(key, str) else key,
            msg.encode(),
            hashlib.sha256).hexdigest()
    else:
        return hmac.new(
            key.encode() if isinstance(key, str) else key,
            msg.encode(),
            hashlib.sha256).digest()


class Tokeks(object):
    """A class for getting the Kubernetes token of a AWS EKS cluster."""

    YMD_FORMAT = '%Y%m%d'
    SIGV4_TIMESTAMP = '{ymd_format}T%H%M%SZ'.format(ymd_format=YMD_FORMAT)
    SIGV4_ALGORITHM = 'AWS4-HMAC-SHA256'
    SERVICE_NAME = 'sts'
    VERSION = '2011-06-15'
    STS_TOKEN_EXPIRES_IN = 60

    HOST = 'sts.{region_id}.amazonaws.com'
    URL = 'https://{host}/?Action=GetCallerIdentity&Version=' + VERSION

    def __init__(self, access_key_id, secret_access_key, region_id,
                 cluster_id, token_expiry=None):
        self._access_key_id = access_key_id
        self._secret_access_key = secret_access_key
        self.region_id = region_id
        self.cluster_id = cluster_id
        self.token_expiry = token_expiry or self.STS_TOKEN_EXPIRES_IN
        self.HOST = self.HOST.format(region_id=self.region_id)
        self.URL = self.URL.format(host=self.HOST)

    def _get_credential_scope(self, dt):
        return '/'.join([dt.strftime(self.YMD_FORMAT),
                         self.region_id,
                         self.SERVICE_NAME,
                         'aws4_request'])

    def _get_string_to_sign(self, params, headers, dt, method, path, data):
        canonical_request = _get_canonical_request(
            params=params,
            headers=headers,
            method=method,
            path=path,
            data=data,
            use_canonical_query_string=True)
        return '\n'.join(['AWS4-HMAC-SHA256',
                          dt.strftime(self.SIGV4_TIMESTAMP),
                          self._get_credential_scope(dt),
                          _hash(canonical_request)])

    def _get_key_to_sign_with(self, dt):
        return _sign(
            _sign(
                _sign(
                    _sign(('AWS4' + self._secret_access_key),
                          dt.strftime(self.YMD_FORMAT)),
                    self.region_id),
                self.SERVICE_NAME),
            'aws4_request')

    def _get_signature(self, params, headers, dt, method, path, data):
        key = self._get_key_to_sign_with(dt)
        string_to_sign = self._get_string_to_sign(params=params,
                                                  headers=headers, dt=dt,
                                                  method=method, path=path,
                                                  data=data)
        return _sign(key=key, msg=string_to_sign, hex=True)

    def _generate_presigned_url(self, params):
        query = {}
        query['X-Amz-Algorithm'] = self.SIGV4_ALGORITHM
        dt = datetime.datetime.utcnow()
        credential_scope = self._get_credential_scope(dt=dt)
        query['X-Amz-Credential'] = f'{self._access_key_id}/{credential_scope}'
        query['X-Amz-Date'] = dt.strftime(self.SIGV4_TIMESTAMP)
        query['X-Amz-Expires'] = self.token_expiry
        headers = {'host': self.HOST, 'x-k8s-aws-id': self.cluster_id}
        signed_headers = _get_signed_headers(headers)
        query['X-Amz-SignedHeaders'] = signed_headers
        params['url'] = f"{params['url']}&{urlencode(query)}"
        signature = self._get_signature(params=params, headers=headers,
                                        dt=dt, method='GET', path='/',
                                        data=None)
        query['X-Amz-Signature'] = signature
        presigned_url = f'{self.URL}&{urlencode(query)}'
        return presigned_url

    def get_token(self):
        params = {
            'method': 'GET',
            'url': self.URL,
            'body': {},
            'headers': {
                'x-k8s-aws-id': self.cluster_id
            },
            'context': {}
        }
        signed_url = self._generate_presigned_url(params)
        base64_url = base64.urlsafe_b64encode(
            signed_url.encode('utf-8')).decode('utf-8')
        return 'k8s-aws-v1.' + re.sub(r'=*', '', base64_url)
