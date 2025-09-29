{
  description = "Danmu TTS Server - High-performance TTS server for live streaming";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        python = pkgs.python312;

        # Build edge-tts from PyPI since it's not in nixpkgs
        edge-tts = python.pkgs.buildPythonPackage rec {
          pname = "edge-tts";
          version = "6.1.0";
          format = "setuptools";

          src = python.pkgs.fetchPypi {
            inherit pname version;
            sha256 = "sha256-FvP9tZV5aw5n1g8AcObgs1xJYNGYzPYyF3Cxf2PJYoM=";
          };

          propagatedBuildInputs = with python.pkgs; [
            aiohttp
            certifi
          ];

          # Skip tests as they require network access
          doCheck = false;

          meta = with pkgs.lib; {
            description = "Use Microsoft Edge's online text-to-speech service from Python";
            homepage = "https://github.com/rany2/edge-tts";
            license = licenses.gpl3Plus;
          };
        };

        danmu-tts = python.pkgs.buildPythonApplication rec {
          pname = "danmu-tts";
          version = "1.0.0";
          format = "pyproject";

          src = ./.;

          nativeBuildInputs = with python.pkgs; [
            hatchling
          ];

          propagatedBuildInputs = with python.pkgs; [
            fastapi
            uvicorn
            edge-tts
            pydantic
            python-multipart
            aiofiles
          ];

          nativeCheckInputs = with python.pkgs; [
            pytest
            pytest-asyncio
            httpx
          ];

          # Skip tests during build since they might require network access
          doCheck = false;

          meta = with pkgs.lib; {
            description = "High-performance TTS server for live streaming";
            homepage = "https://github.com/jiahaoxiang2000/danmu-tts";
            license = licenses.mit;
            maintainers = with maintainers; [ ];
            platforms = platforms.linux ++ platforms.darwin;
          };
        };

      in
      {
        packages = {
          default = danmu-tts;
          danmu-tts = danmu-tts;
        };

        apps = {
          default = {
            type = "app";
            program = "${danmu-tts}/bin/danmu-tts";
          };
        };

        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            python
            python.pkgs.pip
            python.pkgs.virtualenv
            python.pkgs.hatchling
            python.pkgs.fastapi
            python.pkgs.uvicorn
            python.pkgs.pydantic
            python.pkgs.python-multipart
            python.pkgs.aiofiles
            python.pkgs.pytest
            python.pkgs.pytest-asyncio
            python.pkgs.httpx
            edge-tts
          ];

          shellHook = ''
            echo "Danmu TTS development environment"
            echo "Run 'danmu-tts' to start the server"
          '';
        };

        # For CI/CD and caching
        checks = {
          build = danmu-tts;
        };
      }
    );
}