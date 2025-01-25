KEYS_STYLE = ['border-radius: 1em',
                                'color: #000',
                                'padding: 0em 1em',
                                'border: none',
                                'text-align: right',
                                'margin: 0em']

CONTENT_PORTAL_BOX_KEYS_STYLE = ['padding:0em',
                                'border:thin inset #0ff',
                                'color:#000']

BANNER_PORTAL_BOX_KEYS_STYLE = ['font-weight:bold',
                             'text-shadow: #333 .1em .1em .1em, #fff -.1em -.1em .1em',
                             'text-align: center',
                             'color: #000',
                             'margin: 0em',
                             'border-width: medium',
                             'padding:0.1em',
                             'font-size: 1em']

IGNORED_DIV_RULES = {
    "classes": ["mw-references-wrap", "subpagelist"],
    "ids": ["tradbox","toc"],
    "styles": [KEYS_STYLE,
               CONTENT_PORTAL_BOX_KEYS_STYLE,
               BANNER_PORTAL_BOX_KEYS_STYLE,
               "margin:1em 0em 2em 0em; padding:0.1em; border: none groove #fa5; border-radius:1em; background: #fda; background-image: linear-gradient(to top, #500 0%, #a50 10%, #fda 20% 80%, #fb7 90%, #fa5 100%); color: #fa5; text-align: center;",
               "padding-top:.5em;text-align:center;font-weight: bold; font-size: 150%;font-variant: small-caps;",
               "position:absolute; left:40px; top:2px; right:0px",
               "text-align: right; font-size: smaller;",
               "text-align:center;",
               "text-align:center"]
}

IGNORED_TABLE_RULES = {
    "classes": [],
    "ids": [],
    "styles": ["float: right; width:25%; max-width:30%; margin: 0.1em; overflow: auto; border: thick outset #C90; border-radius:1em; padding: 0.1em;background-color: #C90; background-color: rgba(255, 165, 0, 0.5); background-image: radial-gradient(rgba(255, 255, 255, 0.2),rgba(255, 165, 0, 0.5)); cellspacing: 0.01em; cellpadding:0.01em; vertical-align:center;",
               "border:1px solid #336600; font-size:90%; width:100%; text-align:center; clear:both;",
               "background-color: transparent;",
               "background-color: transparent",
               "margin:auto;",
               "margin:auto"]
}