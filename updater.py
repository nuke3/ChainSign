import json
import os
import sys
import requests

from PySide2 import QtCore


def get_git_rev():
    return open('.git/' + (open('.git/HEAD').read().strip().split(': ')[1])).read()[:7]  # noqa


def get_bundle_rev():
    return open(os.path.join(sys._MEIPASS, 'build_id.txt')).read().decode('utf-8').strip()  # noqa pylint: disable=no-member,protected-access


def check_updates(rev, target_mime='application/x-ms-dos-executable'):
    tags = requests.get('https://api.github.com/repos/nuke3/ChainSign/tags').json()
    rev_tag = next((t['name'] for t in tags if t['commit']['sha'].startswith(rev)), None)

    if not rev_tag:
        return None

    releases = requests.get('https://api.github.com/repos/nuke3/ChainSign/releases').json()
    rel = next((r for r in releases if r['tag_name'] == rev_tag), None)

    if not rel:
        return None

    if rel['prerelease']:
        latest = releases[0]
    else:
        latest = next((r for r in releases if not r['prerelease']), rel)

    if latest['id'] != rel['id']:
        binary_url = next((
            a['browser_download_url'] for a in latest['assets']
            if a['content_type'] == target_mime
        ), None)
        return {
            'latest': latest,
            'current': rel,
            'binary_url': binary_url,
            }
    return {
        'latest': latest,
        'current': rel,
        }


class UpdateCheckerThread(QtCore.QThread):
    response = QtCore.Signal(str)  # FIXME: this shouldn't throw json...

    def run(self):
        try:
            try:
                rev = get_bundle_rev()
            except Exception as exc:  # pylint: disable=broad-except
                print(str(exc))
                rev = get_git_rev()

            resp = check_updates(rev)
        except Exception as exc:  # pylint: disable=broad-except
            resp = {"error": str(exc)}

        self.response.emit(json.dumps(resp))
