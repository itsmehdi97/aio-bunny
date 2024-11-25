author_info = (
    ("Author", "mkamani@sheypoor.com"),)

package_info = """
An asyncio wrapper around aio-pika.
Provides simplified API, graceful consumer shutdown and optional idempotency.
"""
package_license = "MIT License"

team_email = ""

version_info = (0, 0, 7)

__author__ = ", ".join("{} <{}>".format(*info) for info in author_info)
__version__ = ".".join(map(str, version_info))
