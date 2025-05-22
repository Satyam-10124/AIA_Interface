# crew.py
import os
import json
import logging
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError, validator
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import yaml
 
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, ScrapeWebsiteTool,CodeInterpreterTool
from langchain_community.embeddings import AzureOpenAIEmbeddings
# Load environment variables securely
load_dotenv()
 
llm = LLM(
    model="gemini/gemini-2.0-flash",
    api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.7,
    streaming=True
)
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# ======================
# DATA MODELS
# ======================
class DynamicInsights(BaseModel):
    """Extracted insights, statistics, and visualization suggestions from the dataset."""

    no_of_pages: int = Field(..., description="Number of pages for the document.")
    
    key_insights: List[str] = Field(
        ..., 
        description="Key insights extracted strictly from the description. These should be concise and actionable. Try to explain them in 3 or 5 or 7 points based on the number of insights"
    )
    
    # Optional dictionary for statistics, can hold a variety of statistical data
    statistics: Optional[Dict[str, Any]] = Field(
        default_factory=dict, 
        description="Statistical summaries derived directly from the dataset. This could include mean, median, standard deviation, etc."
    )
    
    visual_cues: Optional[List[str]] = Field(
        default_factory=list, 
        description="Visualization suggestions based solely on the dataset. Examples include 'bar chart for distribution' or 'line plot for trends'."
    )
 
 
class SlideContent(BaseModel):
    """Structured content for each slide."""
    title: str = Field(..., min_length=5, description="Slide title.")
    content: List[str] = Field(
        ...,
        min_items=3,
        description="List of bullet points, derived only from the dataset."
    )
 
class VisualizationSpec(BaseModel):
    """Visualization details for each slide."""
    visualization_type: str = Field(
        ...,
        pattern="^(bar|line|pie|scatter|table)$",
        description="Type of visualization."
    )
    data_columns: List[str] = Field(
        ...,
        description="Columns to visualize, based only on the provided dataset."
    )
    customization: Dict[str, Any] = Field(
        default_factory=lambda: {
            "colors": ["#2E86C1", "#138D75"],
            "dimensions": {"width": 10, "height": 6}
        },
        description="Customization for the visualization."
    )
 
class FinalPageReport(BaseModel):
    """Final report structure."""
    title: str = Field(..., min_length=5, description="Report title.")
    introduction: str = Field(..., min_length=10, description="Introduction to the report.")
    content: List[SlideContent] = Field(
        ...,
        min_items=3,
        description="List of slide content, derived strictly from the dataset."
    )
    visualizations: List[VisualizationSpec] = Field(
        ...,
        min_items=1,
        description="List of visualizations, based solely on the dataset."
    )
 
class FinalOutput(BaseModel):
    """Final output structure."""
    total_pages : int = Field(..., description="Total number of pages in the report.")
    report_per_page : List[FinalPageReport] = Field(
        ...,
        min_items=1,
        description="List of final report pages, derived strictly from the dataset."
    )
 
class GeneratedCode(BaseModel):
    """Generated Python code for creating a Word document."""
    code: str = Field(..., description="Generated Python code for creating a Word document.")


def generate_html_report(slide_content):
    """
    Converts slide content data into a structured, interactive HTML report.
    """
    html_template = f"""
    <html>
    <head>
        <title>AI-Generated Report</title>
        <script src='https://cdn.jsdelivr.net/npm/chart.js'></script>
        <link rel='stylesheet' href='https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.19/tailwind.min.css'>
    </head>
    <body class='p-8'>
        <h1 class='text-3xl font-bold text-center mb-6'>AI-Generated Data Analysis Report</h1>
        <div class='container mx-auto'>
            {slide_content}  <!-- Inject generated content dynamically -->
        </div>
    </body>
    </html>
    """
    
    with open("generated_report.html", "w", encoding="utf-8") as file:
        file.write(html_template)
    
    return "generated_report.html"
 
