from django.conf import settings
import httplib
import socket
import ssl


class HTTPSConnectionValidating(httplib.HTTPSConnection):
    def __init__(self, host, port=None, key_file=None,
                 cert_file=None, timeout=None, strict=None):
        httplib.HTTPSConnection.__init__(
            self, host, port=port, key_file=key_file,
            cert_file=cert_file, timeout=timeout, strict=strict)
        self.key_file = key_file
        self.cert_file = cert_file
        self.timeout = timeout

    def connect(self):
        sock = socket.create_connection((self.host, self.port), self.timeout)
        if self._tunnel_host:
            self.sock = sock
            self._tunnel()

        self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file,
                                    ca_certs=settings.AWS_CA_BUNDLE,
                                    cert_reqs=ssl.CERT_REQUIRED)


def https_connection_factory(host, port=None, strict=None):
    return HTTPSConnectionValidating(host, port=port, strict=strict,
                                     key_file=settings.EVENT_AWS_SQS_KEY,
                                     cert_file=settings.EVENT_AWS_SQS_CERT)
