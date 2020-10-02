library(shiny)
library(ggplot2)
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
        plotOutput("plot1")
    )
)

# Define server logic required to draw a histogram
server <- function(input, output) {
    selectedData <- reactive({
        df_2010 %>%
            filter(ICD_Chapter == input$cod)
    })
    
    output$plot1 <- renderPlot({
        ggplot(selectedData()) +
            aes(reorder(State, Crude_Rate), Crude_Rate) +
            geom_bar(stat = "identity") +
            coord_flip() +
            theme_bw() +
            labs(# subtitle = paste0("Cause of death: ", input$cod),
                 x = "State",
                 y = "Crude Mortality Rate (per 100,000)",
                 caption = "Source: CDC")
            }, height = 700)
}

# Run the application 
shinyApp(ui = ui, server = server)
