import importlib.metadata

import inference_gateway


def test_version_matches_package_metadata():
    """__version__ tracks package metadata, falling back to "0.0.0" for source checkouts.

    CI runs the suite against the source tree without ``pip install``, so distribution
    metadata is absent and ``__version__`` falls back to "0.0.0". When the package is
    installed, ``__version__`` must equal the metadata version. Either way it must never
    be a stale hardcoded literal.
    """
    try:
        expected = importlib.metadata.version("inference-gateway")
    except importlib.metadata.PackageNotFoundError:
        expected = "0.0.0"
    assert inference_gateway.__version__ == expected
    assert isinstance(inference_gateway.__version__, str)
