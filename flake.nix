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
            projectDir = self;
            preferWheels = true;
            postPatch = ''
              echo '_LIBNAME="${pkgs.rhash}/lib/librhash.so"' > src/yumemi/_rhash/libname.py
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
