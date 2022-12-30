{
  description = "Simple Static site generator for a recipe website";

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }: flake-utils.lib.eachDefaultSystem
    (system:
      let pkgs = nixpkgs.legacyPackages.${system}; in
      rec {
        packages.apicius_parser = pkgs.python3Packages.buildPythonPackage rec {
          pname = "apicius_parser";
          version = "0.1.0";
          src = ./.;
          propagatedBuildInputs = with pkgs.python3Packages; [
            CommonMark
            beautifulsoup4
            werkzeug
          ];
          format = "other";
          dontBuild = true;
          dontConfigure = true;
          installPhase = let pythonPackages = "$out/${pkgs.python3Packages.python.sitePackages}"; in ''
            mkdir -p ${pythonPackages}/recipe_parser
            install -Dm 0644 $src/src/recipe_parser.py ${pythonPackages}/recipe_parser/__init__.py
            install -Dm 0644 $src/src/html_template.html ${pythonPackages}/recipe_parser/html_template.html
          '';
        };
        packages.apicius_app = let executable_name="apicius"; in pkgs.python3Packages.buildPythonApplication rec {
          pname = "apicius_app";
          version = "0.1.0";
          src = ./.;
          propagatedBuildInputs = with pkgs.python3Packages; [
            CommonMark
            beautifulsoup4
            werkzeug
            self.packages.${system}.apicius_parser
          ];
          format = "other";
          dontBuild = true;
          dontConfigure = true;
          installPhase =  ''
            install -Dm 0755 $src/src/build_web.py $out/bin/build_web.py
            ln -s $out/bin/build_web.py $out/bin/${executable_name}
          '';
          meta = {
            description = "Apicius is a simple static site generator for recipe collections stored in markdown";
            mainProgram = "${executable_name}";
          };
        };
        packages.apicius_default_theme = pkgs.stdenv.mkDerivation {
          pname = "apicius_default_theme";
          version = "2022-12-30";
          src = ./.;
          installPhase = ''
            mkdir -p $out
            cp script.js theme.css $out
          '';
        };
        packages.default = self.packages.${system}.apicius_app;

        hydraJobs.apicius_app = self.packages.${system}.default;
      }
  );

}
