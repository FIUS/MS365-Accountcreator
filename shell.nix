let 
  nur_overlay = self: super: {
    nur = import (builtins.fetchTarball "https://github.com/nix-community/NUR/archive/master.tar.gz") {
      pkgs = super;
    };
  };

  python_overlay = self: super: {
    my_python = super.nur.repos.neumantm.pythonWithPipenv.override {
       myPythonDerivation = super.python37; 
       myPythonPackages = pp: with pp; [
         # Dev dependencies
         pylint
         autopep8
       
         # Native dependencies
         six
       ];
    };
  };
in
{ pkgs ? import <nixpkgs> { overlays = [ nur_overlay python_overlay ]; } }:
pkgs.mkShell {
  buildInputs = [
    pkgs.my_python
  ];

  shellHook = 
    ''
    function initPipenvIfNeeded {
      if ! pipenv --venv > /dev/null 2>&1 ;then
        pipenv install --dev
      fi
    }              

    function loadPipenv {
      export loadPipenvDepth=$(expr $loadPipenvDepth + 1) 
      initPipenvIfNeeded
      source "$(pipenv --venv)/bin/activate"
      if ! python -c "" ;then
        if [ $loadPipenvDepth -gt 3 ] ;then
          echo "Could not load pipenv after 3 tries."
          exit 1
        fi
        pipenv --rm
        loadPipenv
      fi
    } 

    loadPipenv || exit
    unset loadPipenvDepth

    export FLASK_APP=ms365_accountcreator
    export FLASK_DEBUG=1  # to enable autoreload
    export MODE=debug

    flask create_db
    '';
}