data_agent = Agent(
    role="Business Data Analyst",
    goal="Analyze business datasets strictly based on the provided description - {description}. Extract actionable insights, key metrics, and strategic recommendations while ensuring objectivity. Avoid assumptions or external knowledge, and present findings in a structured, logical, and decision-oriented manner.",
    backstory=(
        "A seasoned business intelligence analyst with expertise in financial, operational, and market data analysis. "
        "With a strong background in statistical modeling, machine learning, and financial forecasting, this agent specializes in uncovering meaningful trends, KPIs, and growth opportunities. "
        "It ensures that all analysis remains strictly data-driven, offering businesses clarity and actionable insights for strategic planning, investment decisions, and operational improvements."
    ),
    personality=(
        "Strategic, analytical, and precision-focused. Communicates insights in an executive-friendly format, "
        "tailoring reports for C-level executives, analysts, and business managers. Avoids speculation and ensures all recommendations are evidence-backed."
    ),
    expertise=[
        "Financial & operational data analysis",
        "Market trend forecasting & competitive analysis",
        "KPI tracking & business performance evaluation",
        "Revenue & cost optimization insights",
        "Customer segmentation & behavior analytics",
        "Predictive modeling for business growth"
    ],
    capabilities=[
        "Extracting financial insights from business reports",
        "Identifying growth opportunities and market trends",
        "Tracking business KPIs and performance benchmarks",
        "Using predictive analytics for revenue forecasting",
        "Generating executive-level reports and dashboards",
        "Ensuring structured, data-driven decision-making"
    ],
    llm=llm,
    verbose=True
)
 
content_agent = Agent(
    role="AI-Powered Presentation Architect",
    goal="Convert complex data insights into structured, engaging, and visually compelling slide content. Generate precise visualization specifications for {num_pages} slides based on {description}, ensuring alignment with {purpose}. Maintain clarity, coherence, and impact while optimizing visual storytelling to maximize audience engagement.",
    backstory="A highly skilled AI agent specializing in data-driven storytelling, transforming raw analysis into structured, compelling presentations. With expertise in audience psychology, narrative structuring, and visual communication, this agent crafts content that not only informs but also persuades and engages. It ensures every slide is optimized for clarity, strategic impact, and effective decision-making while maintaining professional aesthetics.",
    personality="Analytical, adaptable, and insight-driven. It tailors slide content, tone, and structure based on the target audience—whether executives, analysts, or general staff—ensuring relevance, engagement, and strategic alignment. Focused on precision and clarity, it seamlessly integrates data with visual storytelling for maximum effectiveness.",
    expertise=[
        "Data-driven storytelling",
        "Slide content structuring & information hierarchy",
        "Business communication & executive-level presentations",
        "Infographic & data visualization optimization",
        "Strategic messaging for decision-making",
        "Engagement-driven presentation design"
    ],
    capabilities=[
        "Transforming complex data into concise, audience-friendly slides",
        "Generating structured narratives aligned with business goals",
        "Creating visualization specifications for charts, graphs, and infographics",
        "Optimizing slide flow for clarity, impact, and professional appeal"
    ],
    llm=llm,
    verbose=True
)
 
viz_agent = Agent(
    role="Business Data Visualization Expert",
    goal="Design precise, business-driven visualizations that translate complex data into clear, insightful graphics. Ensure accuracy, clarity, and strategic impact while maintaining alignment with business objectives and KPIs.",
    backstory="A seasoned expert in business data visualization, specializing in transforming financial, operational, and strategic datasets into compelling visuals. With a deep understanding of corporate reporting, KPI tracking, and executive dashboards, this agent ensures that each visualization enhances decision-making without introducing unnecessary complexity. It balances analytical depth with visual clarity, ensuring insights are immediately actionable.",
    personality="Insightful, strategic, and precision-focused. Adapts visualization styles based on the business audience—whether executives, financial analysts, or operational teams—ensuring relevance and maximum impact.",
    expertise=[
        "Financial & operational data visualization",
        "Executive-level dashboard creation",
        "Performance metrics & KPI tracking",
        "Market trends & forecasting visuals",
        "Comparative & benchmarking analytics",
        "Optimizing visual hierarchy for decision-making"
    ],
    capabilities=[
        "Translating business data into clear, compelling visuals",
        "Selecting optimal charts for KPIs, trends, and comparisons",
        "Enhancing engagement through strategic, data-driven visuals",
        "Ensuring consistency, accessibility, and precision in business reporting"
    ],
    llm=llm,
    verbose=True
)
 
 
 
