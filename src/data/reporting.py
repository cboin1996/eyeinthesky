import pylatex 
import logging 
from pylatex import Document, Section, Subsection, Tabular, Table, NoEscape, Command
from pylatex import Math, TikZ, Axis, Plot, Figure, Matrix, Alignat, Package
from pylatex import Document, PageStyle, Head, MiniPage, Foot, LargeText, \
    MediumText, LineBreak, simple_page_number
from pylatex.utils import bold
from pylatex.utils import italic
import os
import datetime

from src import util, config
from src.io import files

logger = logging.getLogger(__name__)
def initialize(data_folder):
    root_report_dir = config.reporting_dir
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    pretty_timestamp = datetime.datetime.now().strftime("%Y %B %d, %H:%M:%S")
    logger.info(f"Launching latex creator for report {timestamp}.")
    out_path = os.path.join(config.reporting_dir, timestamp)

    util.copy_tree(data_folder, out_path)
    return timestamp, out_path, pretty_timestamp

def create_latex(data_folder, open_when_done, author="Christian Boin", title="Add Title", company="JMP",
                  logo_fpath=None):
    """
    Create a latex pdf
    Arguments:
        data_folder : The folder of the data to generate the report from
        open_when_done : whether to open the pdf when done
        author : the author of the report
    """
    timestamp, report_dir, pretty_timestamp = initialize(data_folder)
    logger.info("Beginning Report Generation.")
    report_name = os.path.join(report_dir, timestamp)

    section_paths = util.browse_dir(report_dir, level=1)
    geometry_options = {"tmargin": "2cm", "lmargin": "2cm"}

    doc = Document(geometry_options=geometry_options)
    doc.packages.append(Package('float'))
    doc.packages.append(Package('booktabs'))
    doc.packages.append(Package('hyperref'))

    doc = generate_header(doc, title=title, author=author, company=company, date=pretty_timestamp,
                          logo_fpath=logo_fpath)

    doc.append(Command('tableofcontents'))
    doc.append(Command('listoffigures'))
    doc.append(Command('newpage'))

    for section_path in section_paths:
        section_name = util.get_last_path_name(section_path)
        section_name = util.get_freq_english(section_name)
        with doc.create(Section(f"Results Organized By {section_name}")):
            subsec_paths = util.browse_dir(section_path, level=1)
            for subsec_path in subsec_paths:
                subsec_name = util.get_last_path_name(subsec_path)
                fnames = util.browse_dir(subsec_path, level=1)
                with doc.create(Subsection(f"{subsec_name} Results")):
                    for fname in fnames:
                        if ".csv" in fname and "summary" in fname and "summary all" not in fname:
                            df = files.read_csv(fname)
                            with doc.create(Table(position='H')) as table:
                                table.add_caption(util.get_last_path_name(fname))
                                table.append(Command('centering'))
                                table.append(Command('tiny'))
                                table.append(NoEscape(df.to_latex(escape=True)))

                        if ".png" in fname:
                            # with doc.create(Subsection('Cute kitten pictures')):
                            with doc.create(Figure(position='H')) as fig:
                                fig.add_image(fname, width=NoEscape('0.9\linewidth'))
                                fig.add_caption(util.get_last_path_name(fname))
    # Creating a pdf
    # pdf with toc 
    # compiler = 'latexmk -f -xelatex -interaction=nonstopmode -output-directory=' + report_dir
    doc.generate_pdf(report_name, clean=True, compiler="latexmk", compiler_args=["-f", "-xelatex"])

    logger.info(f"Report Generated => {report_name}")


def generate_header(doc, title="Insert Title Here", author="Insert Author Here", 
                    company="Insert Company Here", date="Insert Date Here", logo_fpath=None):
    # Add document header
    header = PageStyle("header")
    # Create left header
    with header.create(Head("L")):
        header.append(f"Date of report generation:")
        header.append(LineBreak())
        header.append(f"{date}")

    # Create center header
    with header.create(Head("C")):
        header.append(company)
    # Create right header
    with header.create(Head("R")):
        header.append(simple_page_number())

    doc.preamble.append(header)
    doc.change_document_style("header")

    # Add Heading
    with doc.create(MiniPage(align='c')):
        doc.append(Command('vspace{1.5cm}'))
        doc.append(LargeText(bold(title)))
        doc.append(LineBreak())
        doc.append(Command('vspace{1.5cm}'))
        doc.append(MediumText(bold(f"Author: {author}")))
        
        if logo_fpath is not None:
            doc.append(Command('vspace{2.5cm}'))
            with doc.create(Figure(position='H')) as fig:
                fig.add_image(logo_fpath, width=NoEscape('0.2\linewidth'))

    doc.append(Command('newpage'))
    return doc
