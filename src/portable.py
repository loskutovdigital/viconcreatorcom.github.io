"""Make authored static HTML and CSS work under any GitHub Pages base path."""
import posixpath
import re
from urllib.parse import urlsplit


def rewrite_site(root):
    def relative(value, parent):
        if not value.startswith('/') or value.startswith('//'):
            return value
        url = urlsplit(value)
        path = posixpath.relpath(url.path.lstrip('/') or '.', parent or '.')
        if url.path.endswith('/'):
            path = './' if path == '.' else path + '/'
        return path + ('?' + url.query if url.query else '') + ('#' + url.fragment if url.fragment else '')

    for file in root.rglob('*.html'):
        parent = file.parent.relative_to(root).as_posix()
        source = file.read_text()
        source = re.sub(r'\b(href|src|poster|data-full|action)="([^"]*)"',
                        lambda m: f'{m[1]}="{relative(m[2], parent)}"', source)
        def srcset(match):
            entries = []
            for item in match[2].split(','):
                parts = item.strip().split()
                if parts:
                    parts[0] = relative(parts[0], parent)
                entries.append(' '.join(parts))
            return match[1] + '="' + ', '.join(entries) + '"'
        source = re.sub(r'\b(srcset|imagesrcset)="([^"]*)"', srcset, source)
        file.write_text(source)
    for file in root.rglob('*.css'):
        parent = file.parent.relative_to(root).as_posix()
        source = re.sub(r'url\(([\'"]?)(/[^)\'" ]+)\1\)',
                        lambda m: 'url(' + m[1] + relative(m[2], parent) + m[1] + ')', file.read_text())
        file.write_text(source)
