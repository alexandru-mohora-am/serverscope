# -*- coding: utf-8 -*-

"""
Serverscope.io benchmark tool
"""

import os
import platform
import tempfile
import shutil

from .cli import get_parser
from .benchmarks import get_selected_benchmark_classes
from .utils import Color as c, get_geo_info, post_results
from .server import get_server_specs

from six import print_


if __name__ == '__main__':
    devnull = open(os.devnull, 'w')

    args = get_parser()

    payload = {
        "email": args["email"], "plan": args["plan"], "locale": args["locale"]}
    payload["os"] = platform.dist()

    try:
        tmp_dir = tempfile.mkdtemp(prefix='serverscope-')
        os.chdir(tmp_dir)

        payload['geo'] = get_geo_info()
        payload['specs'] = get_server_specs(devnull)

        benchmarks = {}
        print_("", end=c.RESET)

        for BenchmarkClass in get_selected_benchmark_classes(args.get('include', None)):
            benchmark = BenchmarkClass(specs=payload['specs'], stdout=devnull)
            benchmark.download()
            result = benchmark.run()
            if result:
                benchmarks[benchmark.code] = result

        payload['benchmarks'] = benchmarks

        if payload.get('benchmarks', None):
            print_(c.GREEN + c.BOLD)
            print_("All done! Submitting the results..." + c.RESET)
            post_results(payload, devnull)
    finally:
        devnull.close()
        shutil.rmtree(tmp_dir)
