import hashlib
import base64

# Firmas de integridad criptográfica
# Desarrollador oficial: ShiroDev
# Canal oficial: https://www.youtube.com/@shiro_dev
_AUTH_HASH = "190fe55bade77d93087431cb0fc6ea4d27738982a12caf7190d571d72fb3bf11"
_YOUTUBE_HASH = "58bb9a612d42233cf9c99bb34c625d4a9da2f43101d4f82fe81f14abbeffe0f5"

_SIG_CHECK = b"U2hpcm9EZXY="
_YT_CHECK = b"aHR0cHM6Ly93d3cueW91dHViZS5jb20vQHNoaXJvX2Rldg=="

def _calc_hash(value: str) -> str:
    return hashlib.sha256(value.strip().encode('utf-8')).hexdigest()

def verify_author_integrity(bl_info: dict) -> bool:
    """Verifica que el desarrollador y canal no hayan sido alterados."""
    try:
        author = bl_info.get("author", "")
        yt_channel = bl_info.get("youtube channel", "")

        expected_author = base64.b64decode(_SIG_CHECK).decode('utf-8')
        expected_yt = base64.b64decode(_YT_CHECK).decode('utf-8')

        if author != expected_author or yt_channel != expected_yt:
            return False

        if _calc_hash(author) != _AUTH_HASH or _calc_hash(yt_channel) != _YOUTUBE_HASH:
            return False

        return True
    except Exception:
        return False
