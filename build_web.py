import argparse
import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
WEB_SOURCE_DIR = PROJECT_ROOT / 'build' / 'web-source'
WEB_BUILD_DIR = WEB_SOURCE_DIR / 'build' / 'web'
PAGES_DIR = PROJECT_ROOT / 'docs'
WEB_TEMPLATE = PROJECT_ROOT / 'web_template.tmpl'
FAVICON = PROJECT_ROOT / 'favicon.png'
MINIMUM_PYTHON = (3, 9)
WEB_ITEMS = [
    'code',
    'data',
    'font.ttf',
    'images',
    'main.py',
]
WEB_IGNORES = {
    'data': shutil.ignore_patterns(
        'level.tiled-session',
        'level.tmx',
        'Objects.tsx',
        'Ground.tsx',
        'industrial-assets.tsx',
        'TX Village Props.png',
        'TX Tileset Ground.png',
    ),
    'images': shutil.ignore_patterns(
        'aseprite',
        'senior',
        'btn_large',
    ),
}


def check_python_version():
    if sys.version_info < MINIMUM_PYTHON:
        current = '.'.join(str(part) for part in sys.version_info[:3])
        required = '.'.join(str(part) for part in MINIMUM_PYTHON)
        raise SystemExit(
            f'Pygbag 0.9.3 requires Python {required} or newer; current Python is {current}.\n'
            'Create the web environment with Python 3.12 and run:\n'
            '  PYENV_VERSION=3.12.0 python -m venv .venv-web\n'
            '  .venv-web/bin/python -m pip install -r requirements.txt\n'
            '  .venv-web/bin/python build_web.py --serve'
        )


def prepare_web_source():
    if WEB_SOURCE_DIR.exists():
        shutil.rmtree(WEB_SOURCE_DIR)
    WEB_SOURCE_DIR.mkdir(parents=True)

    for item in WEB_ITEMS:
        source = PROJECT_ROOT / item
        destination = WEB_SOURCE_DIR / item
        if source.is_dir():
            ignore = WEB_IGNORES.get(
                item,
                shutil.ignore_patterns('__pycache__', '*.pyc'),
            )
            shutil.copytree(source, destination, ignore=ignore)
        else:
            shutil.copy2(source, destination)


def build_pygbag():
    subprocess.run(
        [
            sys.executable,
            '-m',
            'pygbag',
            '--build',
            '--ume_block',
            '0',
            '--template',
            str(WEB_TEMPLATE),
            '--icon',
            str(FAVICON),
            str(WEB_SOURCE_DIR),
        ],
        check=True,
    )


def copy_pages(destination):
    source = WEB_BUILD_DIR
    if not source.exists():
        raise SystemExit(f'Pygbag build output was not found: {source}')

    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(
        source,
        destination,
        ignore=shutil.ignore_patterns('*.apk'),
    )
    (destination / '.nojekyll').touch()


def main():
    check_python_version()

    parser = argparse.ArgumentParser(description='Build Bit Debugger for GitHub Pages with Pygbag.')
    parser.add_argument(
        '--serve',
        action='store_true',
        help='Start the local Pygbag server instead of only building static files.',
    )
    parser.add_argument(
        '--pages-dir',
        default=str(PAGES_DIR),
        help='Destination folder for GitHub Pages static files.',
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Local server port used with --serve (default: 8000).',
    )
    args = parser.parse_args()
    if args.serve and args.port != 8000:
        raise SystemExit(
            'Pygbag 0.9.3 requires port 8000 for its local WebAssembly package proxy.\n'
            'Run: .venv-web/bin/python build_web.py --serve'
        )

    prepare_web_source()

    if args.serve:
        subprocess.run(
            [
                sys.executable,
                '-m',
                'pygbag',
                '--ume_block',
                '0',
                '--template',
                str(WEB_TEMPLATE),
                '--icon',
                str(FAVICON),
                '--port',
                str(args.port),
                str(WEB_SOURCE_DIR),
            ],
            check=True,
        )
        return

    build_pygbag()
    destination = Path(args.pages_dir)
    copy_pages(destination)
    print(f'GitHub Pages files written to {destination}')


if __name__ == '__main__':
    main()
