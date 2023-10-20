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

        packages =
          let
            callPythonPackage = pkgs.lib.callPackageWith (
              pkgs // pkgs.python3Packages // self.packages.${system}
            );
          in
          rec {
            default = yumemi;
            yumemi = callPythonPackage ./nix/yumemi.nix { };
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
