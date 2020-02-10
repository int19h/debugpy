# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root
# for license information.

from __future__ import absolute_import, division, print_function, unicode_literals

"""Script injected into the debuggee process during attach-to-PID."""

import os


__file__ = os.path.abspath(__file__)
_debugpy_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


# def attach(mode, address, log_dir=None, client_access_token=None):
def attach(setup):
    try:
        import sys

        if "threading" not in sys.modules:
            try:

                def on_warn(msg):
                    print(msg, file=sys.stderr)

                def on_exception(msg):
                    print(msg, file=sys.stderr)

                def on_critical(msg):
                    print(msg, file=sys.stderr)

                pydevd_attach_to_process_path = os.path.join(
                    _debugpy_dir,
                    "debugpy",
                    "_vendored",
                    "pydevd",
                    "pydevd_attach_to_process",
                )
                assert os.path.exists(pydevd_attach_to_process_path)
                sys.path.insert(0, pydevd_attach_to_process_path)

                # NOTE: that it's not a part of the pydevd PYTHONPATH
                import attach_script

                attach_script.fix_main_thread_id(
                    on_warn=on_warn, on_exception=on_exception, on_critical=on_critical
                )

                # NOTE: At this point it should be safe to remove this.
                sys.path.remove(pydevd_attach_to_process_path)
            except:
                import traceback

                traceback.print_exc()
                raise

        sys.path.insert(0, _debugpy_dir)
        try:
            import debugpy
            from debugpy.common import log
        finally:
            assert sys.path[0] == _debugpy_dir
            del sys.path[0]

        if setup["log_to"] is not None:
            debugpy.log_to(setup["log_to"])
        log.info("Configuring injected debugpy: {0!j}", setup)

        if setup["mode"] == "listen":
            debugpy.listen(setup["address"])
        elif setup["mode"] == "connect":
            debugpy.connect(
                setup["address"], access_token=setup["adapter_access_token"]
            )
        else:
            raise AssertionError(repr(setup))

    except:
        import traceback

        traceback.print_exc()
        raise log.exception()

    log.info("debugpy injected successfully")
