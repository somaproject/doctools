
import somatex


graphicstext = """

this is some test text
and this is some more text
and this is some more text
\includegraphics[width=3in]{silly.svg}
and this continues to be more text and this continues to be more text and this continues to be more text and this continues to be more text

"""

print somatex.genGraphicsDeps(graphicstext, "BUILD")

