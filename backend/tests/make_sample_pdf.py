"""Regenerates tests/sample_data/sample.pdf (requires reportlab: pip install reportlab)."""
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

PAGES = [
    ["Renewable Energy Overview", "",
     "Solar panels convert sunlight into electricity using photovoltaic cells.",
     "Commercial silicon solar panels typically reach an efficiency between 18 and 22 percent.",
     "Solar power works best in regions with high annual sunshine such as Rajasthan.",
     "Batteries store the extra electricity generated during the day for use at night."],
    ["Wind and Hydropower", "",
     "Wind turbines transform the kinetic energy of moving air into electrical energy.",
     "Offshore wind farms produce more consistent power because sea winds are stronger and steadier.",
     "Hydropower uses flowing water from dams to spin turbines and generate electricity.",
     "Large dams can disrupt river ecosystems and displace local communities."],
]


def build(out: Path) -> None:
    c = canvas.Canvas(str(out), pagesize=A4)
    for lines in PAGES:
        y = 780
        for line in lines:
            c.setFont("Helvetica-Bold" if y == 780 else "Helvetica", 14 if y == 780 else 11)
            c.drawString(50, y, line)
            y -= 24
        c.showPage()
    c.save()


if __name__ == "__main__":
    build(Path(__file__).parent / "sample_data" / "sample.pdf")
