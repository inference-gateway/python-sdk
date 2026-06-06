from importlib.metadata import version

import inference_gateway


def test_version_matches_package_metadata():
    """__version__ should track installed package metadata, not a hardcoded value."""
    assert inference_gateway.__version__ == version("inference-gateway")
    assert isinstance(inference_gateway.__version__, str)
