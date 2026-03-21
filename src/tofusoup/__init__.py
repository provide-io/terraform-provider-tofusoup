"""TofuSoup Terraform provider package."""

from provide.foundation.utils.versioning import get_version

__path__ = __import__("pkgutil").extend_path(__path__, __name__)

__version__ = get_version("terraform-provider-tofusoup", __file__)
