

import DocbookElement


class LatexDoc:
    """
    code that handles putting in the header and footer, and finalizing
    the document
    """

    def __init__(self, filename):

        self.outfile = file(filename, 'w')
        
        pass

    def finalize(self, element):
        if isinstance(element, DocbookElement.Article):
            ## Treat as an article ##
            articleheader = r"""\documentclass{article}
            \usepackage{fullpage}
            \usepackage{graphicx}
            """
            self.outfile.write(articleheader)
            self.outfile.write("\\title{%s}\n"% element.title)
            self.outfile.write("\\author{%s}\n" % element.author)
            self.outfile.write("\\begin{document}\n")
            self.outfile.write("\\maketitle\n")
            self.outfile.write(element.to_latex())
            self.outfile.write("\\end{document}\n")


        self.outfile.close()

