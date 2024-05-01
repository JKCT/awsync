"HTTP type models."
from awsync.models.strenum import StrEnum


class Method(StrEnum):
    """
    A HTTP request method.
    See: https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods
    """

    GET = "GET"
    "The GET method requests a representation of the specified resource. Requests using GET should only retrieve data."
    HEAD = "HEAD"
    "The HEAD method asks for a response identical to a GET request, but without the response body."
    POST = "POST"
    "The POST method submits an entity to the specified resource, often causing a change in state or side effects on the server."
    PUT = "PUT"
    "The PUT method replaces all current representations of the target resource with the request payload."
    DELETE = "DELETE"
    "The DELETE method deletes the specified resource."
    CONNECT = "CONNECT"
    "The CONNECT method establishes a tunnel to the server identified by the target resource."
    OPTIONS = "OPTIONS"
    "The OPTIONS method describes the communication options for the target resource."
    TRACE = "TRACE"
    "The TRACE method performs a message loop-back test along the path to the target resource."
    PATCH = "PATCH"
    "The PATCH method applies partial modifications to a resource."


class Scheme(StrEnum):
    "The HTTP scheme of the URI."
    http = "http"
    "Unencrypted Hypertext Transfer Protocol."
    https = "https"
    "Encrypted Hypertext Transfer Protocol Security."
