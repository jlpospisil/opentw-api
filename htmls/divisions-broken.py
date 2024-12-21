from dataclasses import dataclass
from typing import List, Optional
import re

@dataclass
class BracketPage:
    """Represents a page within a bracket template"""
    page_index: int
    page_id: int
    page_name: str
    show_page: bool = True

@dataclass
class Template:
    """Represents a bracket template configuration"""
    template_index: int
    bracket_id: int
    template_id: int
    template_name: str
    bracket_width: str
    bracket_height: str
    bracket_font: str
    pages: List[BracketPage]

@dataclass
class Chart:
    """Represents a bracket/division chart"""
    chart_index: int
    chart_id: str
    chart_name: str
    bracket_id: int

@dataclass
class BracketType:
    """Represents a type of bracket"""
    bracket_id: int
    default_template_index: int = 0

def extract_bracket_data(html_content: str) -> tuple[List[Chart], List[Template], List[BracketType]]:
    """
    Extract bracket data from the HTML content
    Returns tuple of (charts, templates, bracket_types)
    """
    # Find and parse the charts data
    charts_pattern = r'str = "([\d~A-Za-z\s,]+)";[\s\n]*ndx = 0;[\s\n]*if\(str!=null\){'
    charts_match = re.search(charts_pattern, html_content)
    charts = []
    if charts_match:
        charts_data = charts_match.group(1)
        chart_entries = charts_data.split("~")
        for i in range(0, len(chart_entries), 3):
            if i + 2 < len(chart_entries):
                chart = Chart(
                    chart_index=len(charts),
                    chart_id=chart_entries[i],
                    chart_name=chart_entries[i+1],
                    bracket_id=int(chart_entries[i+2])
                )
                charts.append(chart)

    # Find and parse the templates data
    templates_pattern = r'str = "([\d~A-Za-z\s,]+)";[\s\n]*var ndx = 0;'
    templates_match = re.search(templates_pattern, html_content)
    templates = []
    if templates_match:
        templates_data = templates_match.group(1)
        template_entries = templates_data.split("~")
        for i in range(0, len(template_entries), 7):
            if i + 6 < len(template_entries):
                # Parse pages data
                pages_data = template_entries[i+6].split(",")
                pages = []
                for j in range(0, len(pages_data), 2):
                    if j + 1 < len(pages_data):
                        page = BracketPage(
                            page_index=j//2,
                            page_id=int(pages_data[j]),
                            page_name=pages_data[j+1]
                        )
                        pages.append(page)
                
                template = Template(
                    template_index=len(templates),
                    bracket_id=int(template_entries[i+0]),
                    template_id=int(template_entries[i+1]),
                    template_name=template_entries[i+2],
                    bracket_width=template_entries[i+3],
                    bracket_height=template_entries[i+4],
                    bracket_font=template_entries[i+5],
                    pages=pages
                )
                templates.append(template)

    # Find and parse bracket types
    bracket_types_pattern = r'str = "([\d,]+)";[\s\n]*if\(str!=null\)'
    bracket_types_match = re.search(bracket_types_pattern, html_content)
    bracket_types = []
    if bracket_types_match:
        bracket_types_data = bracket_types_match.group(1)
        for bracket_id in bracket_types_data.split(","):
            bracket_type = BracketType(bracket_id=int(bracket_id))
            bracket_types.append(bracket_type)

    return charts, templates, bracket_types

def print_frame(chart_id: str, bracket_width: str, bracket_height: str, 
                bracket_font: str, include_pages: str, template_id: Optional[str] = None) -> str:
    """
    Generate the URL for viewing a bracket frame
    """
    base_url = "Bracket.jsp?TIM=1734317027351&twSessionId=biqfdgkwwl"
    params = {
        "chartId": chart_id,
        "bracketWidth": bracket_width,
        "bracketHeight": bracket_height,
        "bracketFontSize": bracket_font,
        "includePages": include_pages,
        "templateId": template_id if template_id else ""
    }
    
    url = base_url + "".join(f"&{key}={value}" for key, value in params.items())
    return url

def analyze_bracket_structure(html_content: str) -> None:
    """
    Analyze and print out the bracket structure from the HTML
    """
    charts, templates, bracket_types = extract_bracket_data(html_content)
    
    print("\nBracket Structure Analysis:")
    print("-" * 50)
    
    print("\nCharts/Divisions:")
    for chart in charts:
        print(f"  • {chart.chart_name} (ID: {chart.chart_id}, Bracket Type: {chart.bracket_id})")
        
        # Find matching templates for this chart
        matching_templates = [t for t in templates if t.bracket_id == chart.bracket_id]
        if matching_templates:
            print("    Available Templates:")
            for template in matching_templates:
                print(f"      - {template.template_name}")
                print(f"        Pages: {', '.join(p.page_name for p in template.pages)}")
    
    print("\nBracket Types:")
    for btype in bracket_types:
        print(f"  • Bracket Type ID: {btype.bracket_id}")
        
    # Example URL generation
    if charts and templates:
        example_chart = charts[0]
        example_template = next((t for t in templates if t.bracket_id == example_chart.bracket_id), None)
        if example_template:
            example_url = print_frame(
                chart_id=example_chart.chart_id,
                bracket_width=example_template.bracket_width,
                bracket_height=example_template.bracket_height,
                bracket_font=example_template.bracket_font,
                include_pages=",".join(str(p.page_id) for p in example_template.pages),
                template_id=str(example_template.template_id)
            )
            print("\nExample Frame URL:")
            print(example_url)

# Example usage
if __name__ == "__main__":
    with open("bracket_page.html", "r") as f:
        html_content = f.read()
    analyze_bracket_structure(html_content)