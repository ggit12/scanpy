"""This file contains some common fixtures for use in tests.

This is kept seperate from the helpers file because it relies on pytest.
"""
from __future__ import annotations

from pathlib import Path
from collections.abc import Callable

import pytest
import numpy as np
from numpy.typing import ArrayLike
from scipy import sparse
from anndata.tests.helpers import asarray

from ...._compat import DaskArray
from ..._pytest.marks import needs
from .data import (
    _pbmc3ks_parametrized_session,
    pbmc3k_parametrized,
    pbmc3k_parametrized_small,
)


__all__ = [
    "array_type",
    "float_dtype",
    "doctest_env",
    "_pbmc3ks_parametrized_session",
    "pbmc3k_parametrized",
    "pbmc3k_parametrized_small",
]


def _as_dense_dask_array(x: ArrayLike) -> DaskArray:
    import dask.array as da

    return da.from_array(asarray(x))


@pytest.fixture(
    params=[
        pytest.param(asarray, id="numpy-ndarray"),
        pytest.param(sparse.csr_matrix, id="scipy-csr"),
        pytest.param(sparse.csc_matrix, id="scipy-csc"),
        # Dask doesn’t support scipy sparse matrices, so only dense here
        pytest.param(_as_dense_dask_array, marks=[needs("dask")], id="dask-array"),
    ]
)
def array_type(
    request,
) -> Callable[[ArrayLike], DaskArray | np.ndarray | sparse.spmatrix]:
    """Function which converts passed array to one of the common array types."""
    return request.param


@pytest.fixture(params=[np.float64, np.float32])
def float_dtype(request):
    return request.param


@pytest.fixture()
def doctest_env(cache: pytest.Cache, tmp_path: Path) -> None:
    from scanpy import settings
    from scanpy._compat import chdir

    old_dd, settings.datasetdir = settings.datasetdir, cache.mkdir("scanpy-data")
    with chdir(tmp_path):
        yield
    settings.datasetdir = old_dd
