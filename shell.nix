{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {

  buildInputs = [
    (pkgs.poetry2nix.mkPoetryEnv {
      projectDir = ./.;
      pwd = ./.;
    })
  ];

}
