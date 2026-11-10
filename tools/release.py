#!/usr/bin/env python3
"""
Tag and publish the three version lines of the project (see VERSIONS.md).

    hardware  hardware/VERSION       tag hw-v<version>       STL zip, plate 3MF zip (with the print guide and the BOM),
                                                             the drilling template and the manuals (PDF), if present
    firmware  firmware/VERSION       tag fw-v<version>       zip: the MicroPython sources (tracked files only)
    product   product/product.json   tag product-v<version>  lock file plus the pinned hardware and firmware zips

For each line whose tag does not exist yet, the script creates an annotated tag and a GitHub Release with
its assets; the notes come from the CHANGELOG.md section "## [<tag>]". A new tag points at the commit being
released (HEAD: on CI, the head of the push that brought the new version to main). The notes and the tag
message also name the last commit that changed the line's files, when that is an earlier one. Tags on older
commits are not possible from the workflow: GitHub refuses to let its token create a ref on a commit whose
workflow files differ. A product release only goes out when product.json names a version, and only if the
pinned hardware and firmware tags exist and the hardware status is allowed.
When the hardware status rises for an existing tag (designed, printed, tested, field-proven), the title of
its release is updated.

    python tools/release.py --dry-run     show the plan and build the assets in a temporary folder (default)
    python tools/release.py --publish     create tags and releases (needs git push rights and the gh CLI, GH_TOKEN)

Standard library only (Python 3.11+); git and gh on the PATH.
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
import tomllib
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = 'https://github.com/ricricucit/kibble-dispenser'
STATUSES = ['designed', 'printed', 'tested', 'field-proven']
SEMVER = re.compile(r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(-[0-9A-Za-z.-]+)?(\+[0-9A-Za-z.-]+)?$')
SECRET_NAMES = {'secrets.py', 'config_local.py', 'secrets.yaml', '.env'}
SECRET_TEXT = re.compile(r'''(?i)\b(password|passwd|wifi_pass\w*|ssid|api_key|token|secret)\b\s*[:=]\s*['"][^'"\s]{3,}['"]''')


def git(*args, check=True):
    r = subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True)
    if check and r.returncode:
        sys.exit(f'git {" ".join(args)} failed: {r.stderr.strip()}')
    return r.stdout.strip()


def gh(*args, check=True):
    r = subprocess.run(['gh', *args], cwd=ROOT, capture_output=True, text=True)
    if check and r.returncode:
        sys.exit(f'gh {" ".join(args)} failed: {r.stderr.strip()}')
    return r


def read_toml(path):
    return tomllib.loads((ROOT / path).read_text(encoding='utf-8'))


def tracked(*paths, at='HEAD'):
    """Files under paths in the tree of commit `at` (only committed files, so nothing ignored or local)."""
    return [p for p in git('ls-tree', '-r', '-z', '--name-only', at, '--', *paths).split('\0') if p]


def blob(path, at):
    r = subprocess.run(['git', 'show', f'{at}:{path}'], cwd=ROOT, capture_output=True)
    if r.returncode:
        sys.exit(f'{path} not found in {at[:7]}')
    return r.stdout


def last_commit(paths, exclude):
    args = ['log', '-1', '--format=%H', '--', *paths] + [f':(exclude){e}' for e in exclude]
    sha = git(*args)
    if not sha:
        sys.exit(f'no commit touches {paths}')
    return sha


def remote_tags():
    out = git('ls-remote', '--tags', 'origin', check=False)
    tags = {line.split('refs/tags/', 1)[1].removesuffix('^{}') for line in out.splitlines() if 'refs/tags/' in line}
    return tags | set(git('tag', '-l').split())


def changelog_section(tag):
    text = (ROOT / 'CHANGELOG.md').read_text(encoding='utf-8')
    m = re.search(r'^## \[' + re.escape(tag) + r'\][^\n]*\n(.*?)(?=^## |\Z)', text, flags=re.M | re.S)
    return m.group(1).strip() if m else ''


def safe_name(s):
    return re.sub(r'[^A-Za-z0-9._-]', '_', s)


def write_zip(path, prefix, files, extra, when, at):
    """files: repository paths, read from commit `at`; extra: {name: text}. Fixed timestamps (that commit's date)."""
    stamp = tuple(int(x) for x in when.split('-')) + (0, 0, 0)
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, data in [(f, blob(f, at)) for f in sorted(set(files))] + [(n, t.encode()) for n, t in extra.items()]:
            zi = zipfile.ZipInfo(f'{prefix}/{name}', date_time=stamp)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o644 << 16
            z.writestr(zi, data, compresslevel=9)
    return path


# ---------------------------------------------------------------- the three lines
def hardware_line():
    v = read_toml('hardware/VERSION')
    version, status, design = v['version'], v['status'], v['design'].rstrip('/')
    if not SEMVER.match(version) or status not in STATUSES:
        sys.exit(f'hardware/VERSION: bad version {version!r} or status {status!r}')
    if not (ROOT / design).is_dir():
        sys.exit(f'hardware/VERSION: design folder {design} not found')
    major, minor = version.split('.')[:2]
    if not design.endswith((f'v{major}', f'v{major}.{minor}')):
        print(f'note: hardware {version} with design folder {design}')
    content = last_commit(['hardware'], ['hardware/VERSION'])
    target = git('rev-parse', 'HEAD')

    def assets(out, when):
        """STL zip, plate 3MF zip, drilling template and manuals; each zip carries a VERSION.txt and the licences."""
        at = rel['target']
        tag = f'hw-v{version}'
        base = f'kibble-dispenser-{safe_name(tag)}'
        manifest = (f'Kibble Dispenser Outdoor, hardware {version}\nStatus: {status}\nDesign: {design}\n'
                    f'Commit: {target}\nSource: {REPO}/tree/{tag}\n')
        docs = tracked(f'{design}/README.md', f'{design}/bom.json', 'docs/BOM.md', at=at)
        plates = tracked(f'{design}/plates', at=at)
        guide = [f for f in plates if f.endswith(('plates/README.md', 'plates/summary.json'))]
        lic = {'cern': tracked('LICENSES/CERN-OHL-P-2.0.txt', at=at), 'cc': tracked('LICENSES/CC-BY-4.0.txt', at=at)}
        # print-ready STL files: the print package (plates/stl) when there is one, otherwise the design's stl/ folder
        stl = [f for f in plates if '/plates/stl/' in f and f.endswith('.stl')] or tracked(f'{design}/stl', at=at)
        mf = [f for f in plates if f.endswith('.3mf') and '/tools/' not in f]
        res = []
        if stl:
            res.append(write_zip(out / f'{base}-stl.zip', f'{base}-stl', stl + docs + guide + lic['cern'] + lic['cc'],
                                 {'VERSION.txt': manifest}, when, at))
        if mf:
            res.append(write_zip(out / f'{base}-plates-3mf.zip', f'{base}-plates-3mf', mf + docs + guide + lic['cern'] + lic['cc'],
                                 {'VERSION.txt': manifest}, when, at))
        # single PDFs: the drilling template of the design and the manuals in docs/manual/
        pdfs = [f for f in tracked(f'{design}/template', at=at) if f.endswith('.pdf')]
        names = {f: 'kibble-dispenser-drilling-template.pdf' for f in pdfs[:1]}
        names.update({f: Path(f).name for f in tracked('docs/manual', at=at) if f.endswith('.pdf')})
        for f, name in names.items():
            dst = out / name
            dst.write_bytes(blob(f, at))
            res.append(dst)
        return res

    rel = dict(line='hardware', tag=f'hw-v{version}', version=version, status=status, target=target, content=content, paths='hardware/ (VERSION aside)',
                title=f'Hardware {version} · {status}', prerelease=status in ('designed', 'printed'),
                intro=(f'Hardware line, design `{design}`. Status: **{status}**'
                       + (' (designed and checked in CAD, not yet printed or tested).' if status == 'designed' else '.')),
                assets=assets)
    return rel


def firmware_line():
    v = read_toml('firmware/VERSION')
    version, source = v['version'], v['source'].rstrip('/')
    if not SEMVER.match(version):
        sys.exit(f'firmware/VERSION: bad version {version!r}')
    upstream = (ROOT / source / 'VERSION').read_text(encoding='utf-8').strip()
    if version.split('+')[0].split('-')[0] != upstream or v.get('upstream_version') != upstream:
        sys.exit(f'firmware/VERSION {version!r} does not match {source}/VERSION {upstream!r}')
    content = last_commit([source], [])
    target = git('rev-parse', 'HEAD')

    def assets(out, when):
        at = rel['target']
        files = tracked(source, 'firmware/README.md', 'LICENSES/MIT.txt', at=at)
        for f in files:
            name = Path(f).name
            if name in SECRET_NAMES or name.endswith('.env'):
                sys.exit(f'refusing to package {f}: looks like a secrets file')
            if f.endswith(('.py', '.yaml', '.yml', '.json', '.toml', '.cfg', '.ini')):
                hit = SECRET_TEXT.search(blob(f, at).decode('utf-8', errors='replace'))
                if hit:
                    sys.exit(f'refusing to package {f}: possible secret ({hit.group(1)} = ...)')
        tag = f'fw-v{version}'
        manifest = (f'Kibble Dispenser firmware {version}\nSource: {source} (MicroPython)\nCommit: {target}\n'
                    f'Note: {v.get("note", "")}\n')
        return [write_zip(out / f'kibble-dispenser-{safe_name(tag)}.zip', f'kibble-dispenser-{safe_name(tag)}', files,
                          {'VERSION.txt': manifest, 'firmware/VERSION': (ROOT / 'firmware/VERSION').read_text(encoding='utf-8')},
                          when, at)]

    rel = dict(line='firmware', tag=f'fw-v{version}', version=version, status=None, target=target, content=content, paths=f'{source}/',
                title=f'Firmware {version}', prerelease=version.startswith('0.') or '-' in version or '+' in version,
                intro=(f'MicroPython firmware from `{source}`. {v.get("note", "").capitalize()}.'
                       ' The firmware actually flashed on the bench board may differ.'),
                assets=assets)
    return rel


def product_line(tags, hw):
    p = json.loads((ROOT / 'product/product.json').read_text(encoding='utf-8'))
    version = p.get('version')
    if version in (None, '', 'unreleased'):
        return None
    if not SEMVER.match(version):
        sys.exit(f'product/product.json: bad version {version!r}')
    hw_tag, fw_tag = p['hardware'].get('tag'), p['firmware'].get('tag')
    missing = [t for t in (hw_tag, fw_tag) if not t or t not in tags]
    if missing:
        sys.exit(f'product {version} pins tags that do not exist yet: {missing}')
    status = hw['status'] if hw_tag == hw['tag'] else gh_status(hw_tag)
    if status not in p['hardware'].get('required_status', STATUSES):
        sys.exit(f'product {version} needs hardware status {p["hardware"]["required_status"]}, {hw_tag} is {status!r}')
    target = git('rev-parse', 'HEAD')

    def assets(out, when):
        res = [write_zip(out / f'kibble-dispenser-product-v{safe_name(version)}-lock.zip', f'kibble-dispenser-product-v{safe_name(version)}',
                         ['product/product.json', 'product/README.md'] + ([p['bom']] if p.get('bom') else [])
                         + ([p['manual']['file']] if p['manual'].get('file') else []), {}, when, target)]
        for t in (hw_tag, fw_tag):   # the pinned assets, downloaded from their own releases
            r = gh('release', 'download', t, '--dir', str(out), '--clobber', check=False)
            if r.returncode:
                print(f'note: could not download the assets of {t}: {r.stderr.strip()}')
        return res + [f for f in sorted(out.iterdir()) if f.suffix in ('.zip', '.pdf') and f not in res]

    return dict(line='product', tag=f'product-v{version}', version=version, status=None, target=target, content=target, paths='product/',
                title=f'{p["name"]} {version}', prerelease=False,
                intro=f'Product release: hardware `{hw_tag}`, firmware `{fw_tag}`, manual {p["manual"].get("version") or "none"}.',
                assets=assets)


def gh_status(tag):
    r = gh('release', 'view', tag, '--json', 'name', '--jq', '.name', check=False)
    m = re.search(r'· (\S+)$', r.stdout.strip())
    return m.group(1) if m else None


# ---------------------------------------------------------------- main
def provenance(rel):
    same = rel['content'] == rel['target']
    return (f'Tagged commit: {rel["target"][:7]}.' if same else
            f'Tagged commit: {rel["target"][:7]}; the files in {rel["paths"]} last changed in {rel["content"][:7]} '
            f'and are the same in both.')


def notes_for(rel):
    body = changelog_section(rel['tag']) or f'No CHANGELOG section for {rel["tag"]} yet; see {REPO}/blob/main/CHANGELOG.md.'
    return (f'{rel["intro"]}\n\n{provenance(rel)} Version lines and compatibility: '
            f'{REPO}/blob/main/VERSIONS.md\n\n{body}\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--publish', action='store_true', help='create tags and releases')
    ap.add_argument('--dry-run', action='store_true', help='only show the plan (default)')
    a = ap.parse_args()
    publish = a.publish and not a.dry_run
    tags = remote_tags()
    hw, fw = hardware_line(), firmware_line()
    lines = [hw, fw]
    prod = product_line(tags, hw)
    if prod:
        lines.append(prod)
    else:
        print('product: unreleased (product/product.json), nothing to tag')
    work = Path(tempfile.mkdtemp(prefix='kd-release-'))
    for rel in lines:
        tag, target = rel['tag'], rel['target']
        has_tag = tag in tags
        if has_tag:
            view = gh('release', 'view', tag, '--json', 'name', '--jq', '.name', check=False)
            if view.returncode == 0:
                cur = view.stdout.strip()
                if rel['line'] == 'hardware' and cur and cur != rel['title']:
                    print(f'{tag}: release title "{cur}" becomes "{rel["title"]}"')
                    if publish:
                        gh('release', 'edit', tag, '--title', rel['title'], f'--prerelease={str(rel["prerelease"]).lower()}')
                else:
                    print(f'{tag}: exists, nothing to do')
                continue
            if 'not found' not in (view.stderr or '').lower():
                print(f'{tag}: tag exists; cannot check its release ({view.stderr.strip()[:80]}), skipped')
                continue
            target = git('rev-list', '-n', '1', tag)
            rel['target'] = target
        when = git('log', '-1', '--format=%cs', target)
        out = work / safe_name(tag)
        out.mkdir()
        assets = rel['assets'](out, when)
        notes = notes_for(rel)
        print(f'{tag}: {"tag exists, release MISSING" if has_tag else "NEW"} on {target[:7]} ({git("log", "-1", "--format=%s", target)})')
        if rel['content'] != target:
            print(f'  content last changed in {rel["content"][:7]} ({git("log", "-1", "--format=%s", rel["content"])})')
        print(f'  title: {rel["title"]}{"  [pre-release]" if rel["prerelease"] else ""}')
        for f in assets:
            if f.suffix == '.zip':
                with zipfile.ZipFile(f) as z:
                    print(f'  asset: {f.name}  {f.stat().st_size / 1e6:.1f} MB, {len(z.namelist())} files')
            else:
                print(f'  asset: {f.name}  {f.stat().st_size / 1e6:.1f} MB')
        print('  notes:\n' + '\n'.join('    ' + line for line in notes.splitlines()[:12]) + ('\n    ...' if notes.count('\n') > 12 else ''))
        if not publish:
            continue
        if not has_tag:
            msg = f'{rel["title"]}\n\n{rel["intro"]}\n\n{provenance(rel)}\n'
            git('tag', '-a', tag, target, '-m', msg)
            git('push', 'origin', f'refs/tags/{tag}')
        nf = out / 'NOTES.md'
        nf.write_text(notes, encoding='utf-8')
        args = ['release', 'create', tag, *map(str, assets), '--verify-tag', '--title', rel['title'], '--notes-file', str(nf)]
        if rel['prerelease']:
            args.append('--prerelease')
        gh(*args)
        print(f'  published {REPO}/releases/tag/{tag}')
    if not publish:
        print(f'dry run: nothing tagged; assets in {work}')


if __name__ == '__main__':
    main()
