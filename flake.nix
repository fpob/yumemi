{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    flake-compat = {
      url = "github:edolstra/flake-compat";
      flake = false;
    };
  };

  outputs = { self, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            pkgs.poetry
            pkgs.python3
          ];
          LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
            pkgs.rhash
          ];
        };

        formatter = pkgs.nixpkgs-fmt;

        packages = rec {
          default = yumemi;
          yumemi =
            let
              pyproject = builtins.fromTOML (builtins.readFile ./pyproject.toml);
            in
            pkgs.python3Packages.buildPythonPackage rec {
              pname = pyproject.tool.poetry.name;
              version = pyproject.tool.poetry.version;
              format = "pyproject";

              src = ./.;

              nativeBuildInputs = [
                pkgs.installShellFiles
                pkgs.python3Packages.poetry-core
                pkgs.python3Packages.pythonRelaxDepsHook
              ];

              propagatedBuildInputs = [
                pkgs.python3Packages.attrs
                pkgs.python3Packages.click
                pkgs.python3Packages.cryptography
              ];

              nativeCheckInputs = [
                pkgs.python3Packages.pytestCheckHook
                pkgs.python3Packages.pytest-mock
              ];

              postPatch = ''
                echo '_LIBNAME="${pkgs.rhash}/lib/librhash.so"' > src/yumemi/_rhash/libname.py
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
                license = pkgs.lib.licenses.mit;
              };
            };
        };

        checks = {
          yumemi = pkgs.runCommand "yumemi-test"
            {
              buildInputs = [ self.packages.${system}.yumemi ];
            }
            ''
              yumemi --help
              touch $out
            '';
        };
      }
    );
}
