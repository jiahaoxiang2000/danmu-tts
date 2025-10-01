{
  description = "Danmu TTS Server - High-performance TTS server for live streaming";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, pyproject-nix, uv2nix, pyproject-build-systems }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        # Load the workspace from uv.lock
        workspace = uv2nix.lib.workspace.loadWorkspace { workspaceRoot = ./.; };

        # Create the overlay
        overlay = workspace.mkPyprojectOverlay {
          sourcePreference = "wheel";
        };

        # Extend Python package set with pyproject-build-systems and workspace overlay
        pythonSet = pkgs.callPackage pyproject-nix.build.packages {
          python = pkgs.python312;
        };

        # Apply overlays
        python = pythonSet.overrideScope (
          pkgs.lib.composeManyExtensions [
            pyproject-build-systems.overlays.default
            overlay
          ]
        );

        # Create virtual environment
        venv = python.mkVirtualEnv "danmu-tts-env" workspace.deps.default;

        # Development virtual environment with dev dependencies
        devVenv = python.mkVirtualEnv "danmu-tts-dev-env" (workspace.deps.default // workspace.deps.dev);

      in
      {
        packages = {
          default = venv;
          danmu-tts = venv;
        };

        apps = {
          default = {
            type = "app";
            program = "${venv}/bin/danmu-tts";
          };
        };

        devShells.default = pkgs.mkShell {
          buildInputs = [
            devVenv
            pkgs.uv
          ];

          shellHook = ''
            echo "Danmu TTS development environment"
            echo "Run 'danmu-tts' to start the server"
            echo "Python environment: ${devVenv}"
          '';
        };

        # For CI/CD and caching
        checks = {
          build = venv;
        };
      }
    );
}
