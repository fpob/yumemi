{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    flake-compat = {
      url = "github:edolstra/flake-compat";
      flake = false;
    };
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryApplication;
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

        packages = {
          default = self.packages.${system}.yumemi;
          yumemi = mkPoetryApplication {
            projectDir =
              let
                fs = pkgs.lib.fileset;
              in
              fs.toSource {
                root = ./.;
                fileset = fs.intersection
                  (fs.gitTracked ./.)
                  (fs.unions [
                    ./docs
                    ./LICENSE
                    ./poetry.lock
                    ./pyproject.toml
                    ./README.rst
                    ./src
                    ./tests
                  ]);
              };
            preferWheels = true;
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
