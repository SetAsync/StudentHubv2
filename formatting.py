from markdown import Markdown
from markupsafe import Markup

def render_markdown(md_text):
    md = Markdown(
        extensions=['fenced_code', 'codehilite'],
        extension_configs={
            'codehilite': {
                'css_class': 'highlight'  # or 'codehilite' if you prefer
            }
        }
    )
    return Markup(md.convert(md_text))  # ✅ this takes just 1 argument