coding_agent = Agent(
    role="Business Intelligence Report Generator & Data Visualization Specialist",
    llm=llm,
    goal="Craft interactive, corporate-grade HTML reports that translate complex business data into visually compelling, data-driven insights.",
    backstory=(
        "An expert in executive-level business intelligence reporting, specializing in transforming structured data into polished, "
        "interactive HTML reports. Adept at blending corporate branding, advanced data visualization, and intuitive UI design, "
        "the agent ensures that stakeholders receive clear, actionable insights presented in a professional format.\n\n"
        "Excels in leveraging JavaScript-based visualization libraries, adaptive UI theming, and smooth animations to create engaging, "
        "interactive reports. Thrives on precision, innovation, and clarity, ensuring that every report meets the highest standards "
        "of readability, aesthetics, and interactivity."
    ),
    personality=(
        "Analytical, detail-oriented, and highly creative. Passionate about building **executive-friendly dashboards** that blend "
        "data storytelling with interactive business intelligence tools. Ensures reports are visually engaging, data-rich, and "
        "aligned with corporate branding.\n\n"
        "Has an eye for **adaptive theming**, dynamically extracting company logo colors to enhance branding consistency. "
        "Loves integrating sleek UI/UX principles, animations, and modern charting techniques to deliver high-impact business reports."
    ),
    capabilities=[
        "Generate **executive-level HTML reports** with structured business intelligence components",
        "Design **corporate-grade UI/UX** for professional, polished reports",
        "Dynamically extract **company branding colors** to ensure consistency",
        "Implement **interactive dashboards** with D3.js, Highcharts, and ApexCharts",
        "Craft **data-driven storytelling** with AI-generated key takeaways",
        "Enable **smooth animations and transitions** for an engaging experience",
        "Provide **downloadable PDF, Excel reports, and print-friendly formats**",
        "Optimize **accessibility, responsiveness, and performance** for all business use cases",
        "Enhance visualization using **GSAP, CSS animations, and advanced UI theming**",
        "Search for additional visualization libraries using SerperDevTool to enhance impact",
    ],
    verbose=True,
    allow_code_execution=True,
    tools=[CodeInterpreterTool(), SerperDevTool()],
)
 
 
# ======================
# TASK CONFIGURATION
# ======================
data_task = Task(
    name="Business Data Analysis",
    description=(
        "Perform a structured analysis of the provided business dataset, extracting key insights, financial trends, and operational metrics. "
        "Ensure that findings are decision-oriented, data-driven, and formatted for strategic business use. "
        "Provide a breakdown of relevant statistics, KPIs, and actionable recommendations, alongside visualization suggestions for effective communication."
    ),
    expected_output=(
        "1. Extracted key insights from the dataset.\n"
        "2. Financial and operational statistics relevant to business decision-making.\n"
        "3. Market trends, correlations, and growth opportunities.\n"
        "4. Recommended KPIs and performance benchmarks.\n"
        "5. Data visualization specifications to enhance reporting clarity."
    ),
    agent=data_agent,
    tools=[SerperDevTool()],  # Ensuring access to real-time search insights if required.
    output_pydantic=DynamicInsights,  # Structured output formatting for consistency.
    verbose=True,
    # human_input=True  # Uncomment if manual validation is required at any stage.
)
content_task = Task(
    name="Business Slide Content Creation",
    description=(
        "Generate structured and engaging slide content based strictly on the extracted insights, statistics, and dataset analysis. "
        "Ensure the content aligns with the user's purpose: {purpose}, while maintaining clarity, coherence, and impactful storytelling for {num_pages} slides.\n\n"
        
        "### Task Execution Steps:\n"
        "1. **Extract and validate** insights, statistics, and relevant findings from the dataset.\n"
        "2. **Dynamically fetch company branding colors** using SerperDevTool to maintain consistency in slide design.\n"
        "3. **Structure slide content** that is concise, clear, and engaging for the intended audience.\n"
        "4. **Ensure alignment with business objectives**, maintaining a logical narrative flow.\n"
        "5. **Define precise visualization specifications** for each slide based on the dataset.\n"
        "6. Iterate through all {num_pages} slides to ensure consistency and completeness.\n\n"
        
        "**Branding & Visual Appeal:**\n"
        "- Extract **company logo colors** using **SerperDevTool**.\n"
        "- Apply these colors to slide headers, charts, and key elements for **branding consistency**.\n"
        "- Ensure contrast and readability by intelligently adjusting color schemes.\n\n"
        
        "The content should be **data-driven**, strictly derived from insights, and presented in a format that enhances decision-making."
    ),
    expected_output=(
        "1. **Fully structured** and audience-friendly slide content.\n"
        "2. **Key insights and statistics** presented concisely.\n"
        "3. **Logical slide flow** with clear takeaways.\n"
        "4. **Branded color scheme** dynamically applied from the company's logo.\n"
        "5. **Recommended visualization specifications** to enhance clarity and engagement."
    ),
    agent=content_agent,
    context=[data_task],  # Ensuring seamless integration with the dataset analysis task.
    tools=[SerperDevTool()],  # Fetch branding colors dynamically
    verbose=True,
    output_pydantic=FinalOutput
) 
 
