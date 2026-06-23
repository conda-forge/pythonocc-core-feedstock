cd test
REM Skip the display/OpenGL side-effect tests: they create on-screen OpenGL
REM windows, which the headless conda-forge Windows CI agent cannot do
REM (OpenGl_Window::CreateWindow: SetPixelFormat failed / wglMakeCurrent
REM failed). This affects every backend (tk and the Qt backends alike), in
REM particular re-initializing a second display. Linux already skips this
REM suite via a skipif marker; do the same on Windows.
pytest -sv --ignore=test_display_sideeffects.py
