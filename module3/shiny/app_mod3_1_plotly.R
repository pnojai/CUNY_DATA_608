library(shiny)
library(plotly)
library(dplyr)
library(stringr)

df <- read.csv("mortality.csv") 
names(df) <- str_replace_all(string = names(df), pattern = "\\.", replacement = "_")

df_2010 <- df %>%
    filter(Year == 2010)
cod_labels <- sort(unique(df_2010$ICD_Chapter))

ui <- fluidPage(
    headerPanel("Crude Mortality Rate in the U.S. in 2010"),
    sidebarPanel(
        selectInput('cod', 'Cause of Death', cod_labels, selected="Neoplasms")
    ),
    mainPanel(
        plotlyOutput("plot1", height = "1000px")
    )
)

# Define server logic required to draw a histogram
server <- function(input, output) {
    selectedData <- reactive({
        df_2010 %>%
            filter(ICD_Chapter == input$cod)
    })
    
    output$plot1 <- renderPlotly({
        fig <- plot_ly(data = selectedData(), x = ~Crude_Rate, y = ~State,
                       type = "bar", orientation = "h") %>%
            layout(
                title = "",
                xaxis = list(title = "Crude Mortality Rate (per 100,000)"),
                yaxis = list(title = "State",
                             categoryorder = "total ascending")
                )
        fig
    })
}

# Run the application 
shinyApp(ui = ui, server = server)