# quality_assurance_task = Task(
#     name="Quality Assurance",
#     description="Ensure the quality of the generated content and visualizations.",
#     expected_output="Quality assurance report.",
#     agent=data_agent,
#     context=[content_task],
#     output_pydantic=FinalOutput
# )
# ======================
 
coding_task = Task(
    name="Business-Grade Data Visualization Report Generator 📊",
    description=(
        "Generate an **executive-level, interactive, and visually stunning HTML report** "
        "that translates complex data insights into **clear, actionable business intelligence**.\n\n"
        
        "**📌 Features:**\n"
        "- **Corporate-grade UI** with professional design principles.\n"
        "- **Company branding integration**: Extract logo colors and apply them dynamically.\n"
        "- **Real-time interactive charts** powered by **D3.js, Highcharts, and ApexCharts**.\n"
        "- **Executive summary**: Auto-generated insights tailored for business leaders.\n"
        "- **Data-driven storytelling**: Uses AI to highlight key takeaways.\n"
        "- **Downloadable PDFs, Excel reports, and Print-friendly version** for boardroom discussions.\n"
        "- **Smooth transitions & animations** for an engaging user experience.\n\n"
        
        "**📊 Visualization Suite (Intelligently Selected)**\n"
        "✅ **D3.js** - Custom, highly interactive, business intelligence charts.\n"
        "✅ **Highcharts** - Best for financial, sales, and enterprise reports.\n"
        "✅ **ApexCharts** - Animated, modern, and sleek data visualizations.\n"
        "✅ **Chart.js** - Simple yet effective business graphs.\n"
        "✅ **Nivo & amCharts** - Perfect for structured KPI tracking & reports.\n\n"
        
        "**🎨 Intelligent UI Theming:**\n"
        "- **Dynamically fetches the company logo colors** via **SerperDevTool**.\n"
        "- Applies branding colors to **charts, sections, and navigation elements**.\n"
        "- Ensures readability with **adaptive contrast & font styling**.\n\n"
        
        "**📑 Deliverables:**\n"
        "- **An HTML & JS-powered interactive business report**.\n"
        "- **Executive summary & key insights** automatically extracted.\n"
        "- **Seamless integration with PowerPoint for presentations**.\n"
        "- **Downloadable Excel & PDF reports for stakeholder sharing**.\n"
    ),   
    expected_output=(
        "A **polished, investor-ready business report** with:\n"
        "- **Interactive dashboards & charts** (D3.js, Highcharts, etc.)\n"
        "- **Company branding & professional UI**\n"
        "- **Executive summary with auto-generated insights**\n"
        "- **Downloadable PDF, Excel, and print-ready version**\n"
    ),
    agent=coding_agent,
    tools=[CodeInterpreterTool(), SerperDevTool()],  # Fetch logo colors for theming
    context=[data_task,content_task],  # Providing structured slide content for visualization
    output_file="./UI_Results/2Business_Visualization_Report.html",  # Final polished report
)

# ======================
# CREW CONFIGURATION
# ======================
crew = Crew(
    agents=[data_agent, content_agent,coding_agent],
    tasks=[data_task, content_task, coding_task],
    process=Process.sequential,
    verbose=True,
)
 
# ======================
# EXECUTION PIPELINE
# ======================
class DynamicReportGenerator:
    def __init__(self, config):
        self.config = config
        self.crew = crew
 
 
    def execute(self):
        """Run the dynamic report generation pipeline."""
        # self.validate_input()
        try:
            result = self.crew.kickoff(inputs=self.config)
            print("\n✅ Report generated successfully!")
            return result
        except Exception as e:
            print("\n❌ Error during report generation:")
            print(str(e))
            return None
 
# ======================
# MAIN EXECUTION
# ======================
if __name__ == "__main__":
    config = {
        "purpose": "Dynamic dataset analysis",
        "num_pages": 5,
        "description": '''
               
        '''  # Provide your dataset file here
    }
 
    generator = DynamicReportGenerator(config)
    output = generator.execute()
 
    if output:
        print("\n🔍 Insights:")
        print(output)
    else:
        print("\n🚫 Report generation failed.") 