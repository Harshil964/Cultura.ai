"""Image generation is a separate milestone. This module defines the
interface the Visual Studio page expects, so plugging in a real provider
(OpenAI images, Gemini, Stability, etc.) later only means implementing
`generate_image` — no changes needed in the page or the database layer.
"""
from __future__ import annotations

import os


class ImageGenerationNotConfigured(RuntimeError):
    pass


def generate_image(prompt: str) -> bytes:
    """Should return raw image bytes (PNG/JPEG) for the given prompt.
    Raises ImageGenerationNotConfigured until IMAGE_PROVIDER/IMAGE_API_KEY
    are wired to a real provider call.
    """
    if not os.getenv("IMAGE_API_KEY"):
        raise ImageGenerationNotConfigured(
            "Set IMAGE_PROVIDER and IMAGE_API_KEY in .env, and implement the "
            "provider call in services/visual_service.generate_image()."
        )
    raise NotImplementedError("Wire this up to your chosen image provider.")
