from werkzeug.wrappers import Request, Response
from argparse import ArgumentParser, FileType
import json
import hmac
import subprocess as sp

if __name__ == '__main__':
    parser = ArgumentParser(description="Run a simple GitHub webhook server")
    parser.add_argument("-c", "--config", help="The path to the config.json file. (Default: server_config.json)",
                        default="server_config.json", type=FileType())
    args = parser.parse_args()
    config = json.load(args.config)

    @Request.application
    def application(request: Request):
        if request.path != config["push_path"]:
            return Response("Not found", status=404)
        if "X-Hub-Signature" not in request.headers:
            return Response("Invalid request", status=400)
        # TODO: Check content length before getting data
        content = request.data()
        correct_secret = hmac.digest(config["github_secret"], content, "sha1")
        if request.headers["X-Hub-Signature"] != correct_secret:
            return Response("Invalid request", status=400)

        # Secret looks good, we could now check the body, but let's keep it simple and just trigger a pull and rebuild
        sp.Popen(["./pull_and_build.sh", config["src_path"], config["dest_path"]])
        return Response()

    from werkzeug.serving import run_simple
    run_simple('localhost', config["port"], application)
