{ pkgs ? import <nixpkgs> {} }:

let
  poetryEnv = pkgs.poetry2nix.mkPoetryEnv {
    projectDir = ./.;
  };
in pkgs.mkShell {

  buildInputs = [
    pkgs.poetry
    poetryEnv
  ];

  shellHook = 
    ''
    export FLASK_APP=ms365_accountcreator
    export FLASK_DEBUG=1  # to enable autoreload
    export MODE=debug

    flask create_db
    '';
}

