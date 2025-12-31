# py3exiv2 on macOS (Apple Silicon) using uv

This project uses `py3exiv2==0.11.0`, which is not compatible with Homebrew's
`exiv2` 0.28.x API. It also needs a Boost.Python build that matches the
project's Python (3.11 via uv), not the Homebrew system Python.

The working setup below builds local, project-scoped deps under `/.deps` and
installs py3exiv2 against them.

## One-time dependencies (Homebrew)

- `boost`
- `boost-python3`
- `cmake`

Note: installing `boost-python3` may relink Homebrew's `python3` to a newer
version. If that happens and you want to revert, run:

```
brew unlink python@3.14
brew link python@3.11 --force --overwrite
```

## Build Exiv2 0.27.7 locally

```
mkdir -p /tmp/exiv2-src
curl -L https://github.com/Exiv2/exiv2/archive/refs/tags/v0.27.7.tar.gz \
  -o /tmp/exiv2-src/exiv2-0.27.7.tar.gz

tar -xzf /tmp/exiv2-src/exiv2-0.27.7.tar.gz -C /tmp/exiv2-src

cmake -S /tmp/exiv2-src/exiv2-0.27.7 \
  -B /tmp/exiv2-src/exiv2-0.27.7/build \
  -DCMAKE_INSTALL_PREFIX=/tmp/exiv2-0.27 \
  -DEXIV2_ENABLE_NLS=OFF \
  -DEXIV2_BUILD_SAMPLES=OFF \
  -DEXIV2_BUILD_EXIV2_COMMAND=OFF \
  -DEXIV2_ENABLE_BMFF=ON

cmake --build /tmp/exiv2-src/exiv2-0.27.7/build --config Release
cmake --install /tmp/exiv2-src/exiv2-0.27.7/build

mkdir -p .deps
rm -rf .deps/exiv2-0.27
cp -R /tmp/exiv2-0.27 .deps/exiv2-0.27
```

## Build Boost.Python for Python 3.11 (uv)

```
mkdir -p /tmp/boost-src
curl -L https://archives.boost.io/release/1.90.0/source/boost_1_90_0.tar.gz \
  -o /tmp/boost-src/boost_1_90_0.tar.gz

tar -xzf /tmp/boost-src/boost_1_90_0.tar.gz -C /tmp/boost-src

cd /tmp/boost-src/boost_1_90_0
./bootstrap.sh --with-libraries=python --with-python="$HOME/.local/share/uv/python/cpython-3.11.9-macos-aarch64-none/bin/python3"

# Update project-config.jam to point to uv's Python headers/libs.
# Example line:
# using python : 3.11 : "/Users/<you>/.local/share/uv/python/cpython-3.11.9-macos-aarch64-none/bin/python3" : "/Users/<you>/.local/share/uv/python/cpython-3.11.9-macos-aarch64-none/include/python3.11" : "/Users/<you>/.local/share/uv/python/cpython-3.11.9-macos-aarch64-none/lib" ;

./b2 install \
  --prefix="/Users/pranay/Projects/metaextract/.deps/boost-python311" \
  --with-python link=shared threading=multi runtime-link=shared
```

## Patch py3exiv2 to find Boost.Python

Download the sdist and update `setup.py` to search the local Boost.Python lib:

```
mkdir -p /tmp/py3exiv2-src
curl -L https://files.pythonhosted.org/packages/4e/c3/b6a10b79baf14805a38ac9caa4e9d71aa4bb186ede4fc3958dc7541f5b6a/py3exiv2-0.11.0.tar.gz \
  -o /tmp/py3exiv2-src/py3exiv2-0.11.0.tar.gz

tar -xzf /tmp/py3exiv2-src/py3exiv2-0.11.0.tar.gz -C /tmp/py3exiv2-src

# Edit /tmp/py3exiv2-src/py3exiv2-0.11.0/setup.py
# Add this path to get_libboost_osx():
#   "/Users/pranay/Projects/metaextract/.deps/boost-python311/lib/libboost_python*.dylib"
```

## Install with uv (use local deps + rpath)

```
export EXIV2_ROOT="$PWD/.deps/exiv2-0.27"
export EXIV2_INCLUDEDIR="$EXIV2_ROOT/include"
export EXIV2_LIBRARYDIR="$EXIV2_ROOT/lib"

export BOOST_ROOT="$PWD/.deps/boost-python311"
export BOOST_INCLUDEDIR="$BOOST_ROOT/include"
export BOOST_LIBRARYDIR="$BOOST_ROOT/lib"

export LDFLAGS="-L$BOOST_LIBRARYDIR -L$EXIV2_LIBRARYDIR -Wl,-rpath,$BOOST_LIBRARYDIR -Wl,-rpath,$EXIV2_LIBRARYDIR"
export CPPFLAGS="-I$BOOST_INCLUDEDIR -I$EXIV2_INCLUDEDIR"
export PKG_CONFIG_PATH="$EXIV2_ROOT/lib/pkgconfig:$BOOST_ROOT/lib/pkgconfig"

PIP_USE_PEP517=0 uv pip install --no-cache --force-reinstall --no-deps \
  /tmp/py3exiv2-src/py3exiv2-0.11.0
```

## Verify

```
.venv/bin/python - <<'PY'
import pyexiv2
print("pyexiv2", pyexiv2.__version__)
PY
```
