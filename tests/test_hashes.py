import hashlib
import importlib
import zlib

from server.extractor.modules import extract_file_hashes


def _expected_hashes(data: bytes) -> dict:
    md5 = hashlib.md5()
    sha1 = hashlib.sha1()
    sha256 = hashlib.sha256()
    crc = 0
    for chunk_start in range(0, len(data), 65536):
        chunk = data[chunk_start:chunk_start + 65536]
        md5.update(chunk)
        sha1.update(chunk)
        sha256.update(chunk)
        crc = zlib.crc32(chunk, crc)
    return {
        "md5": md5.hexdigest(),
        "sha1": sha1.hexdigest(),
        "sha256": sha256.hexdigest(),
        "crc32": format(crc & 0xFFFFFFFF, "08x"),
    }


def test_extract_file_hashes_known_values(tmp_path):
    payload = b"metaextract-hash-test\n"
    path = tmp_path / "hash-input.bin"
    path.write_bytes(payload)

    result = extract_file_hashes(str(path))
    assert "error" not in result
    assert result == _expected_hashes(payload)


def test_perceptual_hashes_export_from_module():
    modules = importlib.import_module("server.extractor.modules")
    perceptual_module = importlib.import_module("server.extractor.modules.perceptual_hashes")
    assert modules.extract_perceptual_hashes is perceptual_module.extract_perceptual_hashes
