{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    flake-compat = {
      url = "github:edolstra/flake-compat";
      flake = false;
    };
    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, pyproject-nix, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        python = pkgs.python3;

      in
      {
        devShells.default = pkgs.mkShell {
          packages = [
            pkgs.uv
            python
          ];
          env = {
            UV_PYTHON_DOWNLOADS = "never";
            LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
              pkgs.rhash
            ];
          };
        };

        formatter = pkgs.nixpkgs-fmt;

        packages = {
          default = self.packages.${system}.yumemi;
          yumemi =
            let
              project = pyproject-nix.lib.project.loadPyproject {
                projectRoot =
                  let
                    fs = pkgs.lib.fileset;
                  in
                  fs.toSource {
                    root = ./.;
                    fileset = fs.intersection
                      (fs.gitTracked ./.)
                      (fs.unions [
                        ./pyproject.toml
                        ./README.rst
                        ./src
                        ./tests
                      ]);
                  };
              };
              attrs = project.renderers.buildPythonPackage { inherit python; } // {
                nativeBuildInputs = [
                  pkgs.installShellFiles
                ];
                postPatch = ''
                  echo '_LIBNAME="${pkgs.rhash}/lib/librhash.so"' > src/yumemi/_rhash/libname.py
                '';
                postInstall = ''
                  installShellCompletion --cmd yumemi \
                    --bash <(_YUMEMI_COMPLETE=bash_source $out/bin/yumemi) \
                    --zsh <(_YUMEMI_COMPLETE=zsh_source $out/bin/yumemi) \
                    --fish <(_YUMEMI_COMPLETE=fish_source $out/bin/yumemi)
                '';
                nativeCheckInputs = [
                  python.pkgs.pytestCheckHook
                  python.pkgs.pytest-mock
                ];
              };
            in
            python.pkgs.buildPythonPackage attrs;
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
