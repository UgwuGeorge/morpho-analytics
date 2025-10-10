"""
Napari plugin package for morpho-analytics.

Provides an npe2 manifest (napari.yaml) and an npe1 fallback
so the widget is discoverable in both modes.
"""
from __future__ import annotations

from ._widget import tracking_widget


def napari_experimental_provide_dock_widget():
    """npe1 fallback: expose the tracking widget to Napari.

    This ensures the plugin appears in the Plugins menu even if
    npe2 command registration is not available in a given setup.
    """
    return [tracking_widget]
