from dataclasses import dataclass
from typing import List
from bs4 import BeautifulSoup

@dataclass
class BracketPage:
    page_index: int
    page_id: int  
    page_name: str
    show_page: bool

@dataclass
class Template:
    template_index: int
    bracket_id: int
    template_id: int
    template_name: str
    bracket_width: int
    bracket_height: int 
    bracket_font: int
    pages: List[BracketPage]

@dataclass
class Weight:
    weight_index: int
    weight_id: str
    weight_name: str
    bracket_id: int

@dataclass
class BracketType:
    bracket_id: int
    default_template_index: int = 0

def parse_bracket_data(html_content: str) -> tuple[List[Weight], List[Template], List[BracketType]]:
    """
    Parse bracket data from the HTML content into structured dataclasses.
    
    Args:
        html_content: Raw HTML string containing bracket data
        
    Returns:
        Tuple of (weights, templates, bracket_types) lists
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the script containing the data
    script_content = None
    for script in soup.find_all('script'):
        if script.string and 'new Pile()' in script.string:
            script_content = script.string
            break
            
    if not script_content:
        raise ValueError("Could not find bracket data in HTML")
    
    def debug_print(data_str: str, label: str):
        """Helper function to print data for debugging"""
        print(f"\n=== {label} ===")
        print(data_str)
        print("=" * 50)
        
    # Parse templates string (it comes first in the script)
    templates_str = script_content.split('str = "')[1].split('";')[0]
    debug_print(templates_str, "Templates String")
    templates = []
    if templates_str:
        entries = templates_str.split('~')
        for i in range(0, len(entries), 7):
            # Parse pages for this template
            pages_data = entries[i+6].split(',')
            pages = []
            for j in range(0, len(pages_data), 2):
                pages.append(BracketPage(
                    page_index=j//2,
                    page_id=int(pages_data[j]),
                    page_name=pages_data[j+1],
                    show_page=(pages_data[j] in ('1', '2', '4', '6'))
                ))
                
            templates.append(Template(
                template_index=len(templates),
                bracket_id=int(entries[i+0]),
                template_id=int(entries[i+1]),
                template_name=entries[i+2],
                bracket_width=entries[i+3],
                bracket_height=entries[i+4],
                bracket_font=entries[i+5],
                pages=pages
            ))

    # Parse weights string 
    weights_str = script_content.split('str = "')[2].split('";')[0]
    debug_print(weights_str, "Weights String")
    weights = []
    if weights_str:
        entries = weights_str.split('~')
        for i in range(0, len(entries), 3):
            weights.append(Weight(
                weight_index=len(weights),
                weight_id=entries[i],
                weight_name=entries[i+1],
                bracket_id=int(entries[i+2])
            ))

    # Parse bracket types string  
    bracket_types_str = script_content.split('str = "')[3].split('";')[0]
    debug_print(bracket_types_str, "Bracket Types String")
    bracket_types = []
    if bracket_types_str:
        for bracket_id in bracket_types_str.split(','):
            bracket_types.append(BracketType(bracket_id=int(bracket_id)))

    # Parse bracket types string  
    bracket_types_str = script_content.split('str = "')[3].split('";')[0]
    bracket_types = []
    if bracket_types_str:
        for bracket_id in bracket_types_str.split(','):
            bracket_types.append(BracketType(bracket_id=int(bracket_id)))

    return weights, templates, bracket_types

def generate_bracket_url(weight: Weight, 
                      template: Template, 
                      tw_session_id: str,
                      base_url: str = "https://www.trackwrestling.com/teamtournaments/") -> str:
    """
    Generate a URL for viewing a specific bracket based on weight and template settings.
    
    Args:
        weight: Weight object containing weight class info
        template: Template object containing bracket layout info
        tw_session_id: TrackWrestling session ID
        base_url: Base URL for the TrackWrestling site
        
    Returns:
        Complete URL for viewing the specified bracket
    """
    # Get timestamp in milliseconds
    from time import time
    current_time_ms = int(time() * 1000)
    
    # Get the pages that are marked as visible
    visible_pages = [p.page_id for p in template.pages if p.show_page]
    pages_str = ",".join(map(str, visible_pages))
    
    # Construct URL parameters
    params = {
        "TIM": current_time_ms,
        "twSessionId": tw_session_id,
        "chartId": weight.weight_id,
        "groupId": weight.weight_id,
        "bracketWidth": template.bracket_width,
        "bracketHeight": template.bracket_height,
        "bracketFontSize": template.bracket_font,
        "includePages": pages_str,
        "templateId": template.template_id if template.template_id != 0 else ""
    }
    
    # Build query string
    query = "&".join(f"{k}={v}" for k, v in params.items() if v != "")
    
    # Combine into final URL
    return f"{base_url}Bracket.jsp?{query}"

def format_bracket_data(weights: List[Weight], 
                       templates: List[Template], 
                       bracket_types: List[BracketType]) -> str:
    """
    Format the parsed bracket data into a readable string representation.
    
    Args:
        weights: List of Weight objects
        templates: List of Template objects 
        bracket_types: List of BracketType objects
        
    Returns:
        Formatted string showing the parsed data structure
    """
    output = []
    
    output.append("=== Weights ===")
    for w in weights:
        output.append(f"Weight {w.weight_index}: {w.weight_name} (ID: {w.weight_id}, Bracket: {w.bracket_id})")
    
    output.append("\n=== Templates ===") 
    for t in templates:
        output.append(f"\nTemplate {t.template_index}: {t.template_name}")
        output.append(f"Bracket ID: {t.bracket_id}, Template ID: {t.template_id}")
        output.append(f"Dimensions: {t.bracket_width}x{t.bracket_height}, Font: {t.bracket_font}")
        output.append("Pages:")
        for p in t.pages:
            output.append(f"  - {p.page_name} (ID: {p.page_id}, Show: {p.show_page})")
            
    output.append("\n=== Bracket Types ===")
    for bt in bracket_types:
        output.append(f"Bracket Type ID: {bt.bracket_id}")
        
    return "\n".join(output)

# Example usage:
if __name__ == "__main__":
    with open("brackets.html", "r") as f:
        html_content = f.read()
        
    weights, templates, bracket_types = parse_bracket_data(html_content)
    print(format_bracket_data(weights, templates, bracket_types))
    
    # Example of generating a URL for the first weight class and template
    if weights and templates:
        # Example using a sample session ID
        url = generate_bracket_url(weights[1], templates[0], tw_session_id="sample_session")
        print("\n=== Example Bracket URL ===")
        print(url)

# TODO: Sometimes it's chartId, other times its groupId. Need to clarify this.