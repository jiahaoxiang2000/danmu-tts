# Danmu TTS Server

A high-performance Text-to-Speech server designed for live streaming with multiple backend options to balance quality and speed.

## Installation

### Using Nix Flakes (Recommended for NixOS users)

#### Quick Run
```bash
# Run directly from GitHub
nix run github:jiahaoxiang2000/danmu-tts
```

#### Install to Profile
```bash
# Install to your user profile
nix profile install github:jiahaoxiang2000/danmu-tts

# Run the server
danmu-tts
```

#### Build Locally
```bash
# Clone and build
git clone https://github.com/jiahaoxiang2000/danmu-tts.git
cd danmu-tts
nix build
./result/bin/danmu-tts
```

#### Development Environment
```bash
# Enter development shell with all dependencies
nix develop

# Or run directly
nix develop -c danmu-tts
```

#### Add to NixOS System Configuration

Add to your `flake.nix`:
```nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    danmu-tts.url = "github:jiahaoxiang2000/danmu-tts";
  };

  outputs = { self, nixpkgs, danmu-tts }: {
    nixosConfigurations.your-hostname = nixpkgs.lib.nixosSystem {
      modules = [
        {
          environment.systemPackages = [
            danmu-tts.packages.x86_64-linux.default
          ];
        }
      ];
    };
  };
}
```

Or add to your `configuration.nix`:
```nix
{
  # Add this to your imports or let bindings
  danmu-tts = builtins.getFlake "github:jiahaoxiang2000/danmu-tts";

  environment.systemPackages = [
    danmu-tts.packages.x86_64-linux.default
  ];
}
```
