{ lib
, attrs
, buildPythonPackage
, click
, cryptography
, installShellFiles
, poetry-core
, pytestCheckHook
, pytest-mock
, pythonRelaxDepsHook
, rhash
}:

let
  pyproject = builtins.fromTOML (builtins.readFile ../pyproject.toml);
in

buildPythonPackage rec {
  pname = pyproject.tool.poetry.name;
  version = pyproject.tool.poetry.version;
  format = "pyproject";

  src = ../.;

  nativeBuildInputs = [
    installShellFiles
    poetry-core
    pythonRelaxDepsHook
  ];

  propagatedBuildInputs = [
    attrs
    click
    cryptography
  ];

  nativeCheckInputs = [
    pytestCheckHook
    pytest-mock
  ];

  postPatch = ''
    echo '_LIBNAME="${rhash}/lib/librhash.so"' > src/yumemi/_rhash/libname.py
  '';

  pythonImportsCheck = [
    "yumemi"
  ];

  pythonRelaxDeps = [
    "cryptography"
  ];

  postInstall = ''
    installShellCompletion --cmd yumemi \
      --bash <(_YUMEMI_COMPLETE=bash_source $out/bin/yumemi) \
      --zsh <(_YUMEMI_COMPLETE=zsh_source $out/bin/yumemi) \
      --fish <(_YUMEMI_COMPLETE=fish_source $out/bin/yumemi)
  '';

  meta = {
    description = pyproject.tool.poetry.description;
    homepage = pyproject.tool.poetry.repository;
    license = lib.licenses.mit;
  };
}
