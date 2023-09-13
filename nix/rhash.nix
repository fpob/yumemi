{ lib
, buildPythonPackage
, fetchPypi
, rhash
, setuptools
, substituteAll
}:

buildPythonPackage rec {
  pname = "rhash-python";
  version = "1.1";
  format = "pyproject";

  src = fetchPypi {
    inherit version;
    pname = "rhash-Rhash";
    hash = "sha256-mUNFmCCgi9J2rR16cx3r0Lh4f4MsGK09jp1QUdunY00=";
  };

  nativeBuildInputs = [
    rhash
    setuptools
  ];

  patches = [
    (substituteAll {
      src = ./rhash-paths.patch;
      librhash = "${rhash}/lib/librhash.so";
    })
  ];

  pythonImportsCheck = [
    "rhash"
  ];

  meta = {
    license = rhash.meta.license;
  };
}
