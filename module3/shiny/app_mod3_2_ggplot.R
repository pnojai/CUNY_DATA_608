library(shiny)
library(ggplot2)
library(dplyr)
library(stringr)

####################################################################################
#                                  DATA PREP
####################################################################################
df <- read.csv("mortality.csv") 
names(df) <- str_replace_all(string = names(df), pattern = "\\.", replacement = "_")
cod_labels <- sort(unique(df$ICD_Chapter))
state_labels <- sort(unique(df$State))

# U.S. population by year.
df_pop <- df %>%
    filter(ICD_Chapter == "Neoplasms") %>%
    group_by(Year) %>%
    summarise(pop_tot = sum(Population))

# State population weight.
df_pop_wt <- df %>%
    inner_join(df_pop) %>%
    select(ICD_Chapter, State, Year, Population, pop_tot) %>%
    arrange(State, Year) %>%
    mutate(pop_wt = Population / pop_tot)

# Join mortality and population weight.
df_join_wt <- df %>%
    inner_join(df_pop_wt)

# Add weighted mortality to dataframe
df_join_wt <- df_join_wt %>%
    mutate(mort_weighted = Crude_Rate * pop_wt)

####################################################################################
#                                      APP
####################################################################################

ui <- fluidPage(
    headerPanel("Crude Mortality Rate by Cause of Death in the U.S., 1999 - 2010"),
    sidebarPanel(
        selectInput('cod', 'Cause of Death', cod_labels, selected="Neoplasms"),
        selectInput('state', 'State', state_labels, selected="NY")
    ),
    mainPanel(
        plotOutput("plot1")
    )
)

# Define server logic required to plot.
server <- function(input, output) {
    selected_data_natl <- reactive({
        df_join_wt %>%
            filter(ICD_Chapter == input$cod) %>%
            group_by(Year) %>%
            summarize(natl_mort = sum(mort_weighted)) 
    })
    
    selected_data_state <- reactive({
        df_state_mort <- df_join_wt %>%
            filter(ICD_Chapter == input$cod, State == input$state) 
    })

    output$plot1 <- renderPlot({
        ggplot() + 
            geom_line(data = selected_data_natl(), aes(x = Year, y = natl_mort, color = "National Avg")) +
            geom_line(data = selected_data_state(), aes(x = Year, y = Crude_Rate, color = "State")) +
            scale_colour_manual("", 
                                breaks = c("National Avg", "State"),
                                values = c("National Avg"="black", "State"="red")) +
            theme_bw() +
            labs(x = "Year",
                 y = "Mortality Rate (per 100,000)",
                 caption = "Source: CDC")
        })
}

# Run the application 
shinyApp(ui = ui, server = server)
